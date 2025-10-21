import { auth } from "@/auth"

// Remove edge runtime to allow Prisma to work
// export const runtime = "edge"

export async function POST(req: Request) {
  const session = await auth()
  if (!session?.user?.id) {
    return new Response("Unauthorized", { status: 401 })
  }

  console.log("Sending message to FastAPI backend...")

  const { messages, userId } = await req.json()
  const lastMessage = messages[messages.length - 1]

  // Use userId from body if provided, otherwise use session
  const effectiveUserId = userId || session.user.id

  try {
    const fastapiResponse = await fetch("http://127.0.0.1:8000/chat-trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_input: lastMessage.parts[0].text, // Extract text from parts
        user_id: effectiveUserId,
      }),
    })

    // Handle errors from the Python server
    if (!fastapiResponse.ok || !fastapiResponse.body) {
      const errorText = await fastapiResponse.text()
      console.error("FastAPI backend error:", errorText)
      return new Response(
        `Error from backend: ${errorText || "Unknown error"}`,
        { status: fastapiResponse.status }
      )
    }

    console.log("FastAPI response received, extracting text stream...")

    // Extract text content from SSE stream for TextStreamChatTransport
    const encoder = new TextEncoder()
    const decoder = new TextDecoder()

    const stream = new ReadableStream({
      async start(controller) {
        const reader = fastapiResponse.body!.getReader()

        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split("\n")

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6))
                  if (data.ai_response) {
                    // Send just the plain text content
                    controller.enqueue(encoder.encode(data.ai_response))
                  }
                } catch (e) {
                  // Skip malformed JSON
                  continue
                }
              }
            }
          }
        } catch (error) {
          console.error("Stream processing error:", error)
          controller.error(error)
        } finally {
          controller.close()
        }
      },
    })

    return new Response(stream, {
      status: 200,
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    })
  } catch (error) {
    console.error("Error fetching from FastAPI backend:", error)
    return new Response("Failed to connect to the AI service.", { status: 500 })
  }
}
