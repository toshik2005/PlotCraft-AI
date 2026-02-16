"use client";
import Link from "next/link";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FileText,
  Folder,
  Heart,
  PlusCircle,
  ChevronDown,
  Badge,
} from "lucide-react";

export function NavbarLeft() {
  const [assetsOpen, setAssetsOpen] = useState(true);
  return (
    <aside className="fixed left-0 top-0 z-40 h-full w-[250px] bg-sidebar dark:bg-sidebar border-r border-sidebar-border flex flex-col px-4 py-6 gap-6 min-h-screen shadow-sm">
      {/* Logo */}
      <div className="flex items-center gap-2 mb-8 pl-1">
        <Badge className="w-7 h-7 text-primary" />
        <span className="font-bold text-2xl tracking-tight text-primary">Recruitr</span>
      </div>
      {/* Search */}
      <div className="mb-2">
        <Input placeholder="Search..." className="bg-muted rounded-lg px-3 py-2 text-sm" />
      </div>
      {/* Main Navigation */}
      <nav className="flex flex-col gap-1">
        <Link href="/explore" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
          <LayoutDashboard className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" />
          Explore
        </Link>
        <Link href="/candidates" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
          <Users className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" />
          Candidates
        </Link>
        <Link href="/jobs" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
          <Briefcase className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" />
          Jobs
        </Link>
        <Link href="/assessments" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
          <FileText className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" />
          Assessments
        </Link>
        {/* Assets Dropdown */}
        <button
          className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground w-full justify-between group"
          onClick={() => setAssetsOpen((v) => !v)}
          aria-expanded={assetsOpen}
        >
          <span className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" /> Assets
          </span>
          <span className="inline-flex items-center justify-center text-xs bg-muted px-2 py-0.5 rounded-full ml-2 font-semibold text-foreground">112</span>
          <ChevronDown className={`ml-2 w-4 h-4 transition-transform text-muted-foreground ${assetsOpen ? "rotate-180" : "rotate-0"}`} />
        </button>
        {assetsOpen && (
          <div className="ml-8 mt-1 flex flex-col gap-1">
            <Link href="/assets/designs" className="text-sm text-muted-foreground hover:text-foreground py-1">Designs</Link>
            <Link href="/assets/animations" className="text-sm text-muted-foreground hover:text-foreground py-1">Animations</Link>
          </div>
        )}
        <Link href="/likes" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
          <Heart className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" />
          Likes
        </Link>
      </nav>
      {/* Scenes/Folders */}
      <div className="mt-8">
        <div className="text-xs font-semibold text-muted-foreground mb-2 pl-1 tracking-wide">Folders</div>
        <div className="flex flex-col gap-1">
          <Button variant="ghost" size="sm" className="justify-start gap-2 text-base px-2 py-2 rounded-lg font-medium text-muted-foreground hover:bg-accent/60">
            <PlusCircle className="w-5 h-5 text-primary" /> New Folder
          </Button>
          <Link href="/scenes" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-muted-foreground group">
            <Folder className="w-5 h-5 text-primary group-hover:text-foreground transition-colors" /> My Scenes
          </Link>
          <Link href="/folders/untitled" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-orange-600 group">
            <Folder className="w-5 h-5 text-orange-600 group-hover:text-foreground transition-colors" /> Untitled Folder
          </Link>
          <Link href="/folders/3d-icons" className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent/60 transition-colors text-base font-medium text-green-700 group">
            <Folder className="w-5 h-5 text-green-700 group-hover:text-foreground transition-colors" /> 3D Icons
          </Link>
        </div>
      </div>
    </aside>
  );
}

export default NavbarLeft; 