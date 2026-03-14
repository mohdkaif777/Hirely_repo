import { cn } from "@/lib/utils";
import { Trophy, Medal, Award } from "lucide-react";

export function RankBadge({ rank, className }: { rank: number; className?: string }) {
  if (rank === 0) return null; // No rank
  
  const getRankConfig = () => {
    switch(rank) {
      case 1: 
        return { 
          icon: Trophy, 
          color: "text-amber-400", 
          bg: "bg-amber-400/10 border-amber-400/20 shadow-[0_0_10px_rgba(251,191,36,0.15)]",
          label: "Top Match" 
        };
      case 2: 
        return { 
          icon: Medal, 
          color: "text-slate-300", 
          bg: "bg-slate-300/10 border-slate-300/20 shadow-none",
          label: "2nd Best" 
        };
      case 3: 
        return { 
          icon: Award, 
          color: "text-amber-600", 
          bg: "bg-amber-600/10 border-amber-600/20 shadow-none",
          label: "3rd Best" 
        };
      default:
        return { 
          icon: null, 
          color: "text-muted-foreground", 
          bg: "bg-secondary/50 border-border/50 shadow-none",
          label: `Rank #${rank}` 
        };
    }
  };

  const config = getRankConfig();
  const Icon = config.icon;

  return (
    <div className={cn(
      "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm transition-all",
      config.bg,
      config.color,
      className
    )}>
      {Icon && <Icon className="w-3.5 h-3.5" />}
      {config.label}
    </div>
  );
}
