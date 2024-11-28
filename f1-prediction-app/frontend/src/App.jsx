import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SentimentDetails from './pages/SentimentDetails';
import F1Dashboard from './components/F1Dashboard'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<F1Dashboard />} />
        <Route path="/sentiment/:driver" element={<SentimentDetails />} />
      </Routes>
    </Router>
  )
}


export default App