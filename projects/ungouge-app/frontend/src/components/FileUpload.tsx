'use client'

import { useState, useCallback } from 'react'
import { Upload, FileText, Image, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

interface FileUploadProps {
  onFileProcessed: (data: ParsedQuoteData) => void
  onError: (error: string) => void
}

export interface ParsedQuoteData {
  project_type?: string
  location?: string
  contractor_name?: string
  line_items: Array<{
    item_name: string
    description?: string
    quoted_price: number
    quantity: number
    unit: string
  }>
}

export default function FileUpload({ onFileProcessed, onError }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string>('')
  const [uploadStep, setUploadStep] = useState<number>(0) // 0: idle, 1: uploading, 2: extracting, 3: analyzing, 4: complete

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    if (droppedFiles.length > 0) {
      handleFiles(droppedFiles)
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files ? Array.from(e.target.files) : []
    if (selectedFiles.length > 0) {
      handleFiles(selectedFiles)
    }
  }

  const handleFiles = (newFiles: File[]) => {
    // Validate file types
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
    const invalidFiles = newFiles.filter(f => !validTypes.includes(f.type))
    if (invalidFiles.length > 0) {
      onError(`Invalid file type(s): ${invalidFiles.map(f => f.name).join(', ')}. Please upload PDF or image files only.`)
      return
    }

    // Validate file sizes (max 10MB each)
    const oversizedFiles = newFiles.filter(f => f.size > 10 * 1024 * 1024)
    if (oversizedFiles.length > 0) {
      onError(`File(s) too large: ${oversizedFiles.map(f => f.name).join(', ')}. Max 10MB per file.`)
      return
    }

    // Limit to 10 files max
    if (newFiles.length > 10) {
      onError('Maximum 10 files allowed')
      return
    }

    setFiles(newFiles)
    uploadAndParse(newFiles)
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadAndParse = async (filesToUpload: File[]) => {
    setUploading(true)
    setUploadStep(1)
    const fileCount = filesToUpload.length
    setUploadProgress(fileCount === 1 ? 'Uploading your quote...' : `Uploading ${fileCount} files...`)

    try {
      // Create form data with all files
      const formData = new FormData()
      filesToUpload.forEach(file => {
        formData.append('files', file)
      })

      // Upload to backend (uses Next.js rewrite proxy)
      const response = await fetch('/api/quotes/parse-upload', {
        method: 'POST',
        credentials: 'include',  // Send auth cookies
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const detail = errorData.detail
        const message = typeof detail === 'string' 
          ? detail 
          : typeof detail === 'object' && detail !== null
            ? (detail.error || detail.message || JSON.stringify(detail))
            : errorData.error || 'Unable to process your file. Please ensure it\'s a clear image or PDF of your quote.'
        throw new Error(message)
      }

      setUploadStep(2)
      setUploadProgress('Extracting text from your document...')
      
      // Wait a bit for visual feedback
      await new Promise(resolve => setTimeout(resolve, 800))

      setUploadStep(3)
      setUploadProgress('Analyzing your quote with AI...')
      
      const data = await response.json()

      setUploadStep(4)
      setUploadProgress('Analysis complete! Populating your form...')
      
      // Pass parsed data to parent
      await new Promise(resolve => setTimeout(resolve, 500))
      onFileProcessed(data)

      // Reset after success
      setTimeout(() => {
        setUploading(false)
        setUploadProgress('')
        setUploadStep(0)
      }, 800)

    } catch (error) {
      console.error('Upload error:', error)
      onError(error instanceof Error ? error.message : 'We couldn\'t process your file. Please try again or enter details manually.')
      setUploading(false)
      setUploadProgress('')
      setUploadStep(0)
      setFiles([])
    }
  }

  return (
    <div className="w-full">
      {files.length === 0 && !uploading && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-xl p-8 sm:p-12 text-center cursor-pointer
            transition-all duration-300 ease-out
            ${isDragging 
              ? 'border-blue-500 bg-blue-50 scale-[1.02] shadow-lg' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50 hover:shadow-md'
            }
          `}
        >
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg"
            multiple
            onChange={handleFileInput}
          />
          
          <label htmlFor="file-upload" className="cursor-pointer block">
            <div className={`
              w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 rounded-full flex items-center justify-center
              transition-all duration-300
              ${isDragging ? 'bg-blue-100 scale-110' : 'bg-gray-100'}
            `}>
              <Upload className={`w-8 h-8 sm:w-10 sm:h-10 transition-colors ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} />
            </div>
            <h3 className="text-lg sm:text-xl font-semibold mb-2 text-gray-800">
              Drop your contractor quote here
            </h3>
            <p className="text-sm sm:text-base text-gray-600 mb-3">
              or <span className="text-blue-600 font-semibold">click to browse</span>
            </p>
            <p className="text-xs sm:text-sm text-gray-500">
              Supports PDF, PNG, JPG • Max 10MB per file • Up to 10 files
            </p>
            <p className="text-xs text-blue-600 mt-2">
              💡 Multi-page quote? Select all images at once
            </p>
          </label>
        </div>
      )}

      {files.length > 0 && !uploading && (
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-gray-700">
              {files.length} file{files.length > 1 ? 's' : ''} ready to process
            </p>
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          {files.map((file, index) => (
            <div
              key={`${file.name}-${index}`}
              className="border-2 border-green-300 bg-green-50 rounded-lg p-3 sm:p-4 flex items-center justify-between gap-3 transition-all duration-300"
            >
              <div className="flex items-center space-x-3 min-w-0 flex-1">
                <div className="flex-shrink-0">
                  {file.type === 'application/pdf' ? (
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-red-600" />
                    </div>
                  ) : (
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Image className="w-5 h-5 text-blue-600" />
                    </div>
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-gray-800 truncate text-sm">{file.name}</p>
                  <p className="text-xs text-gray-600">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeFile(index)}
                className="flex-shrink-0 p-2 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-100 transition-all duration-200"
                aria-label={`Remove ${file.name}`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {uploading && (
        <div className="border-2 border-blue-300 rounded-lg p-8 bg-gradient-to-br from-blue-50 to-indigo-50">
          <div className="flex flex-col items-center">
            {/* Animated spinner */}
            <div className="relative mb-6">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200"></div>
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent absolute top-0 left-0"></div>
              {uploadStep === 4 && (
                <CheckCircle className="w-8 h-8 text-green-600 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
              )}
            </div>

            {/* Progress text */}
            <p className="text-blue-900 font-semibold text-lg mb-2">{uploadProgress}</p>
            
            {/* Progress steps */}
            <div className="w-full max-w-md mt-4">
              <div className="flex justify-between text-xs text-blue-700 mb-2">
                <span className={uploadStep >= 1 ? 'font-semibold' : 'opacity-50'}>Upload</span>
                <span className={uploadStep >= 2 ? 'font-semibold' : 'opacity-50'}>Extract</span>
                <span className={uploadStep >= 3 ? 'font-semibold' : 'opacity-50'}>Analyze</span>
                <span className={uploadStep >= 4 ? 'font-semibold' : 'opacity-50'}>Complete</span>
              </div>
              <div className="h-2 bg-blue-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${(uploadStep / 4) * 100}%` }}
                />
              </div>
            </div>

            <p className="text-sm text-blue-600 mt-4">
              {uploadStep < 4 ? 'This usually takes 10-30 seconds...' : 'Success! 🎉'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
