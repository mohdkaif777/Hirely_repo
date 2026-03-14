"use client";

import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { Bell, Search, Menu, LogOut } from "lucide-react";
import { usePathname } from "next/navigation";

export function Navbar() {
  const { logout, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  function handleLogout() {
    logout();
    router.push("/");
  }

  // A helper to format the page title from the URL
  const getPageTitle = () => {
    if (pathname === "/dashboard") return "Dashboard";
    const segment = pathname?.split("/").pop();
    if (!segment) return "";
    return segment.charAt(0).toUpperCase() + segment.slice(1).replace("-", " ");
  };

  return (
    <header className="h-16 border-b border-border/50 bg-background/60 backdrop-blur-xl sticky top-0 z-40 flex items-center justify-between px-4 sm:px-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="md:hidden text-muted-foreground hover:text-foreground">
          <Menu className="w-5 h-5" />
        </Button>
        <h1 className="text-lg font-semibold text-foreground hidden sm:block tracking-tight">
          {getPageTitle()}
        </h1>
      </div>
      
      <div className="flex items-center gap-4 sm:gap-6">
        <div className="relative hidden lg:block group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          <input
            type="text"
            placeholder="Search anywhere..."
            className="h-9 w-64 rounded-full border border-border/50 bg-secondary/30 pl-10 pr-4 text-sm outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 focus:bg-secondary/80 transition-all placeholder:text-muted-foreground/70"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex gap-1">
            <kbd className="hidden sm:inline-flex h-5 items-center gap-1 rounded border border-border/50 bg-background/50 px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <span className="text-xs">⌘</span>K
            </kbd>
          </div>
        </div>
        <Button variant="ghost" size="icon" className="rounded-full text-muted-foreground hover:text-foreground hover:bg-secondary relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary border-2 border-background"></span>
        </Button>
        <div className="h-6 w-px bg-border/50 hidden sm:block"></div>
        <Button 
          variant="ghost" 
          onClick={handleLogout} 
          className="rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 hidden sm:flex items-center gap-2 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span className="text-sm font-medium">Log out</span>
        </Button>
      </div>
    </header>
  );
}
