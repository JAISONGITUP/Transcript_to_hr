import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

export default function LiveRecording() {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioBlob, setAudioBlob] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [transcript, setTranscript] = useState('')
  const [extractedData, setExtractedData] = useState(null)
  
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)
      setError('')
      setSuccess('')

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } catch (err) {
      setError('Could not access microphone. Please check permissions.')
      console.error('Error accessing microphone:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    if (timerRef.current) {
      clearInterval(timerRef.current)
    }
    setIsRecording(false)
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleProcess = async () => {
    if (!audioBlob) {
      setError('No recording available')
      return
    }

    setProcessing(true)
    setError('')
    setSuccess('Processing audio...')

    try {
      const formData = new FormData()
      // Convert webm to a file-like object
      const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' })
      formData.append('file', audioFile)

      const response = await axios.post('/api/process-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const transcriptText = response.data.transcript
      const extracted = response.data.extracted_data
      
      setTranscript(transcriptText)
      setExtractedData(extracted)
      setSuccess('Candidate processed and saved successfully!')
      
      setTimeout(() => {
        navigate(`/candidates/${response.data.candidate_id}`)
      }, 2000)

    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during processing')
      console.error('Error:', err)
    } finally {
      setProcessing(false)
    }
  }

  const handleReset = () => {
    setAudioBlob(null)
    setTranscript('')
    setExtractedData(null)
    setRecordingTime(0)
    setError('')
    setSuccess('')
  }

  return (
    <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Live Recording</h1>

        <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-lg shadow-sm p-8 mb-6">
          <div className="text-center mb-6">
            {isRecording ? (
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-red-500 to-rose-600 animate-pulse mb-4 shadow-lg">
                <div className="w-16 h-16 rounded-full bg-red-600"></div>
              </div>
            ) : (
              <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 mb-4">
                <svg className="w-12 h-12 text-slate-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              </div>
            )}
            
            <div className="text-4xl font-bold text-gray-800 mb-2">
              {formatTime(recordingTime)}
            </div>
            <p className="text-sm text-gray-600">
              {isRecording ? 'Recording in progress...' : audioBlob ? 'Recording complete' : 'Ready to record'}
            </p>
          </div>

          <div className="flex justify-center gap-4">
            {!isRecording && !audioBlob && (
              <button
                onClick={startRecording}
                className="px-8 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all duration-200 transform hover:scale-105 shadow-sm font-semibold flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Start Recording
              </button>
            )}

            {isRecording && (
              <button
                onClick={stopRecording}
                className="px-8 py-3 bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-lg hover:from-red-700 hover:to-rose-700 transition-all duration-200 transform hover:scale-105 shadow-sm font-semibold flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 000 2h4a1 1 0 100-2H8z" clipRule="evenodd" />
                </svg>
                Stop Recording
              </button>
            )}

            {audioBlob && !isRecording && (
              <>
                <button
                  onClick={handleProcess}
                  disabled={processing}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 transition-all duration-200 transform hover:scale-105 shadow-sm font-semibold flex items-center gap-2"
                >
                  {processing ? (
                    <>
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
                      </svg>
                      Process Recording
                    </>
                  )}
                </button>
                <button
                  onClick={handleReset}
                  className="px-8 py-3 bg-gradient-to-r from-slate-600 to-slate-700 text-white rounded-lg hover:from-slate-700 hover:to-slate-800 transition-all duration-200 transform hover:scale-105 shadow-sm font-semibold"
                >
                  Record Again
                </button>
              </>
            )}
          </div>

          {error && (
            <div className="mt-4 bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}
        </div>

        {transcript && (
          <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Transcript</h2>
            <div className="bg-white p-4 rounded-lg max-h-64 overflow-y-auto border border-slate-200">
              <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{transcript}</p>
            </div>
          </div>
        )}

        {extractedData && (
          <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-lg shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Extracted Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(extractedData).map(([key, value]) => (
                <div key={key} className="bg-white p-4 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">
                    {key.replace('_', ' ')}
                  </label>
                  <p className="text-sm font-medium text-gray-900">{value || 'N/A'}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

