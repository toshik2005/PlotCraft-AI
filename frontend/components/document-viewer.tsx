"use client"

import { useState, useEffect } from "react"
import { X, Download, FileText, Image as ImageIcon, File, ExternalLink, User, Calendar, MapPin, Briefcase, Star, Share2, Copy, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useTheme } from "@/components/ui/theme-provider"

interface DocumentViewerProps {
  documentUrl: string
  documentName: string
  documentType?: string
  candidateData?: {
    applicantName: string
    email: string
    mobile: string
    city: string
    totalExperience: string
    jobDetails: string
    technicalSkills: string[]
    softSkills: string[]
    createdAt: string
  }
  onClose: () => void
}

export function DocumentViewer({ documentUrl, documentName, documentType, candidateData, onClose }: DocumentViewerProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [showShareOptions, setShowShareOptions] = useState(false)
  const [expandTechSkills, setExpandTechSkills] = useState(false)
  const [expandSoftSkills, setExpandSoftSkills] = useState(false)
  const { theme } = useTheme()
  const isDark = theme === "dark"

  // In some browsers, PDF iframes do not reliably emit onLoad; add a safety timer
  useEffect(() => {
    if (documentType?.toLowerCase() === 'pdf' && loading) {
      const timer = setTimeout(() => {
        setLoading(false)
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [documentType, loading])

  const getDocumentIcon = () => {
    if (!documentType) return <File className="h-8 w-8" />
    
    switch (documentType.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-8 w-8 text-red-500" />
      case 'docx':
      case 'doc':
        return <FileText className="h-8 w-8 text-blue-500" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
      case 'tiff':
        return <ImageIcon className="h-8 w-8 text-green-500" />
      default:
        return <File className="h-8 w-8 text-gray-500" />
    }
  }

  const getDocumentTypeName = () => {
    if (!documentType) return "Document"
    
    switch (documentType.toLowerCase()) {
      case 'pdf':
        return "PDF Document"
      case 'docx':
        return "Word Document"
      case 'doc':
        return "Word Document"
      case 'jpg':
      case 'jpeg':
        return "Image"
      case 'png':
        return "PNG Image"
      case 'gif':
        return "GIF Image"
      case 'bmp':
        return "Bitmap Image"
      case 'tiff':
        return "TIFF Image"
      default:
        return "Document"
    }
  }

  const handleDownload = () => {
    // Prefer the native save dialog via File System Access API when available
    const saveWithPicker = async (blob: Blob) => {
      try {
        // @ts-ignore - showSaveFilePicker not in all TS libs
        const handle = await (window as any).showSaveFilePicker?.({
          suggestedName: documentName,
          types: [
            {
              description: 'Documents',
              accept: {
                'application/pdf': ['.pdf'],
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
                'application/msword': ['.doc']
              }
            }
          ]
        })
        if (handle) {
          const writable = await handle.createWritable()
          await writable.write(blob)
          await writable.close()
          return true
        }
      } catch (e) {
        // Fallback below
      }
      return false
    }

    fetch(documentUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to download file')
        }
        return response.blob()
      })
      .then(async (blob) => {
        const saved = await saveWithPicker(blob)
        if (saved) return
        // Fallback to anchor which triggers browser's default save dialog
        const blobUrl = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = blobUrl
        link.download = documentName
        link.style.display = 'none'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(blobUrl)
      })
      .catch(error => {
        console.error('Download error:', error)
      })
  }

  const handleShare = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: `Document: ${documentName}`,
          text: `Check out this document: ${documentName}`,
          url: documentUrl
        })
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(documentUrl)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }
    } catch (error) {
      console.error('Error sharing:', error)
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(documentUrl)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (clipboardError) {
        console.error('Clipboard error:', clipboardError)
      }
    }
  }

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(documentUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Error copying link:', error)
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return 'Unknown'
    }
  }

  const renderDocumentContent = () => {
    if (error) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className={`p-4 ${isDark ? "bg-red-500/20" : "bg-red-100"} rounded-full mb-4`}>
            <X className="h-8 w-8 text-red-500" />
          </div>
          <h3 className={`text-lg font-semibold mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>Error Loading Document</h3>
          <p className={`mb-4 ${isDark ? "text-gray-400" : "text-gray-600"}`}>{error}</p>
          <Button onClick={() => window.open(documentUrl, '_blank')} variant="outline">
            <ExternalLink className="h-4 w-4 mr-2" />
            Open in New Tab
          </Button>
        </div>
      )
    }

    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <p className={`${isDark ? "text-gray-400" : "text-gray-600"}`}>Loading document...</p>
        </div>
      )
    }

    // For images, show the image directly
    if (documentType && ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'].includes(documentType.toLowerCase())) {
      return (
        <div className="flex justify-center h-full">
          <img 
            src={documentUrl} 
            alt={documentName}
            className="max-w-full max-h-full object-contain rounded-lg shadow-lg"
            onLoad={() => setLoading(false)}
            onError={() => {
              setLoading(false)
              setError("Failed to load image")
            }}
          />
        </div>
      )
    }

    // For PDFs, prefer <object> to improve load handling across browsers
    if (documentType === 'pdf') {
      return (
        <div className="w-full h-full">
          <object
            data={`${documentUrl}#toolbar=1&navpanes=0&scrollbar=1`}
            type="application/pdf"
            className="w-full h-full rounded-lg"
          >
            <div className="h-full w-full flex items-center justify-center text-center p-6">
              <p className={`${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                Unable to preview PDF here.{' '}
                <button className="underline" onClick={() => window.open(documentUrl, '_blank')}>Open in a new tab</button>.
              </p>
            </div>
          </object>
        </div>
      )
    }

    // For other document types, show download option
    return (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <div className={`p-4 ${isDark ? "bg-blue-500/20" : "bg-blue-100"} rounded-full mb-4`}>
          {getDocumentIcon()}
        </div>
        <h3 className={`text-lg font-semibold mb-2 ${isDark ? "text-white" : "text-gray-900"}`}>{getDocumentTypeName()}</h3>
        <p className={`mb-4 ${isDark ? "text-gray-400" : "text-gray-600"}`}>This document type cannot be previewed directly.</p>
        <div className="flex gap-2">
          <Button onClick={handleDownload} className="bg-blue-600 hover:bg-blue-700">
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button onClick={() => window.open(documentUrl, '_blank')} variant="outline">
            <ExternalLink className="h-4 w-4 mr-2" />
            Open in New Tab
          </Button>
        </div>
      </div>
    )
  }

  const renderCandidateInfo = () => {
    if (!candidateData) return null

    return (
      <div className="space-y-4 sm:space-y-6">
        {/* Candidate Header */}
        <div className="flex items-center gap-3 sm:gap-4">
          <Avatar className="h-12 w-12 sm:h-16 sm:w-16 ring-2 ring-purple-500/20">
            <AvatarImage src="/placeholder.svg" />
            <AvatarFallback className="bg-purple-600 text-white font-medium text-sm sm:text-lg">
              {candidateData.applicantName
                .split(" ")
                .reduce((initials, name) => initials + name[0], "")}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <h2 className={`text-lg sm:text-xl font-semibold truncate ${isDark ? "text-white" : "text-gray-900"}`}>
              {candidateData.applicantName}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <Star className="h-3 w-3 sm:h-4 sm:w-4 text-purple-600" />
              <span className="text-xs sm:text-sm font-medium text-purple-600">
                {Math.floor(70 + Math.random() * 25)}% Match
              </span>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="space-y-2 sm:space-y-3">
          <h3 className={`text-sm sm:text-base font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>Contact Information</h3>
          <div className="space-y-1 sm:space-y-2">
            <div className="flex items-center gap-2 sm:gap-3">
              <User className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500 flex-shrink-0" />
              <span className={`text-xs sm:text-sm truncate ${isDark ? "text-gray-300" : "text-gray-700"}`}>
                {candidateData.email}
              </span>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <User className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500 flex-shrink-0" />
              <span className={`text-xs sm:text-sm ${isDark ? "text-gray-300" : "text-gray-700"}`}>
                {candidateData.mobile}
              </span>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <MapPin className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500 flex-shrink-0" />
              <span className={`text-xs sm:text-sm ${isDark ? "text-gray-300" : "text-gray-700"}`}>
                {candidateData.city}
              </span>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <Calendar className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500 flex-shrink-0" />
              <span className={`text-xs sm:text-sm ${isDark ? "text-gray-300" : "text-gray-700"}`}>
                Applied on {formatDate(candidateData.createdAt)}
              </span>
            </div>
          </div>
        </div>

        {/* Experience */}
        <div className="space-y-2 sm:space-y-3">
          <h3 className={`text-sm sm:text-base font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>Experience</h3>
          <div className="flex items-center gap-2 sm:gap-3">
            <Briefcase className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500 flex-shrink-0" />
            <span className={`text-xs sm:text-sm ${isDark ? "text-gray-300" : "text-gray-700"}`}>
              {candidateData.totalExperience} years
            </span>
          </div>
        </div>

        {/* Skills */}
        <div className="space-y-2 sm:space-y-3">
          <h3 className={`text-sm sm:text-base font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>Technical Skills</h3>
          <div className="flex flex-wrap gap-1 sm:gap-2">
            {(expandTechSkills ? candidateData.technicalSkills : candidateData.technicalSkills.slice(0, 6)).map((skill, index) => (
              <Badge 
                key={`tech-${index}`} 
                variant="secondary" 
                className={`rounded-2xl text-xs ${isDark ? "bg-blue-500/20 text-blue-300 border-blue-500/30" : "bg-blue-50 text-blue-700 border-blue-200"}`}
              >
                {skill}
              </Badge>
            ))}
            {candidateData.technicalSkills.length > 6 && !expandTechSkills && (
              <button
                className={`px-2 py-1 rounded-2xl border text-xs ${isDark ? "bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700" : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"}`}
                onClick={() => setExpandTechSkills(true)}
                type="button"
              >
                +{candidateData.technicalSkills.length - 6} more
              </button>
            )}
            {candidateData.technicalSkills.length > 6 && expandTechSkills && (
              <button
                className={`px-2 py-1 rounded-2xl border text-xs ${isDark ? "bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700" : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"}`}
                onClick={() => setExpandTechSkills(false)}
                type="button"
              >
                Show less
              </button>
            )}
          </div>
        </div>

        <div className="space-y-2 sm:space-y-3">
          <h3 className={`text-sm sm:text-base font-semibold ${isDark ? "text-white" : "text-gray-900"}`}>Soft Skills</h3>
          <div className="flex flex-wrap gap-1 sm:gap-2">
            {(expandSoftSkills ? candidateData.softSkills : candidateData.softSkills.slice(0, 4)).map((skill, index) => (
              <Badge 
                key={`soft-${index}`} 
                variant="secondary" 
                className={`rounded-2xl text-xs ${isDark ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" : "bg-emerald-50 text-emerald-700 border-emerald-200"}`}
              >
                {skill}
              </Badge>
            ))}
            {candidateData.softSkills.length > 4 && !expandSoftSkills && (
              <button
                className={`px-2 py-1 rounded-2xl border text-xs ${isDark ? "bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700" : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"}`}
                onClick={() => setExpandSoftSkills(true)}
                type="button"
              >
                +{candidateData.softSkills.length - 4} more
              </button>
            )}
            {candidateData.softSkills.length > 4 && expandSoftSkills && (
              <button
                className={`px-2 py-1 rounded-2xl border text-xs ${isDark ? "bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-700" : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"}`}
                onClick={() => setExpandSoftSkills(false)}
                type="button"
              >
                Show less
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-0">
      <Card className={`w-full h-full max-w-none max-h-none rounded-none overflow-hidden ${isDark ? "bg-[#111111] border-gray-800" : "bg-white border-gray-200"}`}>
        {/* Header */}
        <CardHeader className={`flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-3 sm:space-y-0 pb-4 border-b ${isDark ? "border-gray-800" : "border-gray-200"}`}>
          <div className="flex items-center gap-3 min-w-0 flex-1">
            {getDocumentIcon()}
            <div className="min-w-0 flex-1">
              <CardTitle className={`text-base sm:text-lg truncate ${isDark ? "text-white" : "text-gray-900"}`}>{documentName}</CardTitle>
              <p className={`text-xs sm:text-sm ${isDark ? "text-gray-400" : "text-gray-500"}`}>{getDocumentTypeName()}</p>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            {/* Share Button */}
            <div className="relative">
              <Button 
                onClick={handleShare} 
                variant="outline" 
                size="sm"
                className={`${isDark ? "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700" : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"}`}
              >
                <Share2 className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Share</span>
              </Button>
              {copied && (
                <div className={`absolute -top-10 left-1/2 transform -translate-x-1/2 px-2 py-1 rounded text-xs ${isDark ? "bg-gray-700 text-white" : "bg-gray-800 text-white"}`}>
                  <div className="flex items-center gap-1">
                    <Check className="h-3 w-3" />
                    Copied!
                  </div>
                </div>
              )}
            </div>
            <Button 
              onClick={handleDownload} 
              variant="outline" 
              size="sm"
              className={`${isDark ? "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700" : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"}`}
            >
              <Download className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Download</span>
            </Button>
            <Button 
              onClick={() => window.open(documentUrl, '_blank')} 
              variant="outline" 
              size="sm"
              className={`${isDark ? "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700" : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"}`}
            >
              <ExternalLink className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Open</span>
            </Button>
            <Button 
              onClick={onClose} 
              variant="outline" 
              size="sm"
              className={`${isDark ? "bg-gray-800 border-gray-700 text-gray-300 hover:bg-gray-700" : "bg-white border-gray-300 text-gray-700 hover:bg-gray-50"}`}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        
        {/* Main Content - Responsive Layout */}
        <div className="flex flex-col lg:flex-row h-[calc(100vh-120px)]">
          {/* Document Viewer - Main Content */}
          <div className="flex-1 p-3 sm:p-6 min-h-0">
            <div className={`h-full rounded-lg border-2 border-dashed ${isDark ? "border-gray-700 bg-gray-900/50" : "border-gray-300 bg-gray-50"} overflow-hidden`}>
              {renderDocumentContent()}
            </div>
          </div>
          
          {/* Candidate Info - Sidebar (Hidden on mobile, shown on desktop) */}
          <div className={`hidden lg:block lg:w-96 border-l ${isDark ? "border-gray-800 bg-[#0a0a0a]" : "border-gray-200 bg-gray-50"} p-6 overflow-y-auto`}>
            <div className="sticky top-0">
              <h3 className={`text-lg font-semibold mb-4 ${isDark ? "text-white" : "text-gray-900"}`}>
                Candidate Information
              </h3>
            </div>
            {renderCandidateInfo()}
          </div>
        </div>
      </Card>
    </div>
  )
}
