import React from "react"
import { prisma } from "@/lib/prisma"
import NewLocationClient from "@/components/NewLocationClient"

const page = async ({ params }: { params: Promise<{ tripId: string }> }) => {
  const { tripId } = await params
  const trip = await prisma.trip.findUnique({
    where: {
      id: tripId,
    },
  })
  return <NewLocationClient tripId={tripId} />
}

export default page
