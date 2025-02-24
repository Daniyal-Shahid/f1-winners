import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SentimentDetails from './pages/SentimentDetails';
import F1Dashboard from './components/F1Dashboard'
import RaceResults from './components/RaceResults';
import DriverAnalysis from './components/DriverAnalysis';
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-surface">
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<F1Dashboard />} />
            <Route path="/sentiment/:driver" element={<SentimentDetails />} />
            <Route path="/race-results" element={<RaceResults />} />
            <Route path="/driver-analysis/:driver" element={<DriverAnalysis />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}


export default App