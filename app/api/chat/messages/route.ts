import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest } from "next/server"

// Get chat history for a user
export async function GET(req: NextRequest) {
  const session = await auth()

  if (!session?.user?.id) {
    return Response.json({ error: "Unauthorized" }, { status: 401 })
  }

  try {
    const messages = await prisma.chatMessage.findMany({
      where: {
        userId: session.user.id,
      },
      orderBy: {
        createdAt: "asc",
      },
      take: 50, // Last 50 messages
    })

    return Response.json({ messages })
  } catch (error) {
    console.error("Error fetching chat messages:", error)
    return Response.json({ error: "Failed to fetch messages" }, { status: 500 })
  }
}

// Save a chat message
export async function POST(req: NextRequest) {
  const session = await auth()

  if (!session?.user?.id) {
    return Response.json({ error: "Unauthorized" }, { status: 401 })
  }

  try {
    const { role, content } = await req.json()

    if (!role || !content) {
      return Response.json(
        { error: "Missing role or content" },
        { status: 400 }
      )
    }

    const message = await prisma.chatMessage.create({
      data: {
        role,
        content,
        userId: session.user.id,
      },
    })

    return Response.json({ message })
  } catch (error) {
    console.error("Error saving chat message:", error)
    return Response.json({ error: "Failed to save message" }, { status: 500 })
  }
}

// Clear chat history for a user
export async function DELETE(req: NextRequest) {
  const session = await auth()

  if (!session?.user?.id) {
    return Response.json({ error: "Unauthorized" }, { status: 401 })
  }

  try {
    await prisma.chatMessage.deleteMany({
      where: {
        userId: session.user.id,
      },
    })

    return Response.json({ success: true })
  } catch (error) {
    console.error("Error deleting chat messages:", error)
    return Response.json(
      { error: "Failed to delete messages" },
      { status: 500 }
    )
  }
}
