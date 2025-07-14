import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Layout from '@/components/Layout'
import Dashboard from '@/pages/Dashboard'
import DocumentUpload from '@/pages/DocumentUpload'
import Projects from '@/pages/Projects'
import ProjectDetails from '@/pages/ProjectDetails'
import ProcessingResults from '@/pages/ProcessingResults'
import Settings from '@/pages/Settings'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Layout>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex-1"
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectDetails />} />
            <Route path="/results/:documentId" element={<ProcessingResults />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={
              <div className="flex items-center justify-center min-h-96">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-gray-600 mb-8">Page not found</p>
                  <a 
                    href="/" 
                    className="btn btn-primary btn-lg"
                  >
                    Go Home
                  </a>
                </div>
              </div>
            } />
          </Routes>
        </motion.div>
      </Layout>
    </div>
  )
}

export default App 