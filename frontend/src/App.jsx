import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

const API_URL = import.meta.env.VITE_API_URL

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
      <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" />
    </div>
  )
}

function ToolBadge({ name }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-mono bg-slate-700 text-slate-300 border border-slate-600">
      <span className="text-slate-500">fn</span>
      {name}
    </span>
  )
}

function UserMessage({ text }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[75%] px-4 py-3 rounded-2xl rounded-tr-sm bg-indigo-600 text-white text-sm leading-relaxed">
        {text}
      </div>
    </div>
  )
}

function AssistantMessage({ answer, tools_called }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[75%] flex flex-col gap-2">
        <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-slate-700 text-slate-100 text-sm leading-relaxed prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{answer}</ReactMarkdown>
        </div>
        {tools_called && tools_called.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 px-1">
            <span className="text-xs text-slate-500">Formula used:</span>
            {tools_called.map((name, i) => (
              <ToolBadge key={i} name={name} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function LoadingMessage() {
  return (
    <div className="flex justify-start">
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-slate-700">
        <LoadingDots />
      </div>
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      setMessages(prev => [
        ...prev,
        { role: 'assistant', answer: data.answer, tools_called: data.tools_called },
      ])
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', answer: 'Something went wrong. Please try again.', tools_called: [] },
      ])
    } finally {
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 0)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-full bg-slate-900 text-white">
      {/* Header */}
      <header className="flex-none border-b border-slate-700/60 bg-slate-900/95 backdrop-blur px-6 py-4">
        <h1 className="text-lg font-semibold tracking-tight text-white">
          Headcount Planning AI
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Powered by deterministic formula engine
        </p>
      </header>

      {/* Message history */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto flex flex-col gap-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-500 text-sm mt-20 select-none">
              Ask a headcount or staffing question to get started.
            </div>
          )}
          {messages.map((msg, i) =>
            msg.role === 'user' ? (
              <UserMessage key={i} text={msg.text} />
            ) : (
              <AssistantMessage key={i} answer={msg.answer} tools_called={msg.tools_called} />
            )
          )}
          {loading && <LoadingMessage />}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input bar */}
      <footer className="flex-none border-t border-slate-700/60 bg-slate-900/95 backdrop-blur px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Ask about headcount, staffing gaps, utilization…"
            className="flex-1 bg-slate-800 text-white placeholder-slate-500 text-sm px-4 py-3 rounded-xl border border-slate-700 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  )
}
