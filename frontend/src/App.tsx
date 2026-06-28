import { Navigate, Route, Routes } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AppLayout } from './layouts/AppLayout'
import { DocumentUploadPage } from './pages/DocumentUploadPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { HealthDashboardPage } from './pages/HealthDashboardPage'
import { ResearchChatPage } from './pages/ResearchChatPage'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<ResearchChatPage />} />
          <Route path="/upload" element={<DocumentUploadPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/health" element={<HealthDashboardPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}

export default App
