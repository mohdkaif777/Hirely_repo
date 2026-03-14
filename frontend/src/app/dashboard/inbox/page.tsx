"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getConversations, getMessages } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User as UserIcon, Building2, Search, Info, MessageSquare } from "lucide-react";
import { RankBadge } from "@/components/ui/RankBadge";
import { MatchScore } from "@/components/ui/MatchScore";
import { cn } from "@/lib/utils";

type Conversation = {
  id: string;
  job_id: string;
  job_title: string;
  other_party_name: string;
  agent_status?: string;
  match_score?: number;
  match_rank?: number;
  match_status?: string;
  last_message?: string;
  last_message_time?: string;
};

type Message = {
  id: string;
  sender_type: string;
  message: string;
  created_at: string;
};

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/chat/ws";

export default function InboxPage() {
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputVal, setInputVal] = useState("");
  const [loadingList, setLoadingList] = useState(true);
  
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function fetchList() {
      if (!token) return;
      try {
        const data = await getConversations(token);
        setConversations(data || []);
      } catch (err) {
        console.error("Failed to fetch conversations", err);
      } finally {
        setLoadingList(false);
      }
    }
    fetchList();
  }, [token]);

  useEffect(() => {
    if (!activeConv || !token) return;

    getMessages(token, activeConv.id).then((history) => {
      setMessages(history || []);
      scrollToBottom();
    });

    let reconnectTimeout: NodeJS.Timeout;
    let isCleaned = false;

    function connectWS() {
      if (isCleaned || !activeConv) return;
      const socket = new WebSocket(`${WS_URL}/${activeConv.id}`);
      
      socket.onopen = () => console.log("[WS] Connected to", activeConv.id);

      socket.onmessage = (event) => {
        const newMsg = JSON.parse(event.data);
        setMessages((prev) => [...prev, newMsg]);
        scrollToBottom();
        
        setConversations((prev) => prev.map(c => 
          c.id === activeConv.id 
            ? { ...c, last_message: newMsg.message, last_message_time: newMsg.created_at }
            : c
        ));
      };

      socket.onerror = (err) => console.error("[WS] Error:", err);

      socket.onclose = () => {
        if (!isCleaned) {
          reconnectTimeout = setTimeout(connectWS, 2000);
        }
      };

      ws.current = socket;
    }

    connectWS();

    return () => {
      isCleaned = true;
      clearTimeout(reconnectTimeout);
      ws.current?.close();
    };
  }, [activeConv, token]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN || !inputVal.trim() || !user) return;

    ws.current.send(JSON.stringify({
      sender_type: user.role,
      text: inputVal.trim()
    }));
    
    setInputVal("");
  };

  const formatTime = (iso?: string) => {
    if (!iso) return "";
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loadingList) {
    return (
      <div className="flex flex-col items-center justify-center p-20 space-y-4 h-full">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin"></div>
        <p className="text-sm text-muted-foreground font-medium animate-pulse">Loading inbox...</p>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] rounded-2xl border border-border bg-background shadow-xl overflow-hidden">
      
      {/* Left Rail: Conversations */}
      <div className="w-[320px] md:w-[380px] border-r border-border bg-card/30 backdrop-blur-sm flex flex-col shrink-0">
        <div className="p-4 border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-10">
          <h2 className="text-lg font-bold tracking-tight mb-3">Messages</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search conversations..." 
              className="pl-9 h-9 bg-secondary/30 border-border/50 text-sm rounded-xl focus-visible:ring-1 focus-visible:ring-primary/50"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-hide">
          {conversations.length === 0 ? (
            <div className="p-8 text-center flex flex-col items-center justify-center h-full text-muted-foreground">
              <MessageSquare className="w-12 h-12 mb-4 opacity-20" />
              <p className="text-sm font-medium">No messages yet</p>
              <p className="text-xs mt-1 max-w-[200px] opacity-70">
                {user?.role === "job_seeker" ? "Apply to jobs to start chatting with recruiters." : "Matches will appear here as candidates are validated."}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-border/30">
              {conversations.map((conv) => {
                const isActive = activeConv?.id === conv.id;
                return (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConv(conv)}
                    className={cn(
                      "w-full flex items-start p-4 text-left transition-all hover:bg-secondary/40 group",
                      isActive ? "bg-primary/5 border-l-2 border-l-primary" : "border-l-2 border-l-transparent"
                    )}
                  >
                    <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center shrink-0 mr-3 border border-border shadow-sm">
                      {user?.role === 'recruiter' ? <UserIcon className="w-5 h-5 text-muted-foreground" /> : <Building2 className="w-5 h-5 text-muted-foreground" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-baseline mb-0.5">
                        <span className="font-semibold text-sm truncate pr-2 text-foreground group-hover:text-primary transition-colors">
                          {conv.other_party_name}
                        </span>
                        <span className="text-[10px] text-muted-foreground shrink-0 font-medium">
                          {conv.last_message_time ? new Date(conv.last_message_time).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ""}
                        </span>
                      </div>
                      <div className="text-xs font-medium text-primary/80 line-clamp-1 mb-1.5 flex items-center gap-2">
                        <span>{conv.job_title}</span>
                        {conv.agent_status && (
                          <span className="px-1.5 py-0.5 rounded-sm bg-primary/10 text-primary uppercase text-[8px] tracking-wider font-bold">
                            {conv.agent_status}
                          </span>
                        )}
                      </div>
                      <p className={cn(
                        "text-xs line-clamp-1",
                        isActive ? "text-foreground" : "text-muted-foreground"
                      )}>
                        {conv.last_message || "No messages yet"}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel: Chat Stream */}
      <div className="flex-1 flex flex-col bg-card/10 backdrop-blur-sm relative overflow-hidden">
        {activeConv ? (
          <>
            <div className="h-16 border-b border-border bg-card/60 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-10 shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center hidden sm:flex border border-border">
                  {user?.role === 'recruiter' ? <UserIcon className="w-5 h-5 text-muted-foreground" /> : <Building2 className="w-5 h-5 text-muted-foreground" />}
                </div>
                <div>
                  <h3 className="font-bold text-base leading-none text-foreground flex items-center gap-2">
                    {activeConv.other_party_name}
                    {activeConv.match_rank !== undefined && activeConv.match_rank <= 3 && (
                      <RankBadge rank={activeConv.match_rank} className="scale-90 origin-left" />
                    )}
                  </h3>
                  <p className="text-sm text-primary font-medium mt-1">{activeConv.job_title}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {activeConv.match_score !== undefined && (
                  <div className="hidden sm:block">
                    <MatchScore score={activeConv.match_score} size="sm" />
                  </div>
                )}
                <Button variant="ghost" size="icon" className="rounded-full hover:bg-secondary">
                  <Info className="w-5 h-5 text-muted-foreground relative z-20" />
                </Button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 sm:p-6 flex flex-col gap-5 scrollbar-thin scrollbar-thumb-secondary scrollbar-track-transparent">
              {messages.length === 0 ? (
                <div className="m-auto flex flex-col items-center justify-center text-center max-w-sm">
                  <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
                    <MessageSquare className="w-8 h-8 text-primary" />
                  </div>
                  <h4 className="text-lg font-semibold mb-2">Start the conversation</h4>
                  <p className="text-sm text-muted-foreground">
                    Send a message to introduce yourself. Our AI agent will assist as needed.
                  </p>
                </div>
              ) : (
                messages.map((msg, index) => {
                  const isMe = msg.sender_type === user?.role;
                  const isSystem = msg.sender_type === "system";
                  const isAiAgent = msg.sender_type === "ai_agent";
                  
                  // Add subtle animation delay for staggering if rendering all at once
                  const staggerDelay = index > messages.length - 5 ? `animate-in fade-in slide-in-from-bottom-4 duration-300` : "";

                  if (isSystem) {
                    return (
                      <div key={msg.id} className={cn("self-center my-4 max-w-[85%]", staggerDelay)}>
                        <div className="bg-secondary/30 px-4 py-2 rounded-full text-xs text-muted-foreground font-medium text-center border border-border/50 shadow-sm backdrop-blur-sm flex items-center gap-2">
                          <Info className="w-3.5 h-3.5 opacity-70" />
                          {msg.message}
                          <span className="opacity-50 ml-1 font-mono text-[10px]">
                            {formatTime(msg.created_at)}
                          </span>
                        </div>
                      </div>
                    );
                  }
                  
                  return (
                    <div
                      key={msg.id}
                      className={cn(
                        "flex flex-col group max-w-[85%] sm:max-w-[75%]",
                        isMe ? "self-end items-end" : "self-start items-start",
                        staggerDelay
                      )}
                    >
                      {/* Avatar for others */}
                      {!isMe && (
                        <div className="flex items-end gap-2 mb-1 pl-1">
                          <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                            {isAiAgent && <Bot className="w-3.5 h-3.5 text-primary" />}
                            {isAiAgent ? "AI Assistant" : activeConv.other_party_name}
                          </span>
                        </div>
                      )}
                      
                      <div
                        className={cn(
                          "px-5 py-3 rounded-2xl shadow-sm text-sm leading-relaxed",
                          isMe
                            ? "bg-foreground text-background rounded-br-sm"
                            : isAiAgent 
                              ? "bg-primary/10 text-primary-foreground border border-primary/20 rounded-bl-sm"
                              : "bg-card border border-border text-foreground rounded-bl-sm"
                        )}
                        style={{wordBreak: "break-word"}}
                      >
                        {msg.message}
                      </div>

                      <div className={cn(
                        "text-[10px] text-muted-foreground font-medium mt-1.5 opacity-0 group-hover:opacity-100 transition-opacity",
                        isMe ? "pr-1" : "pl-1"
                      )}>
                        {formatTime(msg.created_at)}
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} className="h-4" />
            </div>

            <div className="p-4 sm:p-5 bg-card/60 backdrop-blur-xl border-t border-border shrink-0">
              <form onSubmit={sendMessage} className="relative flex items-end gap-3 max-w-4xl mx-auto">
                <div className="relative flex-1 bg-secondary/30 border border-border rounded-xl focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all shadow-sm">
                  <textarea
                    placeholder="Type your message..."
                    value={inputVal}
                    onChange={(e) => setInputVal(e.target.value)}
                    className="w-full bg-transparent p-3 pl-4 pr-12 text-sm outline-none resize-none max-h-32 min-h-[44px] hidden-scrollbar rounded-xl placeholder:text-muted-foreground/70"
                    rows={1}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage(e as any);
                      }
                    }}
                  />
                  <div className="absolute right-2 bottom-2">
                    <Button 
                      type="submit" 
                      size="icon" 
                      className={cn(
                        "h-8 w-8 rounded-lg transition-all",
                        inputVal.trim() ? "bg-primary text-primary-foreground shadow-md hover:bg-primary/90" : "bg-transparent text-muted-foreground hover:bg-secondary"
                      )}
                      disabled={!inputVal.trim()}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground bg-gradient-to-b from-transparent to-secondary/10">
            <div className="w-24 h-24 rounded-3xl bg-secondary/50 flex items-center justify-center mb-6 shadow-inner border border-border/50">
              <MessageSquare className="w-10 h-10 opacity-50" />
            </div>
            <h3 className="text-2xl font-bold text-foreground tracking-tight mb-2">HireAI Inbox</h3>
            <p className="text-secondary-foreground max-w-[280px] text-center text-sm">
              Select a conversation from the left sidebar to start messaging.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
