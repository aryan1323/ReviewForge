import { Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { DashboardPage } from './pages/DashboardPage'
import { PRListPage } from './pages/PRListPage'
import { PRDetailPage } from './pages/PRDetailPage'
import { AnalyticsPage } from './pages/AnalyticsPage'

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/"          element={<DashboardPage />} />
            <Route path="/prs"       element={<PRListPage />} />
            <Route path="/prs/:id"   element={<PRDetailPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="*"          element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
