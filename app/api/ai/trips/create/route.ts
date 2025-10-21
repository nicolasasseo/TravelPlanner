import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest } from "next/server"

// API endpoint for the AI agent to create trips
export async function POST(req: NextRequest) {
  console.log("🚀 CREATE TRIP API CALLED")

  const session = await auth()
  console.log("🔐 Session:", session?.user?.id || "No session")

  // Check if userId is provided in body (for agent calls)
  const body = await req.json()
  console.log("📝 Request body:", JSON.stringify(body, null, 2))

  const userId = body.userId || session?.user?.id
  console.log("👤 User ID:", userId)

  if (!userId) {
    console.log("❌ No user ID found")
    return Response.json({ error: "Unauthorized" }, { status: 401 })
  }

  try {
    const { title, description, summary, startDate, endDate, locations } = body
    console.log("📋 Trip data:", {
      title,
      startDate,
      endDate,
      locationsCount: locations?.length,
    })

    if (!title || !startDate || !endDate) {
      console.log("❌ Missing required fields")
      return Response.json(
        { error: "Missing required fields: title, startDate, endDate" },
        { status: 400 }
      )
    }

    console.log("💾 Creating trip in database...")

    // Create the trip with locations and summary
    const trip = await prisma.trip.create({
      data: {
        title,
        description: description || "",
        summary: summary || null,
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        userId,
        locations: locations
          ? {
              create: locations.map((loc: any, index: number) => ({
                locationTitle: loc.name,
                lat: loc.lat || 0,
                lng: loc.lng || 0,
                order: index,
              })),
            }
          : undefined,
      },
      include: {
        locations: true,
      },
    })

    console.log("✅ Trip created successfully:", trip.id)
    return Response.json({ trip, success: true })
  } catch (error) {
    console.error("❌ Error creating trip:", error)
    console.error("❌ Error details:", JSON.stringify(error, null, 2))
    return Response.json({ error: "Failed to create trip" }, { status: 500 })
  }
}
