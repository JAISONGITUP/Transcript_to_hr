import spacy
import re
from typing import Dict, Optional, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model
_nlp = None

# Compile regex patterns once for better performance
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
YEAR_PATTERN = re.compile(r'\b(19\d{2}|20\d{2})\b')
RECENT_YEAR_PATTERN = re.compile(r'\b(20[0-3]\d)\b')

EXPERIENCE_PATTERNS = [
    re.compile(r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience', re.IGNORECASE),
    re.compile(r'experience\s*(?:of\s*)?(\d+)\s*(?:years?|yrs?)', re.IGNORECASE),
    re.compile(r'(\d+)\s*(?:years?|yrs?)\s*(?:in|working)', re.IGNORECASE),
]

# Common Indian cities (compiled pattern for performance)
CITY_PATTERN = re.compile(
    r'\b(chennai|mumbai|delhi|bangalore|hyderabad|pune|kolkata|ahmedabad|jaipur|surat|'
    r'lucknow|kanpur|nagpur|indore|thane|bhopal|visakhapatnam|patna|vadodara|ghaziabad|'
    r'ludhiana|agra|nashik|faridabad|meerut|rajkot|varanasi|srinagar|amritsar|jodhpur|'
    r'raipur|allahabad|coimbatore|jabalpur|gwalior|vijayawada|madurai|kota|guwahati|'
    r'chandigarh|solapur|hubli|bareilly|moradabad|gurgaon|aligarh|jalandhar|tiruchirappalli|'
    r'bhubaneswar|salem|warangal|thiruvananthapuram|bhiwandi|saharanpur|gorakhpur|guntur|'
    r'bikaner|amravati|noida|bhavnagar|dehradun|kolhapur|ajmer|gulbarga|jamnagar|udaipur|'
    r'maheshtala|tirunelveli|davanagere|kozhikode|akola|kurnool|rajahmundry|ballari|agartala|'
    r'bhagalpur|latur|dhule|korba|bhimavaram|panvel|bhatpara|machilipatnam|raichur|puducherry|'
    r'pali|tumkur|bharatpur|ichalkaranji|parbhani|hapur|sirsa|baripada|budaun|jagdalpur|'
    r'motihari|rourkela|baghpat|adoni|ujjain|sangli|lahar|ratlam|dharmavaram|kashipur|'
    r'sujangarh|masaurhi|wadi)\b', re.IGNORECASE
)

# Excluded terms for location (set for O(1) lookup)
EXCLUDED_LOCATION_TERMS = {
    'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'sql', 'mongodb',
    'postgresql', 'mysql', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux',
    'html', 'css', 'typescript', 'c++', 'c#', '.net', 'spring', 'django', 'flask',
    'fastapi', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'machine learning', 'ai',
    'data science', 'api', 'rest', 'graphql', 'json', 'xml', 'http', 'https',
    'india', 'south india', 'north india', 'east india', 'west india', 'usa', 'uk',
    'united states', 'us', 'programming', 'code', 'software', 'developer'
}

# Skills keywords (set for faster lookup)
SKILLS_KEYWORDS = {
    'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'sql', 'mongodb',
    'postgresql', 'mysql', 'aws', 'azure', 'docker', 'kubernetes', 'git', 'linux',
    'html', 'css', 'typescript', 'c++', 'c#', '.net', 'spring', 'django', 'flask',
    'fastapi', 'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch',
    'pandas', 'numpy', 'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'jenkins',
    'terraform', 'ansible', 'prometheus', 'grafana', 'splunk', 'tableau', 'powerbi'
}

# Specializations for degree extraction (ordered by specificity - longer/more specific first)
SPECIALIZATIONS = [
    'computer science engineering', 'computer science and engineering', 'cse',
    'computer science', 'computer engineering', 
    'information technology', 'information technology engineering',
    'mechanical engineering', 'civil engineering', 'electrical engineering', 'electronics engineering',
    'chemical engineering', 'aerospace engineering', 'biotechnology', 'biomedical engineering',
    'data science', 'artificial intelligence', 'machine learning', 'software engineering',
    'business administration', 'management', 'finance', 'marketing', 'accounting',
    'mathematics', 'physics', 'chemistry', 'biology', 'statistics', 'economics',
    'it'  # Keep IT last as it's less specific
]

GRADUATION_KEYWORDS = {'graduate', 'graduation', 'completed', 'finished', 'degree', 'graduated', 'pass out', 'passout', 'studied'}
DEGREE_KEYWORDS = {'degree', 'graduated', 'completed', 'studied', 'education', 'qualification', 'bachelor', 'master'}

def load_nlp_model():
    """Lazy load spaCy model with fallback for compatibility issues"""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Falling back to regex-only extraction. "
                "To enable full NLP: python -m spacy download en_core_web_sm"
            )
            _nlp = False  # Mark as unavailable
        except Exception as e:
            # Handle pydantic compatibility issues (e.g., Python 3.14 with Pydantic V1)
            logger.warning(
                f"spaCy model loading failed ({type(e).__name__}): {str(e)}. "
                "Falling back to regex-only extraction. "
                "This may be due to Python 3.14 incompatibility with Pydantic V1."
            )
            _nlp = False  # Mark as unavailable
    return _nlp if _nlp is not False else None

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(EMAIL_PATTERN.match(email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove common separators and check length
    digits = re.sub(r'[^\d+]', '', phone)
    return 10 <= len(digits) <= 15

def validate_year(year: int) -> bool:
    """Validate graduation year is reasonable"""
    return 1950 <= year <= 2030

def extract_email(transcript: str) -> Optional[str]:
    """Extract and validate email"""
    emails = EMAIL_PATTERN.findall(transcript)
    for email in emails:
        if validate_email(email):
            return email.lower().strip()
    return None

def extract_phone(transcript: str) -> Optional[str]:
    """Extract and validate phone number"""
    phone_match = PHONE_PATTERN.search(transcript)
    if phone_match:
        phone = phone_match.group(0).strip()
        if validate_phone(phone):
            return phone
    return None

def extract_experience(transcript: str) -> Optional[str]:
    """Extract experience with validation"""
    for pattern in EXPERIENCE_PATTERNS:
        match = pattern.search(transcript)
        if match:
            years = int(match.group(1))
            if 0 < years <= 50:  # Reasonable range
                return f"{years} years"
    return None

def extract_skills(transcript: str) -> Optional[str]:
    """Extract skills efficiently using set lookup"""
    transcript_lower = transcript.lower()
    found_skills = []
    
    # Use set intersection for faster lookup
    found = SKILLS_KEYWORDS.intersection(set(transcript_lower.split()))
    
    # Also check for multi-word skills
    for skill in SKILLS_KEYWORDS:
        if ' ' in skill and skill in transcript_lower:
            found_skills.append(skill.title())
    
    # Add single-word skills
    found_skills.extend([s.title() for s in found])
    
    # Remove duplicates and sort
    unique_skills = sorted(set(found_skills))
    return ", ".join(unique_skills) if unique_skills else None

def extract_location(transcript: str, doc=None) -> Optional[str]:
    """Extract location with improved accuracy"""
    # First try city pattern (fastest and most accurate)
    city_match = CITY_PATTERN.search(transcript)
    if city_match:
        city = city_match.group(1).title()
        logger.info(f"Location extracted via regex: {city}")
        return city
    
    # Fallback to NLP but with strict filtering (only if doc available)
    if doc is not None:
        locations = [ent.text.strip() for ent in doc.ents if ent.label_ == "GPE"]
        
        # Filter out excluded terms and validate
        valid_locations = []
        for loc in locations:
            loc_lower = loc.lower()
            if (loc_lower not in EXCLUDED_LOCATION_TERMS and 
                len(loc) > 2 and  # Minimum length
                not loc.isdigit() and  # Not a number
                not any(char.isdigit() for char in loc)):  # No digits in location
                valid_locations.append(loc)
        
        if valid_locations:
            # Prefer longer location names (more specific)
            location = max(valid_locations, key=len)
            logger.info(f"Location extracted via NLP: {location}")
            return location
    
    return None

def extract_graduation_year(transcript: str, doc=None) -> Optional[int]:
    """Extract graduation year with context awareness"""
    # Search in sentences with graduation context first (only if doc available)
    if doc is not None:
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in GRADUATION_KEYWORDS):
                year_match = YEAR_PATTERN.search(sent.text)
                if year_match:
                    year = int(year_match.group(1))
                    if validate_year(year):
                        logger.info(f"Graduation year extracted: {year}")
                        return year
    
    # Fallback: look for recent years (2000-2030)
    recent_years = RECENT_YEAR_PATTERN.findall(transcript)
    if recent_years:
        years = [int(y) for y in recent_years if validate_year(int(y))]
        if years:
            # Take the most recent year
            year = max(years)
            logger.info(f"Graduation year extracted (fallback): {year}")
            return year
    
    return None

def extract_college(transcript: str, doc=None) -> Optional[str]:
    """Extract college/university with validation"""
    # Common prefixes to remove
    prefixes_to_remove = [
        r'\bI graduated from\s+',
        r'\bgraduated from\s+',
        r'\bI studied at\s+',
        r'\bstudied at\s+',
        r'\bI am from\s+',
        r'\bfrom\s+',
        r'\bat\s+'
    ]
    
    if doc is None:
        # Regex-only fallback: look for college/university keywords
        college_pattern = re.compile(r'\b([A-Z][a-zA-Z\s]+(?:University|College|Institute|School|Academy))\b')
        match = college_pattern.search(transcript)
        if match:
            college = match.group(1).strip()
            # Remove common prefixes
            for prefix_pattern in prefixes_to_remove:
                college = re.sub(prefix_pattern, '', college, flags=re.IGNORECASE).strip()
            if 5 <= len(college) <= 100:
                logger.info(f"College extracted via regex: {college}")
                return college
        return None
    
    orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
    college_keywords = {'university', 'college', 'institute', 'school', 'academy'}
    
    for org in orgs:
        org_lower = org.lower()
        # Check if it contains college keywords
        if any(keyword in org_lower for keyword in college_keywords):
            # Validate: should be reasonable length and not a common word
            if 5 <= len(org) <= 100 and org_lower not in {'university', 'college', 'school'}:
                # Clean up the college name by removing prefixes
                cleaned_org = org
                for prefix_pattern in prefixes_to_remove:
                    cleaned_org = re.sub(prefix_pattern, '', cleaned_org, flags=re.IGNORECASE).strip()
                logger.info(f"College extracted: {cleaned_org}")
                return cleaned_org
    
    return None

def extract_degree(transcript: str, doc=None) -> Optional[str]:
    """Extract degree with improved accuracy - captures specializations even when mentioned separately"""
    transcript_lower = transcript.lower()
    
    # Pattern 1: "degree in [specialization]" format (most common in interviews)
    # Match "degree in computer science engineering" or similar
    degree_in_pattern = re.compile(r'\bdegree\s+in\s+([a-z\s]+(?:engineering|science|technology|administration))', re.IGNORECASE)
    degree_in_match = degree_in_pattern.search(transcript)
    if degree_in_match:
        spec_mentioned = degree_in_match.group(1).strip().lower()
        # Check if it matches any of our specializations (prioritize longer/more specific ones)
        sorted_specs = sorted(SPECIALIZATIONS, key=len, reverse=True)
        for spec in sorted_specs:
            # Check if specialization is in the mentioned text or vice versa
            if spec in spec_mentioned or spec_mentioned in spec:
                # Search in wider context (entire transcript) for degree level indicators
                transcript_lower_full = transcript.lower()
                
                # Look for master's degree indicators in the entire transcript
                master_indicators = ['master', 'm.tech', 'mtech', 'm.e', 'm e', 'm.e.', 'postgraduate', 'pg', 'masters']
                bachelor_indicators = ['bachelor', 'b.tech', 'btech', 'b.e', 'b e', 'b.e.', 'undergraduate', 'ug', 'bachelors']
                
                # Check if any master indicator appears before the degree mention
                degree_pos = degree_in_match.start()
                context_before = transcript_lower_full[:degree_pos]
                context_after = transcript_lower_full[degree_pos:degree_pos+200]
                
                has_master = any(indicator in context_before or indicator in context_after for indicator in master_indicators)
                has_bachelor = any(indicator in context_before or indicator in context_after for indicator in bachelor_indicators)
                
                if has_master and not has_bachelor:
                    result = f"M.Tech in {spec.title()}"
                elif has_bachelor and not has_master:
                    # Check specific bachelor type
                    if any(ind in context_before or ind in context_after for ind in ['b.e', 'b e', 'b.e.']):
                        result = f"B.E. in {spec.title()}"
                    elif any(ind in context_before or ind in context_after for ind in ['b.tech', 'btech', 'b.tech.']):
                        result = f"B.Tech in {spec.title()}"
                    elif any(ind in context_before or ind in context_after for ind in ['bachelor', 'bachelors']):
                         result = f"Bachelor's in {spec.title()}"
                    else:
                        # Default for generic "undergraduate" etc - just return specialization
                        result = spec.title()
                elif has_master and has_bachelor:
                    # If both found, check which is closer to the degree mention
                    master_positions = [context_before.rfind(ind) for ind in master_indicators if ind in context_before]
                    master_positions.extend([degree_pos + context_after.find(ind) for ind in master_indicators if ind in context_after])
                    bachelor_positions = [context_before.rfind(ind) for ind in bachelor_indicators if ind in context_before]
                    bachelor_positions.extend([degree_pos + context_after.find(ind) for ind in bachelor_indicators if ind in context_after])
                    
                    if master_positions and bachelor_positions:
                        closest_master = min([abs(p - degree_pos) for p in master_positions if p >= 0])
                        closest_bachelor = min([abs(p - degree_pos) for p in bachelor_positions if p >= 0])
                        if closest_master < closest_bachelor:
                            result = f"M.Tech in {spec.title()}"
                        else:
                            # Closer to bachelor - determine type
                            if any(ind in context_before or ind in context_after for ind in ['b.e', 'b e', 'b.e.']):
                                result = f"B.E. in {spec.title()}"
                            elif any(ind in context_before or ind in context_after for ind in ['b.tech', 'btech', 'b.tech.']):
                                result = f"B.Tech in {spec.title()}"
                            elif any(ind in context_before or ind in context_after for ind in ['bachelor', 'bachelors']):
                                result = f"Bachelor's in {spec.title()}"
                            else:
                                result = spec.title()
                    else:
                        # Default to specialization if unclear
                        result = spec.title()
                else:
                    # No degree level mentioned - return just the specialization
                    result = spec.title()
                    logger.info(f"Degree extracted (specialization only, no level mentioned): {result}")
                    return result
                
                logger.info(f"Degree extracted (degree in format): {result}, matched spec: {spec} from: {spec_mentioned}")
                return result
    
    # Pattern 2: Full degree names with specialization
    spec_pattern = '|'.join(SPECIALIZATIONS)
    full_patterns = [
        (rf'\b(bachelor\s+of\s+(?:technology|engineering|science|arts|commerce))\s+(?:in\s+)?({spec_pattern})', 'bachelor'),
        (rf'\b(master\s+of\s+(?:technology|engineering|science|arts|commerce|business\s+administration))\s+(?:in\s+)?({spec_pattern})', 'master'),
        (rf'\b(bachelor\s+in\s+({spec_pattern}))', 'bachelor'),
        (rf'\b(master\s+in\s+({spec_pattern}))', 'master'),
    ]
    
    for pattern, degree_type in full_patterns:
        match = re.search(pattern, transcript_lower)
        if match:
            if len(match.groups()) > 1 and match.group(2):
                spec = match.group(2).strip()
                # Use the captured degree name to decide the prefix
                captured_degree = match.group(1).lower()
                
                if 'technology' in captured_degree:
                    degree_prefix = "B.Tech" if 'bachelor' in captured_degree else "M.Tech"
                elif 'engineering' in captured_degree:
                    degree_prefix = "B.E." if 'bachelor' in captured_degree else "M.E."
                elif 'science' in captured_degree:
                    degree_prefix = "B.Sc" if 'bachelor' in captured_degree else "M.Sc"
                elif 'arts' in captured_degree:
                    degree_prefix = "B.A." if 'bachelor' in captured_degree else "M.A."
                elif 'commerce' in captured_degree:
                    degree_prefix = "B.Com" if 'bachelor' in captured_degree else "M.Com"
                elif 'business' in captured_degree:
                    degree_prefix = "MBA" # Master only usually
                else:
                    degree_prefix = "Bachelor's" if 'bachelor' in captured_degree else "Master's"
                
                result = f"{degree_prefix} in {spec.title()}"
                logger.info(f"Degree extracted (full): {result}")
                return result
    
    # Pattern 2: Abbreviated forms with specialization in same sentence
    abbrev_patterns = [
        (rf'\b(b\.?\s*tech\.?|btech)\s+(?:in\s+)?({spec_pattern})', 'B.Tech'),
        (rf'\b(m\.?\s*tech\.?|mtech|m\.?\s*e\.?)\s+(?:in\s+)?({spec_pattern})', 'M.Tech'),
        (rf'\b(b\.?\s*sc\.?|bsc)\s+(?:in\s+)?({spec_pattern})', 'B.Sc'),
        (rf'\b(m\.?\s*sc\.?|msc)\s+(?:in\s+)?({spec_pattern})', 'M.Sc'),
    ]
    
    # First, try to find degree abbreviation with specialization in same sentence (only if doc available)
    if doc is not None:
        sentences_list = list(doc.sents)
        for i, sent in enumerate(sentences_list):
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in DEGREE_KEYWORDS):
                for pattern, degree_abbrev in abbrev_patterns:
                    match = re.search(pattern, sent.text, re.IGNORECASE)
                    if match:
                        if len(match.groups()) > 1 and match.group(2):
                            spec = match.group(2).strip()
                            result = f"{degree_abbrev} in {spec.title()}"
                            logger.info(f"Degree extracted (abbrev with spec in same sentence): {result}")
                            return result
        
        # Pattern 3: Find degree abbreviation, then search for specialization in nearby context
        simple_patterns = [
            (r'\b(b\.?\s*tech\.?|btech)\b', 'B.Tech'),
            (r'\b(m\.?\s*tech\.?|mtech|m\.?\s*e\.?)\b', 'M.Tech'),
            (r'\b(b\.?\s*sc\.?|bsc)\b', 'B.Sc'),
            (r'\b(m\.?\s*sc\.?|msc)\b', 'M.Sc'),
            (r'\b(m\.?\s*b\.?\s*a\.?|mba)\b', 'MBA'),
        ]
        
        # Find degree abbreviation first
        degree_found = None
        degree_sentence_idx = None
        
        for i, sent in enumerate(sentences_list):
            sent_text = sent.text.lower()
            if any(keyword in sent_text for keyword in DEGREE_KEYWORDS):
                for pattern, degree_name in simple_patterns:
                    if re.search(pattern, sent.text, re.IGNORECASE):
                        degree_found = degree_name
                        degree_sentence_idx = i
                        break
                if degree_found:
                    break
        
        # If degree found, search for specialization in nearby sentences (current, previous, next)
        if degree_found and degree_sentence_idx is not None:
            # Search in current sentence and adjacent sentences
            search_indices = [
                max(0, degree_sentence_idx - 1),
                degree_sentence_idx,
                min(len(sentences_list) - 1, degree_sentence_idx + 1)
            ]
            
            # Also search in a wider context window (50 words around the degree mention)
            degree_pos = None
            for i, sent in enumerate(sentences_list):
                if i == degree_sentence_idx:
                    # Find position of degree in transcript
                    degree_match = re.search(simple_patterns[0][0] if 'tech' in degree_found.lower() else simple_patterns[2][0], sent.text, re.IGNORECASE)
                    if degree_match:
                        # Get character position in full transcript
                        char_start = transcript.lower().find(sent.text.lower())
                        if char_start != -1:
                            degree_pos = char_start + degree_match.start()
                    break
            
            # Search for specialization in context window (wider search)
            if degree_pos is not None:
                # Search in wider context (400 chars before and after for better coverage)
                context_start = max(0, degree_pos - 400)
                context_end = min(len(transcript), degree_pos + 400)
                context_window = transcript[context_start:context_end].lower()
                
                # Look for specializations in context window (prioritize longer/more specific ones first)
                # Sort by length (longest first) to match "computer science engineering" before "it"
                sorted_specs = sorted(SPECIALIZATIONS, key=len, reverse=True)
                
                for spec in sorted_specs:
                    if spec in context_window:
                        # Verify it's not part of a skill mention
                        spec_pos = context_window.find(spec)
                        context_snippet = context_window[max(0, spec_pos-60):min(len(context_window), spec_pos+len(spec)+60)]
                        # Check if it's in a degree-related context (more lenient)
                        degree_context_keywords = ['degree', 'studied', 'graduated', 'completed', 'in', 'of', 'specialization', 'major', 'field', 'subject', 'branch']
                        # Also check if it's not in a skills context
                        skill_context_keywords = ['skill', 'know', 'expert', 'proficient', 'experience with', 'worked with', 'proficient in', 'good at']
                        
                        has_degree_context = any(keyword in context_snippet for keyword in degree_context_keywords)
                        has_skill_context = any(keyword in context_snippet for keyword in skill_context_keywords)
                        
                        # Prefer degree context, but if no skill context, accept it
                        # Also prioritize longer specializations (more specific)
                        if has_degree_context or (not has_skill_context and len(spec) > 5):
                            result = f"{degree_found} in {spec.title()}"
                            logger.info(f"Degree extracted (with nearby specialization): {result}")
                            return result
            
            # Also check adjacent sentences for specialization (more lenient, prioritize longer specs)
            sorted_specs_adjacent = sorted(SPECIALIZATIONS, key=len, reverse=True)
            for idx in search_indices:
                sent_text = sentences_list[idx].text.lower()
                for spec in sorted_specs_adjacent:
                    if spec in sent_text:
                        # More lenient: check if it's NOT in a skill context, or if it's in degree context
                        skill_indicators = ['skill', 'know', 'expert', 'proficient', 'experience', 'worked', 'proficient in', 'good at']
                        degree_indicators = ['degree', 'studied', 'graduated', 'completed', 'in', 'of', 'specialization', 'major', 'field', 'subject', 'branch']
                        
                        has_skill_indicator = any(indicator in sent_text for indicator in skill_indicators)
                        has_degree_indicator = any(indicator in sent_text for indicator in degree_indicators)
                        
                        # If it has degree indicators OR doesn't have skill indicators, accept it
                        # Prioritize longer specializations (more specific)
                        if has_degree_indicator or (not has_skill_indicator and len(spec) > 5):
                            result = f"{degree_found} in {spec.title()}"
                            logger.info(f"Degree extracted (with specialization in adjacent sentence): {result}")
                            return result
            
            # If no specialization found, return just the degree
            logger.info(f"Degree extracted (without specialization): {degree_found}")
            return degree_found
    
    return None

