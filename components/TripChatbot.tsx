"use client"

import { useChat } from "@ai-sdk/react"
import { TextStreamChatTransport } from "ai"
import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import ReactMarkdown from "react-markdown"

interface TripChatbotProps {
  userId: string
}

export default function TripChatbot({ userId }: TripChatbotProps) {
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { messages, sendMessage, status, setMessages } = useChat({
    transport: new TextStreamChatTransport({
      api: "/api/ai/chat",
      body: {
        userId: userId,
      },
    }),
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // Add initial message when component mounts
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: "initial-assistant-message",
          role: "assistant",
          parts: [
            {
              type: "text",
              text: "Hi! I'm Max, your travel assistant. I can help you with your trips, check weather, find places to visit, and plan your adventures. Ask me anything!",
            },
          ],
        },
      ])
    }
  }, [messages.length, setMessages])

  // Debug messages
  useEffect(() => {
    console.log("Messages updated:", messages)
    messages.forEach((msg, index) => {
      console.log(`Message ${index}:`, msg)
      console.log(`Message ${index} parts:`, msg.parts)
    })
  }, [messages])

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() && status === "ready") {
      sendMessage({ text: input })
      setInput("")
      // Scroll to bottom when user sends a message
      setTimeout(scrollToBottom, 100)
    }
  }

  return (
    <Card className="p-4 sm:p-6 max-w-2xl mx-auto shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        Travel Assistant
      </h2>

      <div className="space-y-4 mb-4 h-80 overflow-y-auto pr-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${
              m.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`p-3 rounded-lg max-w-[85%] break-words shadow-sm ${
                m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <p className="text-xs font-semibold mb-1 opacity-70">
                {m.role === "user" ? "You" : "Max"}
              </p>
              {m.role === "user" ? (
                <div className="text-sm">
                  {m.parts.map((part, index) =>
                    part.type === "text" ? (
                      <span key={index}>{part.text}</span>
                    ) : null
                  )}
                </div>
              ) : (
                <div className="text-sm prose prose-sm max-w-none prose-headings:mt-2 prose-headings:mb-1 prose-p:my-1 prose-li:my-0">
                  {m.parts.map((part, index) =>
                    part.type === "text" ? (
                      <ReactMarkdown key={index}>{part.text}</ReactMarkdown>
                    ) : null
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        {(status === "submitted" || status === "streaming") && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <div className="flex items-center space-x-1">
                <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            setInput(e.target.value)
          }
          placeholder="Ask a question about this trip..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          disabled={status !== "ready"}
        />
        <Button type="submit" disabled={status !== "ready" || !input.trim()}>
          Send
        </Button>
      </form>
    </Card>
  )
}
