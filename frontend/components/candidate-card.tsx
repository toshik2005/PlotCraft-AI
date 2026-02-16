"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MapPin, Mail, Phone, Calendar, Star, Eye, MessageSquare, ChevronDown, ChevronUp, Check } from "lucide-react"

interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  location: string
  title: string
  experience: string
  skills: string[]
  rating: number
  avatar?: string
  uploadDate: string
  status: "new" | "reviewed" | "shortlisted" | "interviewed"
  summary: string
  aiScore?: number
  aiReason?: string
}

interface CandidateCardProps {
  candidate: Candidate
  onView: (id: string) => void
  onContact: (id: string) => void
  isSelected?: boolean
  onToggleSelection?: () => void
}

export function CandidateCard({ candidate, onView, onContact, isSelected = false, onToggleSelection }: CandidateCardProps) {
  const [showAllSkills, setShowAllSkills] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "new":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20"
      case "reviewed":
        return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
      case "shortlisted":
        return "bg-green-500/10 text-green-500 border-green-500/20"
      case "interviewed":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20"
      default:
        return "bg-gray-500/10 text-gray-500 border-gray-500/20"
    }
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
  }

  const toggleSkills = () => {
    setShowAllSkills(!showAllSkills)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.3 }}
      className="h-full"
    >
      <Card className={`h-full hover:border-primary/50 transition-all duration-200 flex flex-col ${
        isSelected 
          ? 'ring-2 ring-primary/30 border-primary/40 shadow-lg shadow-primary/10' 
          : 'hover:shadow-md'
      }`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <Avatar className="w-14 h-14">
                <AvatarImage src={candidate.avatar || "/placeholder.svg"} alt={candidate.name} />
                <AvatarFallback className="bg-primary/10 text-primary font-semibold text-lg">
                  {getInitials(candidate.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className="font-bold text-lg leading-tight">{candidate.name}</h3>
                <p className="text-sm font-medium text-primary">{candidate.title}</p>
                <div className="flex items-center gap-3 mt-1">
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <MapPin className="w-3 h-3" />
                    {candidate.location}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    {candidate.experience}y exp
                  </div>
                </div>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              {onToggleSelection && (
                <button
                  onClick={onToggleSelection}
                  className={`w-7 h-7 rounded-lg border-2 flex items-center justify-center transition-all duration-200 shadow-sm hover:shadow-md ${
                    isSelected 
                      ? 'bg-primary border-primary text-white shadow-primary/25' 
                      : 'border-gray-300 hover:border-primary/50 hover:bg-primary/5'
                  }`}
                >
                  {isSelected && <Check className="w-4 h-4" />}
                </button>
              )}
              {candidate.aiScore && (
                <div className="flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                  <span className="text-xs font-bold">AI: {candidate.aiScore}%</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-semibold">{candidate.rating}</span>
                </div>
                <Badge className={`${getStatusColor(candidate.status)} text-xs px-2 py-1`}>
                  {candidate.status}
                </Badge>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-3 flex-1 flex flex-col">
          {candidate.aiReason && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
              <p className="text-xs text-blue-700 font-medium mb-1">AI Match:</p>
              <p className="text-xs text-blue-600 line-clamp-2">{candidate.aiReason}</p>
            </div>
          )}
          
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-sm text-gray-700 line-clamp-2 leading-relaxed">{candidate.summary}</p>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Mail className="w-3 h-3" />
              <span className="truncate">{candidate.email}</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <Phone className="w-3 h-3" />
              <span className="truncate">{candidate.phone}</span>
            </div>
          </div>

          <div className="space-y-2 flex-1">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold">Skills</p>
                <span className="text-xs text-muted-foreground bg-gray-100 px-2 py-1 rounded-full">
                  {candidate.skills.length}
                </span>
              </div>
              {candidate.skills.length > 4 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSkills}
                  className="h-6 px-2 text-xs text-primary hover:text-primary/80"
                >
                  {showAllSkills ? (
                    <>
                      <ChevronUp className="w-3 h-3 mr-1" />
                      Less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-3 h-3 mr-1" />
                      All
                    </>
                  )}
                </Button>
              )}
            </div>
            <div className="flex flex-wrap gap-1 min-h-[50px]">
              {showAllSkills ? (
                candidate.skills.map((skill, index) => (
                  <Badge key={index} variant="secondary" className="text-xs px-2 py-1 font-medium">
                    {skill}
                  </Badge>
                ))
              ) : (
                <>
                  {candidate.skills.slice(0, 4).map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs px-2 py-1 font-medium">
                      {skill}
                    </Badge>
                  ))}
                  {candidate.skills.length > 4 && (
                    <Badge 
                      variant="outline" 
                      className="text-xs cursor-pointer hover:bg-primary/10 hover:text-primary transition-colors px-2 py-1 font-medium"
                      onClick={toggleSkills}
                    >
                      +{candidate.skills.length - 4}
                    </Badge>
                  )}
                </>
              )}
            </div>
          </div>

          <div className="flex gap-2 pt-2 mt-auto">
            <Button size="sm" onClick={() => onView(candidate.id)} className="flex-1 bg-primary hover:bg-primary/90">
              <Eye className="w-4 h-4 mr-2" />
              View Profile
            </Button>
            <Button size="sm" variant="outline" onClick={() => onContact(candidate.id)} className="hover:bg-primary/5">
              <MessageSquare className="w-4 h-4 mr-1" />
              Contact
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
