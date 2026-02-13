import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Upload from './pages/Upload'
import CandidateMatches from './pages/CandidateMatches'
import Interviewers from './pages/Interviewers'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/candidate/:id" element={<CandidateMatches />} />
        <Route path="/interviewers" element={<Interviewers />} />
      </Routes>
    </Layout>
  )
}