def extract_name(transcript: str, doc=None) -> Optional[str]:
    """Extract name with validation"""
    if doc is None:
        # Regex-only fallback: look for "my name is" or "I am" patterns
        name_patterns = [
            r"(?:my name is|i am|i'm|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s+here|\s+speaking)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if 2 <= len(name) <= 50:
                    logger.info(f"Name extracted via regex: {name}")
                    return name.title()
        return None
    
    persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    
    for person in persons:
        # Validate: name should be reasonable length and not common words
        if (2 <= len(person) <= 50 and 
            person.lower() not in {'i', 'me', 'my', 'you', 'he', 'she', 'we', 'they'} and
            not person.isdigit()):
            logger.info(f"Name extracted: {person}")
            return person.title()
    
    return None

def extract_candidate_info(transcript: str) -> Dict[str, Optional[str]]:
    """
    Extract candidate information from transcript using optimized NLP
    Improved accuracy with validation and better pattern matching
    
    Args:
        transcript: Text transcript of interview
        
    Returns:
        Dictionary with extracted candidate information
    """
    if not transcript or len(transcript.strip()) < 10:
        logger.warning("Transcript too short or empty")
        return {
            "name": None, "email": None, "phone": None, "college": None,
            "degree": None, "graduation_year": None, "experience": None,
            "location": None, "skills": None
        }
    
    result = {
        "name": None,
        "email": None,
        "phone": None,
        "college": None,
        "degree": None,
        "graduation_year": None,
        "experience": None,
        "location": None,
        "skills": None
    }
    
    # Fast regex-based extractions first (no NLP needed)
    result["email"] = extract_email(transcript)
    result["phone"] = extract_phone(transcript)
    result["experience"] = extract_experience(transcript)
    result["skills"] = extract_skills(transcript)
    
    # Optimize NLP processing for long transcripts
    nlp = load_nlp_model()
    doc = None
    
    # Only process with NLP if model is available
    if nlp is not None:
        # For long transcripts, process only relevant sentences
        if len(transcript) > 2000:
            sentences = [s.strip() for s in transcript.split('.') if s.strip()]
            relevant_sentences = []
            
            for sent in sentences:
                sent_lower = sent.lower()
                # Include sentences with keywords or short sentences (likely introductions)
                if (any(keyword in sent_lower for keyword in 
                       ['name', 'i am', 'my name', 'from', 'location', 'live', 'college', 
                        'university', 'degree', 'graduated', 'graduate', 'studied']) or
                    len(sent) < 100):
                    relevant_sentences.append(sent)
            
            # Process relevant sentences + first 3 and last 3
            if relevant_sentences:
                sample_text = '. '.join(relevant_sentences[:25] + sentences[:3] + sentences[-3:])
                doc = nlp(sample_text)
            else:
                doc = nlp(transcript[:2000])
        else:
            doc = nlp(transcript)
    else:
        logger.warning("NLP model unavailable - using regex-only extraction")
    
    # Extract complex entities using NLP (or regex fallback if doc is None)
    result["name"] = extract_name(transcript, doc)
    result["location"] = extract_location(transcript, doc)
    result["graduation_year"] = extract_graduation_year(transcript, doc)
    result["college"] = extract_college(transcript, doc)
    result["degree"] = extract_degree(transcript, doc)
    
    logger.info(f"Extraction complete. Found: {sum(1 for v in result.values() if v)} fields")
    return result
