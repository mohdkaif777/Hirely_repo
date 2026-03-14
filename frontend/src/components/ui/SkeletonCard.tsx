import { cn } from "@/lib/utils";

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("p-6 rounded-2xl border border-border/50 bg-card shadow-sm animate-pulse mb-4", className)}>
      <div className="flex items-start justify-between mb-4">
        <div className="space-y-3 flex-1">
          <div className="h-5 bg-secondary/80 rounded-md w-1/3"></div>
          <div className="h-4 bg-secondary/80 rounded-md w-1/4"></div>
        </div>
        <div className="h-8 w-20 bg-secondary/80 rounded-lg"></div>
      </div>
      <div className="space-y-3 mt-6">
        <div className="h-4 bg-secondary/80 rounded-md w-full"></div>
        <div className="h-4 bg-secondary/80 rounded-md w-5/6"></div>
      </div>
      <div className="mt-6 flex gap-3">
        <div className="h-6 w-16 bg-secondary/80 flex-shrink-0 rounded-full"></div>
        <div className="h-6 w-20 bg-secondary/80 flex-shrink-0 rounded-full"></div>
      </div>
    </div>
  );
}
