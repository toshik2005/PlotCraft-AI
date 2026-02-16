"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, Brain, Filter, MapPin, Briefcase, Star, Zap, Target, TrendingUp, Users, Sparkles } from "lucide-react"

interface SearchFilters {
  query: string
  location: string
  experience: [number, number]
  skills: string[]
  education: string[]
  availability: string
  salaryRange: [number, number]
  aiMatch: boolean
  semanticSearch: boolean
}

interface SearchResult {
  id: string
  name: string
  title: string
  location: string
  experience: number
  skills: string[]
  matchScore: number
  aiInsights: string[]
  availability: string
  lastActive: string
  profileStrength: number
}

export function AdvancedSearch() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: "",
    location: "",
    experience: [0, 15],
    skills: [],
    education: [],
    availability: "any",
    salaryRange: [50, 200],
    aiMatch: true,
    semanticSearch: true,
  })

  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [searchMode, setSearchMode] = useState<"basic" | "advanced" | "ai">("ai")

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
    "PostgreSQL",
    "Redis",
    "Microservices",
    "Machine Learning",
    "Data Science",
    "DevOps",
    "CI/CD",
    "Terraform",
  ]

  const educationLevels = [
    "High School",
    "Associate Degree",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Bootcamp",
    "Self-taught",
  ]

  const mockResults: SearchResult[] = [
    {
      id: "1",
      name: "Sarah Chen",
      title: "Senior React Developer",
      location: "San Francisco, CA",
      experience: 6,
      skills: ["React", "TypeScript", "Node.js", "AWS"],
      matchScore: 94,
      aiInsights: ["Perfect technical fit", "Strong leadership potential", "Cultural alignment"],
      availability: "Available",
      lastActive: "2 hours ago",
      profileStrength: 92,
    },
    {
      id: "2",
      name: "Marcus Johnson",
      title: "Full Stack Engineer",
      location: "New York, NY",
      experience: 4,
      skills: ["JavaScript", "Python", "Docker", "PostgreSQL"],
      matchScore: 87,
      aiInsights: ["Versatile skill set", "Fast learner", "Team player"],
      availability: "Open to offers",
      lastActive: "1 day ago",
      profileStrength: 85,
    },
    {
      id: "3",
      name: "Elena Rodriguez",
      title: "DevOps Engineer",
      location: "Austin, TX",
      experience: 8,
      skills: ["AWS", "Kubernetes", "Terraform", "Python"],
      matchScore: 91,
      aiInsights: ["Infrastructure expert", "Automation specialist", "Scalability focus"],
      availability: "Available",
      lastActive: "30 minutes ago",
      profileStrength: 89,
    },
  ]

  const handleSearch = async () => {
    setIsSearching(true)

    // Simulate AI search processing
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setSearchResults(mockResults)
    setIsSearching(false)
  }

  const addSkill = (skill: string) => {
    if (!filters.skills.includes(skill)) {
      setFilters((prev) => ({ ...prev, skills: [...prev.skills, skill] }))
    }
  }

  const removeSkill = (skill: string) => {
    setFilters((prev) => ({ ...prev, skills: prev.skills.filter((s) => s !== skill) }))
  }

  const getMatchColor = (score: number) => {
    if (score >= 90) return "text-green-500"
    if (score >= 80) return "text-blue-500"
    if (score >= 70) return "text-yellow-500"
    return "text-gray-500"
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Search Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl lg:text-5xl font-bold text-balance">
          AI-Powered{" "}
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Talent Search</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
          Find the perfect candidates using semantic search and AI-powered matching algorithms
        </p>
      </div>

      {/* Search Mode Tabs */}
      <Tabs value={searchMode} onValueChange={(value) => setSearchMode(value as any)} className="w-full">
        <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
          <TabsTrigger value="basic">Basic</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
          <TabsTrigger value="ai">AI Search</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search for candidates by role, skills, or company..."
                    value={filters.query}
                    onChange={(e) => setFilters((prev) => ({ ...prev, query: e.target.value }))}
                    className="text-lg h-12"
                  />
                </div>
                <Button onClick={handleSearch} size="lg" disabled={isSearching}>
                  {isSearching ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      Searching...
                    </div>
                  ) : (
                    <>
                      <Search className="w-5 h-5 mr-2" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Filter className="w-5 h-5" />
                    Advanced Filters
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Location</label>
                    <Input
                      placeholder="City, State, or Remote"
                      value={filters.location}
                      onChange={(e) => setFilters((prev) => ({ ...prev, location: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium">Experience Range</label>
                    <Slider
                      value={filters.experience}
                      onValueChange={(value) =>
                        setFilters((prev) => ({ ...prev, experience: value as [number, number] }))
                      }
                      max={15}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>{filters.experience[0]} years</span>
                      <span>{filters.experience[1]}+ years</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium">Required Skills</label>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {filters.skills.map((skill) => (
                        <Badge
                          key={skill}
                          variant="default"
                          className="cursor-pointer"
                          onClick={() => removeSkill(skill)}
                        >
                          {skill} ×
                        </Badge>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {availableSkills
                        .filter((skill) => !filters.skills.includes(skill))
                        .map((skill) => (
                          <Button
                            key={skill}
                            variant="outline"
                            size="sm"
                            onClick={() => addSkill(skill)}
                            className="text-xs h-7"
                          >
                            {skill}
                          </Button>
                        ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-sm font-medium">Salary Range (K)</label>
                    <Slider
                      value={filters.salaryRange}
                      onValueChange={(value) =>
                        setFilters((prev) => ({ ...prev, salaryRange: value as [number, number] }))
                      }
                      min={30}
                      max={300}
                      step={10}
                      className="w-full"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>${filters.salaryRange[0]}K</span>
                      <span>${filters.salaryRange[1]}K+</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="lg:col-span-2">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex gap-4 mb-6">
                    <div className="flex-1">
                      <Input
                        placeholder="Describe your ideal candidate..."
                        value={filters.query}
                        onChange={(e) => setFilters((prev) => ({ ...prev, query: e.target.value }))}
                        className="text-lg h-12"
                      />
                    </div>
                    <Button onClick={handleSearch} size="lg" disabled={isSearching}>
                      {isSearching ? (
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                          Searching...
                        </div>
                      ) : (
                        <>
                          <Search className="w-5 h-5 mr-2" />
                          Search
                        </>
                      )}
                    </Button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={filters.aiMatch}
                          onCheckedChange={(checked) => setFilters((prev) => ({ ...prev, aiMatch: checked }))}
                        />
                        <label className="text-sm">AI Matching</label>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={filters.semanticSearch}
                          onCheckedChange={(checked) => setFilters((prev) => ({ ...prev, semanticSearch: checked }))}
                        />
                        <label className="text-sm">Semantic Search</label>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                AI-Powered Semantic Search
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Describe what you're looking for in natural language..."
                    value={filters.query}
                    onChange={(e) => setFilters((prev) => ({ ...prev, query: e.target.value }))}
                    className="text-lg h-12"
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    Example: "Senior developer with React experience who can lead a team and has worked at startups"
                  </p>
                </div>
                <Button
                  onClick={handleSearch}
                  size="lg"
                  disabled={isSearching}
                  className="bg-primary hover:bg-primary/90"
                >
                  {isSearching ? (
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-5 h-5 animate-pulse" />
                      AI Searching...
                    </div>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      AI Search
                    </>
                  )}
                </Button>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 bg-primary/5 rounded-lg border border-primary/20">
                  <Brain className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Semantic Understanding</p>
                    <p className="text-xs text-muted-foreground">Understands context and intent</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-accent/5 rounded-lg border border-accent/20">
                  <Target className="w-5 h-5 text-accent" />
                  <div>
                    <p className="text-sm font-medium">Smart Matching</p>
                    <p className="text-xs text-muted-foreground">Finds relevant candidates</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-green-500/5 rounded-lg border border-green-500/20">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-sm font-medium">Ranked Results</p>
                    <p className="text-xs text-muted-foreground">Sorted by relevance</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Search Results */}
      <AnimatePresence>
        {searchResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Search Results ({searchResults.length})</h2>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Refine
                </Button>
                <Button variant="outline" size="sm">
                  Export
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover:border-primary/50 transition-colors">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="space-y-2">
                          <div className="flex items-center gap-3">
                            <h3 className="text-xl font-semibold">{result.name}</h3>
                            <Badge variant="outline" className="text-xs">
                              {result.availability}
                            </Badge>
                          </div>
                          <p className="text-lg text-muted-foreground">{result.title}</p>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {result.location}
                            </div>
                            <div className="flex items-center gap-1">
                              <Briefcase className="w-4 h-4" />
                              {result.experience} years
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              {result.lastActive}
                            </div>
                          </div>
                        </div>
                        <div className="text-right space-y-2">
                          <div className={`text-3xl font-bold ${getMatchColor(result.matchScore)}`}>
                            {result.matchScore}%
                          </div>
                          <p className="text-sm text-muted-foreground">Match Score</p>
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="text-sm">{result.profileStrength}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <p className="text-sm font-medium mb-2">Skills</p>
                          <div className="flex flex-wrap gap-2">
                            {result.skills.map((skill) => (
                              <Badge key={skill} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div>
                          <p className="text-sm font-medium mb-2">AI Insights</p>
                          <div className="flex flex-wrap gap-2">
                            {result.aiInsights.map((insight, i) => (
                              <div
                                key={i}
                                className="flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded-md text-xs"
                              >
                                <Zap className="w-3 h-3" />
                                {insight}
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex gap-2 pt-2">
                          <Button size="sm">View Profile</Button>
                          <Button size="sm" variant="outline">
                            Contact
                          </Button>
                          <Button size="sm" variant="outline">
                            Save
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {isSearching && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <Brain className="w-8 h-8 text-primary animate-pulse" />
          </div>
          <h3 className="text-xl font-semibold mb-2">AI is searching...</h3>
          <p className="text-muted-foreground">Analyzing candidate profiles and matching requirements</p>
        </motion.div>
      )}
    </div>
  )
}
