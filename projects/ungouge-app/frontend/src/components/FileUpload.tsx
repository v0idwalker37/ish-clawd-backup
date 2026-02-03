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
  const [file, setFile] = useState<File | null>(null)
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

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      handleFile(droppedFile)
    }
  }, [])

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      handleFile(selectedFile)
    }
  }

  const handleFile = (file: File) => {
    // Validate file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/heic']
    if (!validTypes.includes(file.type)) {
      onError('Please upload a PDF or image file (PNG, JPG, HEIC)')
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      onError('File size must be less than 10MB')
      return
    }

    setFile(file)
    uploadAndParse(file)
  }

  const uploadAndParse = async (file: File) => {
    setUploading(true)
    setUploadStep(1)
    setUploadProgress('Uploading your quote...')

    try {
      // Create form data
      const formData = new FormData()
      formData.append('file', file)

      // Upload to backend
      const response = await fetch('/api/quotes/parse-upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Unable to process your file. Please ensure it\'s a clear image or PDF of your quote.')
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
      setFile(null)
    }
  }

  const removeFile = () => {
    setFile(null)
    setUploadProgress('')
  }

  return (
    <div className="w-full">
      {!file && !uploading && (
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
            accept=".pdf,.png,.jpg,.jpeg,.heic"
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
              Supports PDF, PNG, JPG, HEIC • Max 10MB
            </p>
          </label>
        </div>
      )}

      {file && !uploading && (
        <div className="border-2 border-green-300 bg-green-50 rounded-lg p-4 sm:p-6 flex items-center justify-between gap-4 transition-all duration-300">
          <div className="flex items-center space-x-3 min-w-0 flex-1">
            <div className="flex-shrink-0">
              {file.type === 'application/pdf' ? (
                <div className="w-12 h-12 sm:w-14 sm:h-14 bg-red-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 sm:w-7 sm:h-7 text-red-600" />
                </div>
              ) : (
                <div className="w-12 h-12 sm:w-14 sm:h-14 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Image className="w-6 h-6 sm:w-7 sm:h-7 text-blue-600" />
                </div>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-semibold text-gray-800 truncate">{file.name}</p>
                <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
              </div>
              <p className="text-sm text-gray-600">
                {(file.size / 1024 / 1024).toFixed(2)} MB • Ready to process
              </p>
            </div>
          </div>
          <button
            onClick={removeFile}
            className="flex-shrink-0 p-2 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-100 transition-all duration-200"
            aria-label="Remove file"
          >
            <X className="w-5 h-5 sm:w-6 sm:h-6" />
          </button>
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
