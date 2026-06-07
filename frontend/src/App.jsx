import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Bot,
  FileText,
  HeartPulse,
  History,
  Loader2,
  Lock,
  MessageCircle,
  MessageSquarePlus,
  Paperclip,
  RefreshCw,
  Send,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  UserRound,
} from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const CHAT_HISTORY_STORAGE_KEY = "healio-chat-sessions";

const starterMessages = [
  {
    id: "welcome",
    role: "assistant",
    type: "answer",
    text:
      "Hi, I am Healio. Ask me a health question or upload a report, and I will keep things private, simple, and careful.",
  },
];

const symptomPrompts = [
  "My head hurts and I feel warm.",
  "I have a cough. What should I watch for?",
  "How do I clean a small scrape?",
  "What signs mean an allergy is serious?",
];

const rulebook = [
  { icon: ShieldCheck, label: "PII is redacted before AI." },
  { icon: AlertTriangle, label: "Emergency red flags bypass AI." },
  { icon: FileText, label: "Local references guide answers." },
  { icon: Lock, label: "Educational support only." },
];

function createChatSession(messages = starterMessages) {
  return {
    id: crypto.randomUUID(),
    title: getChatTitle(messages),
    messages,
    updatedAt: Date.now(),
  };
}

function getChatTitle(messages) {
  const firstUserMessage = messages.find((message) => message.role === "user");
  if (!firstUserMessage) return "New chat";

  return firstUserMessage.text.replace(/^Uploaded\s+/i, "").slice(0, 42);
}

function loadChatState() {
  try {
    const saved = JSON.parse(localStorage.getItem(CHAT_HISTORY_STORAGE_KEY));
    if (Array.isArray(saved) && saved.length > 0) {
      return { chatSessions: saved, activeChatId: saved[0].id };
    }
  } catch {
    localStorage.removeItem(CHAT_HISTORY_STORAGE_KEY);
  }

  const session = createChatSession();
  return { chatSessions: [session], activeChatId: session.id };
}

async function postChat(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error("Healio could not answer right now.");
  }

  return response.json();
}

async function postUpload(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Healio could not read that file.");
  }

  return response.json();
}

