import { Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './components/MainLayout'
import Chat from './pages/Chat'
import Knowledge from './pages/Knowledge'
import Resume from './pages/Resume'
import Eval from './pages/Eval'
import Gap from './pages/Gap'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<Chat />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="resume" element={<Resume />} />
        <Route path="eval" element={<Eval />} />
        <Route path="gap" element={<Gap />} />
      </Route>
    </Routes>
  )
}

export default App
