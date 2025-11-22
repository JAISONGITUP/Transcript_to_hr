import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import axios from 'axios'

export default function CandidateDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchCandidate()
  }, [id])

  const fetchCandidate = async () => {
    try {
      const response = await axios.get(`/api/candidates/${id}`)
      setCandidate(response.data.candidate)
    } catch (error) {
      console.error('Error fetching candidate:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      setDeleting(true)
      try {
        await axios.delete(`/api/candidates/${id}`)
        navigate('/candidates')
      } catch (error) {
        console.error('Error deleting candidate:', error)
        alert('Error deleting candidate')
      } finally {
        setDeleting(false)
      }
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    )
  }

  if (!candidate) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="text-center">
            <p className="text-slate-500 text-lg mb-4">Candidate not found</p>
            <Link
              to="/candidates"
              className="inline-block bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-medium"
            >
              Back to Candidates
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="mb-6 flex justify-between items-center">
          <Link
            to="/candidates"
            className="text-slate-600 hover:text-gray-900 font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Candidates
          </Link>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="bg-gradient-to-r from-red-600 to-rose-600 text-white px-6 py-2 rounded-lg hover:from-red-700 hover:to-rose-700 disabled:from-gray-400 disabled:to-gray-400 transition-all duration-200 font-medium"
          >
            {deleting ? 'Deleting...' : 'Delete Candidate'}
          </button>
        </div>

        <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-lg shadow-sm overflow-hidden">
          <div className="bg-gradient-to-r from-slate-100 to-slate-200 border-b border-slate-200 px-8 py-6">
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-2xl font-semibold shadow-sm">
                {candidate.name ? candidate.name.charAt(0).toUpperCase() : '?'}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-1">
                  {candidate.name || 'Unnamed Candidate'}
                </h1>
                <p className="text-slate-600 text-sm">
                  Added on {new Date(candidate.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
          </div>

          <div className="px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Name
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.name || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Email
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.email || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Phone
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.phone || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Location
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.location || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  College
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.college || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Degree
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.degree || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Graduation Year
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.graduation_year || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Experience
                </label>
                <p className="text-lg font-medium text-gray-900">
                  {candidate.experience || <span className="text-slate-400">Not provided</span>}
                </p>
              </div>
              
              <div className="md:col-span-2">
                <div className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                    Skills
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills ? (
                      candidate.skills.split(', ').map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1.5 bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-800 rounded-md text-sm font-medium border border-blue-200"
                        >
                          {skill.trim()}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400">Not provided</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {candidate.transcript && (
              <div className="mt-8 pt-8 border-t border-slate-200">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Full Transcript</h2>
                <div className="bg-gradient-to-br from-slate-50 to-white p-6 rounded-lg border border-slate-200 max-h-96 overflow-y-auto">
                  <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{candidate.transcript}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
