import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  XMarkIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import { DocumentType, FileUpload, ProcessingState } from '@/types'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function DocumentUpload() {
  const [files, setFiles] = useState<FileUpload[]>([])
  const [selectedProject, setSelectedProject] = useState('')
  const [documentType, setDocumentType] = useState<DocumentType>(DocumentType.UNKNOWN)
  const [additionalContext, setAdditionalContext] = useState('')
  const [processing, setProcessing] = useState<ProcessingState>({
    isProcessing: false,
    progress: 0,
    currentStep: ''
  })
  const navigate = useNavigate()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'pending' as const
    }))
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const processFiles = async () => {
    if (files.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    setProcessing({
      isProcessing: true,
      progress: 0,
      currentStep: 'Preparing upload...'
    })

    try {
      for (let i = 0; i < files.length; i++) {
        const fileUpload = files[i]
        
        setProcessing(prev => ({
          ...prev,
          progress: (i / files.length) * 100,
          currentStep: `Processing ${fileUpload.file.name}...`
        }))

        // Simulate file processing
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Update file status
        setFiles(prev => prev.map((f, index) => 
          index === i ? { ...f, status: 'complete' } : f
        ))
      }

      setProcessing({
        isProcessing: false,
        progress: 100,
        currentStep: 'Complete!'
      })

      toast.success('All files processed successfully!')
      
      // Navigate to results page
      setTimeout(() => {
        navigate('/projects')
      }, 1000)

    } catch (error) {
      setProcessing({
        isProcessing: false,
        progress: 0,
        currentStep: '',
        error: 'Processing failed'
      })
      toast.error('Failed to process files')
    }
  }

  const getFileIcon = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'pdf':
        return '📄'
      case 'doc':
      case 'docx':
        return '📝'
      case 'md':
        return '📋'
      default:
        return '📄'
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Documents</h1>
        <p className="text-gray-600">Transform your project documents into structured epics and user stories</p>
      </div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="card-body">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
              isDragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            {isDragActive ? (
              <p className="text-lg text-primary-600">Drop your files here...</p>
            ) : (
              <div>
                <p className="text-lg text-gray-600 mb-2">
                  Drag & drop files here, or <span className="text-primary-600 font-semibold">browse</span>
                </p>
                <p className="text-sm text-gray-500">
                  Supports PDF, Word docs, Markdown, and text files (max 10MB)
                </p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="card"
          >
            <div className="card-header">
              <h3 className="text-lg font-semibold">Selected Files ({files.length})</h3>
            </div>
            <div className="card-body space-y-3">
              {files.map((fileUpload, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{getFileIcon(fileUpload.file)}</span>
                    <div>
                      <p className="font-medium text-gray-900">{fileUpload.file.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(fileUpload.file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {fileUpload.status === 'complete' && (
                      <CheckCircleIcon className="h-5 w-5 text-success-600" />
                    )}
                    {fileUpload.status === 'error' && (
                      <ExclamationTriangleIcon className="h-5 w-5 text-error-600" />
                    )}
                    <button
                      onClick={() => removeFile(index)}
                      className="p-1 hover:bg-gray-200 rounded-full"
                    >
                      <XMarkIcon className="h-4 w-4 text-gray-500" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Processing Options */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold">Processing Options</h3>
        </div>
        <div className="card-body space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Type
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value as DocumentType)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value={DocumentType.UNKNOWN}>Auto-detect</option>
              <option value={DocumentType.PRD}>Product Requirements Document</option>
              <option value={DocumentType.RFC}>Request for Comments</option>
              <option value={DocumentType.REQUIREMENTS}>Requirements Document</option>
              <option value={DocumentType.FEATURE_SPEC}>Feature Specification</option>
              <option value={DocumentType.MARKDOWN}>Markdown</option>
              <option value={DocumentType.TEXT}>Plain Text</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Context (Optional)
            </label>
            <textarea
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              rows={3}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              placeholder="Provide any additional context that might help with processing..."
            />
          </div>
        </div>
      </div>

      {/* Processing Status */}
      <AnimatePresence>
        {processing.isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="card"
          >
            <div className="card-body">
              <div className="flex items-center space-x-3 mb-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                <span className="font-medium text-gray-900">{processing.currentStep}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${processing.progress}%` }}
                />
              </div>
              <div className="text-sm text-gray-600 mt-2">{Math.round(processing.progress)}% complete</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => setFiles([])}
          className="btn btn-secondary"
          disabled={processing.isProcessing}
        >
          Clear All
        </button>
        <button
          onClick={processFiles}
          disabled={files.length === 0 || processing.isProcessing}
          className="btn btn-primary flex items-center space-x-2"
        >
          <span>Process Documents</span>
          <ArrowRightIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
} 