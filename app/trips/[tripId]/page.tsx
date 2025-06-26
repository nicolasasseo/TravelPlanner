import { auth } from "@/auth"
import { prisma } from "@/lib/prisma"
import TripClientDetail from "@/components/TripClientDetail"
import React from "react"

const page = async ({ params }: { params: Promise<{ tripId: string }> }) => {
  const { tripId } = await params
  const session = await auth()
  if (!session) {
    return <div>Please Sign In.</div>
  }
  const trip = await prisma.trip.findFirst({
    where: {
      id: tripId,
      userId: session?.user?.id,
    },
    include: { locations: true },
  })
  if (!trip) return <div>Trip not found.</div>

  return <TripClientDetail trip={trip} />
}

export default page
