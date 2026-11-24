"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { 
  Bot, Send, User, Sparkles, Wrench, CheckCircle2, 
  MessageSquare, Plus, ArrowRight, CornerDownLeft, RefreshCw 
} from "lucide-react";
import { api } from "@/lib/api";
import { AgentChatMessage } from "@/types";

function AgentContent() {
  const searchParams = useSearchParams();
  const initialMsg = searchParams.get("msg") || "";

  const [messages, setMessages] = useState<AgentChatMessage[]>([
    {
      sender: "assistant",
      content: "Hello! I am your **MatchIQ AI Career Intelligence Copilot**. I have direct access to your candidate profile, real-time hybrid search, and the explainable matching engine.\n\nYou can ask me to discover opportunities, compare roles, evaluate skill gaps, or update your preferences.",
      model: "matchiq-copilot-engine"
    }
  ]);
  const [input, setInput] = useState(initialMsg);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [conversations, setConversations] = useState<any[]>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load existing conversations
  useEffect(() => {
    api.getConversations().then((convos) => {
      if (Array.isArray(convos)) setConversations(convos);
    }).catch(() => {});

    // If an initial message was passed via query params, send it automatically
    if (initialMsg) {
      handleSendMessage(initialMsg);
    }
  }, []);

  const handleSendMessage = async (textToSend = input) => {
    if (!textToSend.trim() || loading) return;

    const userMessage = textToSend.trim();
    setInput("");

    // Append user message immediately
    setMessages((prev) => [...prev, { sender: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await api.chatWithAgent(userMessage, conversationId);
      if (res.conversation_id && !conversationId) {
        setConversationId(res.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          content: res.response,
          tool_calls: res.tools_executed?.map((t: any) => ({ name: t.name, args: t.args })),
          tool_results: res.tools_executed?.map((t: any) => ({ name: t.name, result: t.result })),
          model: res.model_used
        }
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          content: `Agent error: ${err.message || "Could not process request."}`,
          model: "system-error"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startNewConversation = () => {
    setConversationId(undefined);
    setMessages([
      {
        sender: "assistant",
        content: "Started a fresh career strategy session. How can I assist your opportunity search today?",
        model: "matchiq-copilot-engine"
      }
    ]);
  };

  const SUGGESTIONS = [
    "Search for backend roles involving Python, distributed systems and AI",
    "Analyze skill gaps for opp-seed-002",
    "What are my current candidate profile skills?",
    "Save opp-seed-001 to my tracker"
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-1 flex flex-col">
      {/* Top Bar */}
      <div className="flex items-center justify-between pb-4 border-b border-navy-800/80 mb-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-300">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white flex items-center gap-2">
              Career Copilot
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-300 border border-brand-500/20">
                Tool Execution Engine Active
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">
              Autonomous reasoning with explicit PostgreSQL & vector tool calling.
            </p>
          </div>
        </div>

        <button
          onClick={startNewConversation}
          className="px-3 py-1.5 rounded-lg border border-navy-800 bg-navy-900 hover:bg-navy-850 text-xs text-slate-300 hover:text-white transition flex items-center gap-1.5"
        >
          <Plus className="h-3.5 w-3.5" />
          New Chat
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4 min-h-[450px] max-h-[600px]">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 text-xs sm:text-sm ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {msg.sender === "assistant" && (
              <div className="h-7 w-7 rounded-lg bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-300 flex-shrink-0 mt-1">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 leading-relaxed ${
                msg.sender === "user"
                  ? "bg-brand-600 text-white rounded-br-sm"
                  : "bg-navy-900/90 border border-navy-800 text-slate-200 rounded-bl-sm shadow-md"
              }`}
            >
              {/* Tool Execution Badges if Assistant executed backend functions */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="mb-3 space-y-2">
                  {msg.tool_calls.map((tool: any, tIdx: number) => (
                    <div
                      key={tIdx}
                      className="p-2 rounded-lg bg-navy-950/80 border border-brand-500/25 flex items-center justify-between text-[11px]"
                    >
                      <div className="flex items-center gap-1.5 text-brand-300 font-mono">
                        <Wrench className="h-3 w-3 text-brand-400" />
                        <span>tool_executed: <strong>{tool.name}</strong></span>
                      </div>
                      <span className="flex items-center gap-1 text-[10px] text-emerald-400">
                        <CheckCircle2 className="h-3 w-3" /> success
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* Message text with basic markdown formatting */}
              <div className="whitespace-pre-wrap space-y-2 font-sans">
                {msg.content}
              </div>

              {msg.model && (
                <div className="mt-2 pt-2 border-t border-navy-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>Engine: {msg.model}</span>
                </div>
              )}
            </div>

            {msg.sender === "user" && (
              <div className="h-7 w-7 rounded-lg bg-navy-800 border border-navy-700 flex items-center justify-center text-slate-300 flex-shrink-0 mt-1">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2.5 text-xs text-brand-400 p-3 rounded-xl bg-navy-900/60 border border-navy-800 max-w-sm">
            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            <span>Analyzing candidate context & executing backend tools...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {SUGGESTIONS.map((sugg, i) => (
          <button
            key={i}
            onClick={() => handleSendMessage(sugg)}
            className="text-[11px] text-slate-400 hover:text-slate-200 bg-navy-900/70 hover:bg-navy-850 border border-navy-800 px-2.5 py-1 rounded-lg transition"
          >
            {sugg}
          </button>
        ))}
      </div>

      {/* Chat Input Box */}
      <div className="relative">
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Copilot (e.g. 'Compare opp-seed-001 and opp-seed-002', 'What skills am I missing for senior Go roles?')..."
          className="w-full bg-navy-900 border border-navy-700/80 rounded-2xl p-3 pr-12 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition shadow-inner resize-none"
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={!input.trim() || loading}
          className="absolute right-3 bottom-4 p-2 rounded-xl bg-brand-600 hover:bg-brand-500 text-white transition disabled:opacity-40"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

export default function AgentPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center text-xs text-slate-400">Initializing Career Copilot session...</div>}>
      <AgentContent />
    </Suspense>
  );
}