function App() {
  const [chatState, setChatState] = useState(loadChatState);
  const [draft, setDraft] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isUploadLoading, setIsUploadLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedFileName, setSelectedFileName] = useState("");
  const fileInputRef = useRef(null);

  const activeChat =
    chatState.chatSessions.find((session) => session.id === chatState.activeChatId) ||
    chatState.chatSessions[0];
  const messages = activeChat?.messages || starterMessages;
  const isBusy = isChatLoading || isUploadLoading;
  const latestEmergency = useMemo(
    () => [...messages].reverse().find((message) => message.type === "emergency"),
    [messages],
  );

  useEffect(() => {
    localStorage.setItem(CHAT_HISTORY_STORAGE_KEY, JSON.stringify(chatState.chatSessions));
  }, [chatState.chatSessions]);

  function updateActiveMessages(updater) {
    setChatState((current) => {
      const nextSessions = current.chatSessions.map((session) => {
        if (session.id !== current.activeChatId) return session;

        const nextMessages = updater(session.messages);
        return {
          ...session,
          messages: nextMessages,
          title: getChatTitle(nextMessages),
          updatedAt: Date.now(),
        };
      });

      return { ...current, chatSessions: nextSessions };
    });
  }

  function startNewChat() {
    if (isBusy) return;

    const session = createChatSession();
    setDraft("");
    setError("");
    setSelectedFileName("");
    setChatState((current) => ({
      chatSessions: [session, ...current.chatSessions],
      activeChatId: session.id,
    }));
  }

  function selectChat(chatId) {
    if (isBusy) return;

    setDraft("");
    setError("");
    setSelectedFileName("");
    setChatState((current) => ({ ...current, activeChatId: chatId }));
  }

  async function submitMessage(nextMessage = draft) {
    const text = nextMessage.trim();
    if (!text || isBusy) return;

    setError("");
    setDraft("");
    setIsChatLoading(true);
    updateActiveMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", type: "user", text },
    ]);

    try {
      const result = await postChat(text);
      updateActiveMessages((current) => [...current, normalizeAssistantMessage(result)]);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsChatLoading(false);
    }
  }

  async function handleFile(file) {
    if (!file || isBusy) return;

    setError("");
    setSelectedFileName(file.name);
    setIsUploadLoading(true);
    updateActiveMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        type: "upload",
        text: `Uploaded ${file.name}`,
      },
    ]);

    try {
      const result = await postUpload(file);
      updateActiveMessages((current) => [...current, normalizeAssistantMessage(result)]);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsUploadLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <main className="min-h-screen bg-clinic-cream text-clinic-ink">
      <div className="mx-auto grid min-h-screen w-full max-w-7xl grid-cols-1 gap-5 px-4 py-4 sm:px-6 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-8">
        <aside className="flex min-h-[520px] flex-col rounded-lg border border-white/80 bg-white/70 p-5 shadow-sm lg:sticky lg:top-4 lg:h-[calc(100vh-2rem)] lg:min-h-0">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-clinic-mint text-emerald-800">
              <HeartPulse aria-hidden="true" size={28} />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-bold uppercase tracking-wide text-emerald-700">Healio</p>
              <h1 className="text-2xl font-black leading-tight">Health Buddy</h1>
            </div>
          </div>

          <button
            type="button"
            onClick={startNewChat}
            disabled={isBusy}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-800 px-4 py-3 text-sm font-black text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            title="New chat"
          >
            <MessageSquarePlus aria-hidden="true" size={18} />
            New chat
          </button>

          <div className="mt-6 min-h-0 flex-1 overflow-y-auto pr-1">
            <ChatHistory
              activeChatId={chatState.activeChatId}
              chatSessions={chatState.chatSessions}
              isBusy={isBusy}
              onSelectChat={selectChat}
            />

            <div className="mt-6 space-y-3">
              {rulebook.map(({ icon: Icon, label }) => (
                <div key={label} className="flex min-h-14 items-center gap-3 rounded-lg bg-clinic-sky/45 p-3">
                  <Icon aria-hidden="true" className="shrink-0 text-sky-700" size={20} />
                  <p className="text-sm font-semibold leading-5">{label}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-lg border border-orange-200 bg-orange-50 p-4">
              <div className="flex items-center gap-2 font-bold text-orange-800">
                <AlertTriangle aria-hidden="true" className="shrink-0" size={20} />
                Urgent Care
              </div>
              <p className="mt-2 text-sm leading-6 text-orange-900">
                Chest pain, trouble breathing, severe bleeding, unconsciousness, seizures,
                poisoning, or suicidal thoughts need emergency help right away.
              </p>
            </div>
          </div>
        </aside>

        <section className="flex min-h-[calc(100vh-2rem)] flex-col rounded-lg border border-white/80 bg-white/75 shadow-sm">
          <header className="flex flex-col gap-4 border-b border-slate-200/80 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-clinic-peach text-rose-800">
                <Sparkles aria-hidden="true" size={24} />
              </div>
              <div>
                <h2 className="text-xl font-black">Ask Healio</h2>
                <p className="text-sm font-semibold text-slate-600">
                  Private first, safety first, family friendly.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-800">
              <Lock aria-hidden="true" size={16} />
              Local safety checks active
            </div>
          </header>

          {latestEmergency && (
            <div className="border-b border-red-200 bg-red-50 px-4 py-3 sm:px-5">
              <div className="flex items-start gap-3 text-red-900">
                <AlertTriangle aria-hidden="true" className="mt-1 shrink-0" size={22} />
                <div>
                  <p className="font-black">Emergency alert</p>
                  <p className="text-sm leading-6">{latestEmergency.text}</p>
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-2 border-b border-slate-200/80 p-4 sm:p-5">
            {symptomPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                onClick={() => submitMessage(prompt)}
                disabled={isBusy}
                className="rounded-lg border border-sky-200 bg-clinic-sky/45 px-3 py-2 text-left text-sm font-bold text-sky-900 transition hover:bg-clinic-sky disabled:cursor-not-allowed disabled:opacity-60"
              >
                {prompt}
              </button>
            ))}
          </div>

          <div className="grid flex-1 grid-cols-1 overflow-hidden lg:grid-cols-[minmax(0,1fr)_300px]">
            <div className="flex min-h-[540px] flex-col">
              <div className="flex-1 space-y-4 overflow-y-auto p-4 sm:p-5">
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
                {isChatLoading && <LoadingBubble label="Thinking carefully" />}
              </div>

              {error && (
                <div className="mx-4 mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-800 sm:mx-5">
                  <div className="flex items-center justify-between gap-3">
                    <span>{error}</span>
                    <button
                      type="button"
                      onClick={() => setError("")}
                      className="rounded-lg bg-white px-2 py-1 text-xs font-black"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}

              <form
                className="border-t border-slate-200/80 p-4 sm:p-5"
                onSubmit={(event) => {
                  event.preventDefault();
                  submitMessage();
                }}
              >
                <div className="flex gap-3">
                  <label className="sr-only" htmlFor="healio-message">
                    Message
                  </label>
                  <textarea
                    id="healio-message"
                    value={draft}
                    onChange={(event) => setDraft(event.target.value)}
                    placeholder="Tell Healio what is going on..."
                    rows={2}
                    className="min-h-14 flex-1 resize-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-base font-semibold leading-6 outline-none ring-emerald-200 transition focus:ring-4"
                  />
                  <button
                    type="submit"
                    disabled={!draft.trim() || isBusy}
                    className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-clinic-peach text-rose-900 shadow-sm transition hover:bg-rose-300 disabled:cursor-not-allowed disabled:opacity-60"
                    aria-label="Send message"
                    title="Send message"
                  >
                    {isChatLoading ? <Loader2 className="animate-spin" size={22} /> : <Send size={22} />}
                  </button>
                </div>
              </form>
            </div>

            <UploadPanel
              fileInputRef={fileInputRef}
              isLoading={isUploadLoading}
              selectedFileName={selectedFileName}
              onFile={handleFile}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

function ChatHistory({ activeChatId, chatSessions, isBusy, onSelectChat }) {
  const sortedSessions = [...chatSessions].sort((left, right) => right.updatedAt - left.updatedAt);

  return (
    <section>
      <div className="flex items-center gap-2 text-sm font-black text-slate-700">
        <History aria-hidden="true" size={17} />
        Chat history
      </div>
      <div className="mt-3 space-y-2">
        {sortedSessions.map((session) => {
          const isActive = session.id === activeChatId;

          return (
            <button
              key={session.id}
              type="button"
              onClick={() => onSelectChat(session.id)}
              disabled={isBusy}
              className={`w-full rounded-lg px-3 py-3 text-left transition disabled:cursor-not-allowed disabled:opacity-60 ${
                isActive
                  ? "bg-clinic-mint text-emerald-950"
                  : "bg-white/75 text-slate-700 hover:bg-white"
              }`}
              title={session.title}
            >
              <span className="block truncate text-sm font-black">{session.title}</span>
              <span className="mt-0.5 block text-xs font-semibold opacity-70">
                {formatChatTime(session.updatedAt)}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function formatChatTime(timestamp) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(timestamp));
}

function normalizeAssistantMessage(result) {
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    type: result.type || "answer",
    text: result.message || "Healio could not find a response.",
    redacted: Boolean(result.redacted),
    sourcesUsed: Boolean(result.sources_used),
    matchedTerms: result.matched_terms || [],
  };
}

function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const isEmergency = message.type === "emergency";
  const Icon = isUser ? UserRound : isEmergency ? AlertTriangle : Bot;

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div
          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
            isEmergency ? "bg-red-100 text-red-700" : "bg-clinic-mint text-emerald-800"
          }`}
        >
          <Icon aria-hidden="true" size={20} />
        </div>
      )}
      <div
        className={`max-w-[82%] rounded-lg px-4 py-3 shadow-sm ${
          isUser
            ? "bg-slate-800 text-white"
            : isEmergency
              ? "border border-red-200 bg-red-50 text-red-950"
              : "border border-slate-200 bg-white text-slate-800"
        }`}
      >
        <p className="whitespace-pre-wrap text-sm font-semibold leading-6 sm:text-base">{message.text}</p>
        {!isUser && !isEmergency && (message.redacted || message.sourcesUsed) && (
          <div className="mt-3 flex flex-wrap gap-2 text-xs font-black">
            {message.redacted && <span className="rounded-lg bg-emerald-50 px-2 py-1 text-emerald-800">PII redacted</span>}
            {message.sourcesUsed && <span className="rounded-lg bg-sky-50 px-2 py-1 text-sky-800">Local references</span>}
          </div>
        )}
        {isEmergency && message.matchedTerms.length > 0 && (
          <p className="mt-3 text-xs font-black uppercase tracking-wide text-red-700">
            Matched: {message.matchedTerms.join(", ")}
          </p>
        )}
      </div>
      {isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-800 text-white">
          {message.type === "upload" ? <Paperclip aria-hidden="true" size={20} /> : <Icon aria-hidden="true" size={20} />}
        </div>
      )}
    </article>
  );
}

function LoadingBubble({ label }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-clinic-mint text-emerald-800">
        <Bot aria-hidden="true" size={20} />
      </div>
      <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-slate-600">
        <Loader2 aria-hidden="true" className="animate-spin" size={18} />
        {label}
      </div>
    </div>
  );
}

function UploadPanel({ fileInputRef, isLoading, selectedFileName, onFile }) {
  return (
    <aside className="border-t border-slate-200/80 bg-slate-50/70 p-4 lg:border-l lg:border-t-0 sm:p-5">
      <div className="flex items-center gap-2">
        <FileText aria-hidden="true" className="text-sky-700" size={22} />
        <h3 className="text-lg font-black">Report Upload</h3>
      </div>
      <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
        Text, markdown, CSV, PDF, and image files under 2 MB are summarized through the same safety pipeline.
      </p>

      <label
        className="mt-5 flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-sky-200 bg-white p-5 text-center transition hover:border-sky-400 hover:bg-sky-50"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          onFile(event.dataTransfer.files?.[0]);
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="sr-only"
          accept=".txt,.md,.csv,.pdf,.jpg,.jpeg,.png,.webp,text/*,application/pdf,image/jpeg,image/png,image/webp"
          onChange={(event) => onFile(event.target.files?.[0])}
        />
        <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-clinic-sky text-sky-800">
          {isLoading ? <Loader2 className="animate-spin" size={28} /> : <UploadCloud size={28} />}
        </div>
        <p className="mt-4 text-base font-black">Drop or choose a file</p>
        <p className="mt-1 text-sm font-semibold text-slate-500">
          {selectedFileName || "Healio will summarize it simply."}
        </p>
      </label>

      <div className="mt-5 grid gap-3">
        <div className="rounded-lg bg-white p-3 text-sm font-semibold leading-6 text-slate-700">
          <div className="mb-1 flex items-center gap-2 font-black text-emerald-800">
            <MessageCircle aria-hidden="true" size={18} />
            Safety Flow
          </div>
          Emergency detection runs first, then PII redaction, local reference lookup, and summary generation.
        </div>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 rounded-lg bg-slate-800 px-4 py-3 text-sm font-black text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw aria-hidden="true" size={18} />
          Choose File
        </button>
      </div>
    </aside>
  );
}

export default App;
