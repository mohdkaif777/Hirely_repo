"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getConversations, getMessages } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

type Conversation = {
  id: string;
  job_id: string;
  job_title: string;
  other_party_name: string;
  last_message?: string;
  last_message_time?: string;
};

type Message = {
  id: string;
  sender_type: string;
  message: string;
  created_at: string;
};

// Assuming backend runs on 8000
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

  // Load conversation list
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

  // Connect to WS when a conversation is selected
  useEffect(() => {
    if (!activeConv || !token) return;

    // Load history first
    getMessages(token, activeConv.id).then((history) => {
      setMessages(history || []);
      scrollToBottom();
    });

    // Establish WebSocket
    const socket = new WebSocket(`${WS_URL}/${activeConv.id}`);
    
    socket.onmessage = (event) => {
      const newMsg = JSON.parse(event.data);
      setMessages((prev) => [...prev, newMsg]);
      scrollToBottom();
      
      // Update sidebar latest message optimistically
      setConversations((prev) => prev.map(c => 
        c.id === activeConv.id 
          ? { ...c, last_message: newMsg.message, last_message_time: newMsg.created_at }
          : c
      ));
    };

    ws.current = socket;

    return () => {
      socket.close();
    };
  }, [activeConv, token]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ws.current || !inputVal.trim() || !user) return;

    ws.current.send(JSON.stringify({
      sender_type: user.role,
      text: inputVal.trim()
    }));
    
    setInputVal("");
  };

  if (loadingList) {
    return <div className="text-center py-10">Loading inbox...</div>;
  }

  return (
    <div className="grid md:grid-cols-3 gap-6 h-[75vh]">
      {/* Sidebar: Conversations */}
      <Card className="md:col-span-1 h-full overflow-hidden flex flex-col">
        <CardHeader className="border-b pb-4">
          <CardTitle>Inbox</CardTitle>
          <CardDescription>Your recent messages</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-0">
          {conversations.length === 0 ? (
            <div className="p-6 text-center text-muted-foreground text-sm">
              No conversations yet. {user?.role === "job_seeker" ? "Apply to jobs to start a chat!" : "Wait for candidates to message you."}
            </div>
          ) : (
            <div className="flex flex-col">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setActiveConv(conv)}
                  className={`flex flex-col items-start p-4 text-left border-b transition-colors hover:bg-muted ${
                    activeConv?.id === conv.id ? "bg-muted" : ""
                  }`}
                >
                  <div className="flex justify-between w-full mb-1">
                    <span className="font-semibold">{conv.other_party_name}</span>
                    <span className="text-xs text-muted-foreground">
                      {conv.last_message_time ? new Date(conv.last_message_time).toLocaleDateString() : ""}
                    </span>
                  </div>
                  <span className="text-xs font-medium text-primary mb-1">
                    Regarding: {conv.job_title}
                  </span>
                  <span className="text-sm text-muted-foreground line-clamp-1 w-full">
                    {conv.last_message || "No messages yet"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Chat Area */}
      <Card className="md:col-span-2 h-full flex flex-col overflow-hidden">
        {activeConv ? (
          <>
            <CardHeader className="border-b bg-muted/30 pb-4">
              <CardTitle>{activeConv.other_party_name}</CardTitle>
              <CardDescription>{activeConv.job_title}</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
              {messages.length === 0 ? (
                <div className="m-auto text-muted-foreground text-sm">
                  Send a message to start the conversation!
                </div>
              ) : (
                messages.map((msg) => {
                  const isMe = msg.sender_type === user?.role;
                  return (
                    <div
                      key={msg.id}
                      className={`flex flex-col max-w-[80%] ${
                        isMe ? "self-end items-end" : "self-start items-start"
                      }`}
                    >
                      <div
                        className={`px-4 py-2 rounded-2xl ${
                          isMe
                            ? "bg-primary text-primary-foreground rounded-br-none"
                            : "bg-muted rounded-bl-none"
                        }`}
                      >
                        {msg.message}
                      </div>
                      <span className="text-[10px] text-muted-foreground mt-1 px-1">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </CardContent>
            <div className="p-4 bg-background border-t">
              <form onSubmit={sendMessage} className="flex gap-2">
                <Input
                  placeholder="Type your message..."
                  value={inputVal}
                  onChange={(e) => setInputVal(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit" size="icon" disabled={!inputVal.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </>
        ) : (
          <div className="m-auto flex flex-col items-center justify-center text-muted-foreground">
            <svg
              className="w-16 h-16 text-muted mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p>Select a conversation to start messaging</p>
          </div>
        )}
      </Card>
    </div>
  );
}
