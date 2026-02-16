"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, X } from "lucide-react"

interface FilterProps {
  onFilterChange: (filters: any) => void
}

export function DashboardFilters({ onFilterChange }: FilterProps) {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [statusFilter, setStatusFilter] = useState("all")
  const [experienceFilter, setExperienceFilter] = useState("all")

  const availableSkills = [
    "JavaScript",
    "React",
    "Node.js",
    "Python",
    "AWS",
    "TypeScript",
    "Docker",
    "Kubernetes",
    "GraphQL",
    "MongoDB",
  ]

  const addSkill = (skill: string) => {
    if (!selectedSkills.includes(skill)) {
      const newSkills = [...selectedSkills, skill]
      setSelectedSkills(newSkills)
      onFilterChange({ searchTerm, skills: newSkills, status: statusFilter, experience: experienceFilter })
    }
  }

  const removeSkill = (skill: string) => {
    const newSkills = selectedSkills.filter((s) => s !== skill)
    setSelectedSkills(newSkills)
    onFilterChange({ searchTerm, skills: newSkills, status: statusFilter, experience: experienceFilter })
  }

  const handleSearchChange = (value: string) => {
    setSearchTerm(value)
    onFilterChange({ searchTerm: value, skills: selectedSkills, status: statusFilter, experience: experienceFilter })
  }

  return (
    <div className="space-y-4 mb-8">
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search candidates by name, title, or skills..."
            value={searchTerm}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="new">New</SelectItem>
              <SelectItem value="reviewed">Reviewed</SelectItem>
              <SelectItem value="shortlisted">Shortlisted</SelectItem>
              <SelectItem value="interviewed">Interviewed</SelectItem>
            </SelectContent>
          </Select>

          <Select value={experienceFilter} onValueChange={setExperienceFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Experience" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="junior">0-2 years</SelectItem>
              <SelectItem value="mid">3-5 years</SelectItem>
              <SelectItem value="senior">5+ years</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="icon">
            <Filter className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">Filter by Skills</p>
        <div className="flex flex-wrap gap-2">
          {availableSkills.map((skill) => (
            <Button
              key={skill}
              variant={selectedSkills.includes(skill) ? "default" : "outline"}
              size="sm"
              onClick={() => (selectedSkills.includes(skill) ? removeSkill(skill) : addSkill(skill))}
              className="text-xs"
            >
              {skill}
              {selectedSkills.includes(skill) && <X className="w-3 h-3 ml-1" />}
            </Button>
          ))}
        </div>
      </div>

      {(selectedSkills.length > 0 || statusFilter !== "all" || experienceFilter !== "all") && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {selectedSkills.map((skill) => (
            <Badge key={skill} variant="secondary" className="text-xs">
              {skill}
              <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => removeSkill(skill)} />
            </Badge>
          ))}
          {statusFilter !== "all" && (
            <Badge variant="secondary" className="text-xs">
              Status: {statusFilter}
            </Badge>
          )}
          {experienceFilter !== "all" && (
            <Badge variant="secondary" className="text-xs">
              Experience: {experienceFilter}
            </Badge>
          )}
        </div>
      )}
    </div>
  )
}
