"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";
import {
  Briefcase,
  MessageSquare,
  User,
  LayoutDashboard,
  Building2,
} from "lucide-react";

export function Sidebar() {
  const { user } = useAuth();
  const pathname = usePathname();

  if (!user) return null;

  const recruiterLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "My Jobs", href: "/dashboard/my-jobs", icon: Briefcase },
    { name: "Post Job", href: "/dashboard/post-job", icon: Building2 },
    { name: "Inbox", href: "/dashboard/inbox", icon: MessageSquare },
    { name: "Company", href: "/dashboard/company", icon: Building2 },
  ];

  const seekerLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Browse Jobs", href: "/dashboard/jobs", icon: Briefcase },
    { name: "Inbox", href: "/dashboard/inbox", icon: MessageSquare },
    { name: "My Profile", href: "/dashboard/profile", icon: User },
  ];

  const links = user.role === "recruiter" ? recruiterLinks : seekerLinks;

  return (
    <div className="w-64 border-r border-border bg-card hidden md:flex flex-col h-full transition-all duration-300">
      <div className="h-16 flex items-center px-6 border-b border-border/50">
        <Link href="/" className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <div className="w-7 h-7 rounded-xl bg-primary flex items-center justify-center shadow-sm shadow-primary/20">
            <span className="text-primary-foreground text-sm font-black">H</span>
          </div>
          Hire<span className="text-primary">AI</span>
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto py-6 px-3 space-y-1 scrollbar-hide">
        <div className="mb-4 px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Menu
        </div>
        {links.map((link) => {
          // Exact match or sub-route match (e.g. /dashboard/inbox/123)
          const isActive = pathname === link.href || (pathname !== "/dashboard" && pathname?.startsWith(link.href));
          return (
            <Link
              key={link.name}
              href={link.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group",
                isActive
                  ? "bg-primary/10 text-primary ring-1 ring-primary/20"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <link.icon className={cn("w-4 h-4 transition-colors", isActive ? "text-primary" : "text-muted-foreground group-hover:text-foreground")} />
              {link.name}
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-border/50">
        <div className="flex items-center gap-3 p-2 rounded-xl hover:bg-secondary transition-colors cursor-pointer border border-transparent hover:border-border/50">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-medium text-primary shadow-inner">
            {user.email?.[0].toUpperCase()}
          </div>
          <div className="flex flex-col text-sm overflow-hidden">
            <span className="truncate font-medium text-foreground">{user.email}</span>
            <span className="truncate text-xs text-muted-foreground capitalize">{user.role?.replace('_', ' ')}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
