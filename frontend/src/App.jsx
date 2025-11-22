import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import CandidateList from './components/CandidateList'
import CandidateDetail from './components/CandidateDetail'
import UploadAudio from './components/UploadAudio'
import LiveRecording from './components/LiveRecording'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<UploadAudio />} />
          <Route path="/record" element={<LiveRecording />} />
          <Route path="/candidates" element={<CandidateList />} />
          <Route path="/candidates/:id" element={<CandidateDetail />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

