import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, Briefcase, Users, Send } from "lucide-react";

export type Job = {
  id: string;
  title: string;
  description: string;
  skills_required: string[];
  salary_range: string;
  experience_required: string;
  location: string;
  number_of_vacancies: number;
  confirmed_candidates?: number;
  waiting_candidates?: number;
  created_at?: string;
};

interface JobCardProps {
  job: Job;
  onAction?: (jobId: string) => void;
  actionLabel?: string;
  actionIcon?: React.ReactNode;
}

export function JobCard({ job, onAction, actionLabel = "Apply", actionIcon = <Send className="w-4 h-4 mr-2" /> }: JobCardProps) {
  return (
    <Card className="flex flex-col rounded-2xl border border-border/50 bg-card/50 backdrop-blur-sm transition-all hover:shadow-lg hover:shadow-primary/5 hover:border-border group min-h-[300px]">
      <CardHeader className="pb-4">
        <div className="flex justify-between items-start gap-4">
          <div>
            <CardTitle className="line-clamp-2 text-lg font-semibold tracking-tight group-hover:text-primary transition-colors">
              {job.title}
            </CardTitle>
            <div className="flex flex-wrap items-center gap-3 mt-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" />
                {job.location || "Remote"}
              </div>
              <div className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5" />
                {job.experience_required || "Entry Level"}
              </div>
              <div className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5" />
                {job.number_of_vacancies || 1} Vacanc{job.number_of_vacancies === 1 ? 'y' : 'ies'}
              </div>
            </div>
          </div>
          {job.salary_range && (
            <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20 whitespace-nowrap border border-emerald-500/20">
              {job.salary_range}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 pb-4 flex flex-col justify-between">
        <div>
          <p className="text-sm text-muted-foreground line-clamp-3 leading-relaxed mb-6">
            {job.description}
          </p>
          <div className="flex flex-wrap gap-1.5">
            {job.skills_required.slice(0, 4).map((skill) => (
              <Badge key={skill} variant="outline" className="rounded-md border-border/50 text-xs font-medium text-foreground/80 bg-secondary/20">
                {skill}
              </Badge>
            ))}
            {job.skills_required.length > 4 && (
              <Badge variant="outline" className="rounded-md border-border/50 text-xs font-medium text-muted-foreground bg-transparent">
                +{job.skills_required.length - 4}
              </Badge>
            )}
          </div>
        </div>

        {job.confirmed_candidates !== undefined && (
          <div className="mt-6 pt-4 border-t border-border/50 grid grid-cols-3 gap-2 text-center">
            <div className="bg-secondary/30 rounded-lg p-2 flex flex-col items-center justify-center">
              <div className="text-[10px] uppercase font-semibold text-muted-foreground mb-0.5">Vacancies</div>
              <div className="text-lg font-bold tracking-tight text-foreground">{job.number_of_vacancies}</div>
            </div>
            <div className="bg-emerald-400/10 rounded-lg p-2 flex flex-col items-center justify-center border border-emerald-400/10">
              <div className="text-[10px] uppercase font-semibold text-emerald-400 mb-0.5">Confirmed</div>
              <div className="text-lg font-bold tracking-tight text-emerald-400">{job.confirmed_candidates}</div>
            </div>
            <div className="bg-amber-400/10 rounded-lg p-2 flex flex-col items-center justify-center border border-amber-400/10">
              <div className="text-[10px] uppercase font-semibold text-amber-400 mb-0.5">Waiting</div>
              <div className="text-lg font-bold tracking-tight text-amber-400">{job.waiting_candidates}</div>
            </div>
          </div>
        )}
      </CardContent>
      {onAction && (
        <CardFooter className="pt-4 border-t border-border/50 bg-secondary/10 rounded-b-2xl">
          <Button 
            className="w-full rounded-xl bg-foreground text-background hover:bg-foreground/90 transition-all font-medium border border-transparent"
            onClick={() => onAction(job.id)}
          >
            {actionIcon}
            {actionLabel}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
