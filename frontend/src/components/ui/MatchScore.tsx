import { cn } from "@/lib/utils";

export function MatchScore({ score, size = "md", className }: { score: number; size?: "sm" | "md" | "lg"; className?: string }) {
  const percentage = Math.round(score * 100);
  
  let colorClass = "text-emerald-400";
  let bgClass = "bg-emerald-400/10";
  let borderClass = "border-emerald-400/20";
  let glowClass = "shadow-[0_0_15px_rgba(52,211,153,0.15)]";
  
  if (percentage < 50) {
    colorClass = "text-destructive";
    bgClass = "bg-destructive/10";
    borderClass = "border-destructive/20";
    glowClass = "shadow-none";
  } else if (percentage < 75) {
    colorClass = "text-amber-400";
    bgClass = "bg-amber-400/10";
    borderClass = "border-amber-400/20";
    glowClass = "shadow-[0_0_15px_rgba(251,191,36,0.1)]";
  }

  const sizes = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
    lg: "px-3 py-1.5 text-sm"
  };

  return (
    <div className={cn(
      "inline-flex items-center justify-center font-bold rounded-full border backdrop-blur-sm transition-all",
      bgClass,
      colorClass,
      borderClass,
      glowClass,
      sizes[size],
      className
    )}>
      {percentage}% Match
    </div>
  );
}
