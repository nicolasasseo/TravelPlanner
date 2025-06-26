"use server"

import { auth } from "@/auth"
import { prisma } from "../prisma"

export async function reorderItinerary(tripId: string, newOrder: string[]) {
  const session = await auth()
  if (!session?.user) {
    throw new Error("Unauthorized")
  }
  await prisma.$transaction(
    newOrder.map((locationId: string, key: number) =>
      prisma.location.update({
        where: { id: locationId },
        data: { order: key },
      })
    )
  )
}
