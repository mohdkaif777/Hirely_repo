"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { signup, authGoogle } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { Sparkles, ArrowRight } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();
  const { setAuth } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    try {
      await signup(email, password);
      router.push("/login?registered=true");
    } catch (err: any) {
      setError(typeof err.message === "object" ? JSON.stringify(err.message) : (err.message || "Signup failed"));
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSuccess(credentialResponse: any) {
    if (!credentialResponse.credential) return;
    setError("");
    setLoading(true);
    try {
      const decoded: any = jwtDecode(credentialResponse.credential);
      const data = await authGoogle(decoded.email, decoded.name, decoded.picture);
      setAuth(data.access_token, data.user);

      if (!data.user.role) {
        router.push("/role-selection");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(typeof err.message === "object" ? JSON.stringify(err.message) : (err.message || "Google authentication failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/bg-gradient.svg')] bg-cover bg-center relative px-4 sm:px-6">
      <div className="absolute inset-0 bg-background/80 backdrop-blur-[100px] pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-tl from-primary/5 via-transparent to-accent-soft/5 pointer-events-none" />
      
      <div className="relative z-10 w-full flex justify-center py-12">
        <div className="w-full max-w-md animate-in fade-in zoom-in-95 duration-500">
          <div className="flex flex-col items-center mb-8 text-center">
            <Link href="/" className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-primary/10 text-primary mb-4 shadow-sm border border-primary/20 hover:scale-105 transition-transform">
              <Sparkles className="w-6 h-6" />
            </Link>
            <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">Create an account</h1>
            <p className="text-muted-foreground">Join HireAI to transform your hiring workflow</p>
          </div>

          <Card className="rounded-3xl border border-border/50 bg-card/60 backdrop-blur-xl shadow-2xl overflow-hidden">
            <div className="h-1 w-full bg-gradient-to-r from-accent-soft/80 to-primary/80" />
            
            <form onSubmit={handleSubmit} className="p-2">
              <CardContent className="space-y-4 p-6 sm:p-8">
                {error && (
                  <div className="bg-destructive/10 text-destructive text-sm font-medium p-3 rounded-xl border border-destructive/20 text-center animate-in slide-in-from-top-2">
                    {error}
                  </div>
                )}
                
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="h-12 bg-secondary/30 border-border/50 rounded-xl px-4 focus-visible:ring-primary/50 transition-all text-base"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="At least 6 characters"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="h-12 bg-secondary/30 border-border/50 rounded-xl px-4 focus-visible:ring-primary/50 transition-all text-base tracking-widest placeholder:tracking-normal"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="Repeat your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="h-12 bg-secondary/30 border-border/50 rounded-xl px-4 focus-visible:ring-primary/50 transition-all text-base tracking-widest placeholder:tracking-normal"
                  />
                </div>

                <Button type="submit" className="w-full h-12 rounded-xl text-base font-medium shadow-md group mt-3" disabled={loading}>
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin inline-block"></span>
                      Creating account...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2 w-full">
                      Sign Up
                      <ArrowRight className="w-4 h-4 opacity-70 group-hover:translate-x-1 transition-transform" />
                    </div>
                  )}
                </Button>

                <div className="relative my-6 text-center text-xs after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border/50">
                  <span className="relative z-10 bg-card px-3 text-muted-foreground uppercase tracking-widest font-semibold">
                    Or register with
                  </span>
                </div>

                <div className="flex justify-center w-full pb-2 relative z-20">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => setError("Google authentication failed")}
                    useOneTap
                    theme="filled_black"
                    shape="rectangular"
                    size="large"
                    logo_alignment="center"
                  />
                </div>
              </CardContent>
              <CardFooter className="px-8 pb-8 pt-0 flex justify-center border-t border-border/50 bg-secondary/5 mt-2 pt-6">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <Link href="/login" className="text-primary font-semibold hover:underline decoration-2 underline-offset-4 transition-all">
                    Log in
                  </Link>
                </p>
              </CardFooter>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
