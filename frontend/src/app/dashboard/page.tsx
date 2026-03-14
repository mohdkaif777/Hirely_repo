"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getMyJobs, getConversations } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Briefcase, MessageSquare, Users, CheckCircle2 } from "lucide-react";
import { SkeletonCard } from "@/components/ui/SkeletonCard";
import Link from "next/link";
import { JobCard } from "@/components/ui/JobCard";

export default function DashboardPage() {
  const { user, token, loading } = useAuth();
  const [stats, setStats] = useState({ jobs: 0, activeMatches: 0, screening: 0, scheduled: 0 });
  const [recentItems, setRecentItems] = useState<any[]>([]);
  const [dataLoading, setDataLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      if (!token || !user) return;
      try {
        if (user.role === "recruiter") {
          const [jobsData, convData] = await Promise.all([
            getMyJobs(token).catch(() => ({ jobs: [] })),
            getConversations(token).catch(() => [])
          ]);
          
          const jobsList = jobsData.jobs || [];
          const convs = convData || [];
          
          const activeMatches = convs.filter((c: any) => c.agent_status !== 'rejected').length;
          const screening = convs.filter((c: any) => c.agent_status === 'screening').length;
          const scheduled = convs.filter((c: any) => c.agent_status === 'interview_scheduled').length;

          setStats({
            jobs: jobsList.length,
            activeMatches,
            screening,
            scheduled
          });
          
          setRecentItems(jobsList.slice(0, 3));
        } else if (user.role === "job_seeker") {
          const convData = await getConversations(token).catch(() => []);
          const convs = convData || [];
          
          setStats({
            jobs: 0, // Not applicable
            activeMatches: convs.length,
            screening: convs.filter((c: any) => c.agent_status === 'screening').length,
            scheduled: convs.filter((c: any) => c.agent_status === 'interview_scheduled').length,
          });
        }
      } catch (err) {
        console.error("Dashboard loading error", err);
      } finally {
        setDataLoading(false);
      }
    }
    
    if (!loading) loadDashboard();
  }, [user, token, loading]);

  if (loading || dataLoading) {
    return (
      <div className="space-y-6">
        <div>
          <div className="h-8 w-48 bg-secondary/50 rounded-md animate-pulse mb-2"></div>
          <div className="h-4 w-72 bg-secondary/30 rounded-md animate-pulse"></div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <SkeletonCard key={i} className="h-28" />)}
        </div>
      </div>
    );
  }

  const StatBox = ({ title, value, icon: Icon, trend }: any) => (
    <Card className="rounded-2xl border-border/50 bg-card/60 backdrop-blur-sm shadow-sm md:hover:-translate-y-1 transition-transform group">
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{title}</p>
            <p className="text-3xl font-bold tracking-tight text-foreground">{value}</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
            <Icon className="w-5 h-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          {user?.role === "recruiter" 
            ? "Track your hiring pipeline and top candidates." 
            : "Track your active applications and interview statuses."}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
        {user?.role === "recruiter" && (
          <StatBox title="Active Jobs" value={stats.jobs} icon={Briefcase} />
        )}
        <StatBox title="Active Matches" value={stats.activeMatches} icon={Users} />
        <StatBox title="In Screening" value={stats.screening} icon={MessageSquare} />
        <StatBox title="Interviews Set" value={stats.scheduled} icon={CheckCircle2} />
      </div>

      {user?.role === "recruiter" && recentItems.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-border/50">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold tracking-tight">Recent Job Postings</h2>
            <Link href="/dashboard/my-jobs" className="text-sm font-medium text-primary hover:text-primary/80 transition-colors">
              View all
            </Link>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {recentItems.map((job) => (
              <JobCard 
                key={job.id} 
                job={job} 
              />
            ))}
          </div>
        </div>
      )}
      
      {user?.role === "job_seeker" && (
        <div className="space-y-4 pt-4 border-t border-border/50">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold tracking-tight">Find Opportunities</h2>
            <Link href="/dashboard/jobs" className="text-sm font-medium text-primary hover:text-primary/80 transition-colors">
              Browse jobs
            </Link>
          </div>
          <Card className="rounded-2xl border-dashed border-border/60 bg-secondary/10 p-8 text-center backdrop-blur-sm">
            <Briefcase className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-bold mb-2">Ready for your next role?</h3>
            <p className="text-muted-foreground text-sm max-w-sm mx-auto mb-6">
              Our AI is constantly finding the best matches for your skills and experience.
            </p>
            <Link href="/dashboard/jobs" className="inline-flex h-10 items-center justify-center rounded-xl bg-primary px-6 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
              View Recommended Jobs
            </Link>
          </Card>
        </div>
      )}
    </div>
  );
}
