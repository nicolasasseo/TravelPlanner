import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import { NextRequest } from "next/server"

// API endpoint for the AI agent to fetch user trips
export async function GET(req: NextRequest) {
  const session = await auth()

  // Check if userId is provided in query params (for agent calls)
  const searchParams = req.nextUrl.searchParams
  const userId = searchParams.get("userId")

  if (!userId && !session?.user?.id) {
    return Response.json({ error: "Unauthorized" }, { status: 401 })
  }

  const targetUserId = userId || session?.user?.id

  try {
    const trips = await prisma.trip.findMany({
      where: {
        userId: targetUserId,
      },
      include: {
        locations: {
          orderBy: {
            order: "asc",
          },
        },
      },
      orderBy: {
        startDate: "desc",
      },
    })

    // Format dates as strings for JSON serialization
    const formattedTrips = trips.map((trip) => ({
      id: trip.id,
      title: trip.title,
      description: trip.description,
      startDate: trip.startDate.toISOString(),
      endDate: trip.endDate.toISOString(),
      locations: trip.locations.map((loc) => ({
        id: loc.id,
        name: loc.locationTitle,
        lat: loc.lat,
        lng: loc.lng,
        order: loc.order,
      })),
    }))

    return Response.json({ trips: formattedTrips })
  } catch (error) {
    console.error("Error fetching trips:", error)
    return Response.json({ error: "Failed to fetch trips" }, { status: 500 })
  }
}
