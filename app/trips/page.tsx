import { auth } from "@/auth"
import React from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { prisma } from "@/lib/prisma"
import TripChatbot from "@/components/TripChatbot"

const page = async () => {
  const session = await auth()
  const trips = await prisma.trip.findMany({
    where: {
      userId: session?.user?.id,
    },
  })
  const sortedTrips = [...trips].sort((a, b) => {
    return new Date(b.startDate).getTime() - new Date(a.startDate).getTime()
  })
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const upcomingTrips = sortedTrips.filter((trip) => {
    return new Date(trip.startDate) >= today
  })

  if (!session) {
    return (
      <div className="flex justify-center items-center h-screen text-gray-700 text-xl">
        Please Sign In.
      </div>
    )
  }

  return (
    <div className="space-y-6 container mx-auto px-4 py-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <Link href="/trips/new">
          <Button>New Trip</Button>
        </Link>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Welcome Back, {session.user?.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>
            {trips.length > 0
              ? `You have ${trips.length} trip${
                  trips.length === 1 ? "" : "s"
                } planned.${
                  upcomingTrips.length > 0
                    ? `${upcomingTrips.length} upcoming.`
                    : ""
                }`
              : "You have not created any trips yet. Click the button above to create your first trip."}
          </p>
        </CardContent>
      </Card>
      {/* Show the TripChatbot if there is at least one trip */}
      <div>
        <h2 className="text-xl font-semibold mt-4 mb-2">Need help planning?</h2>
        {/* We give the first trip as an example, adjust as needed */}
        <TripChatbot
          tripId={sortedTrips[0].id}
          userId={session.user?.id as string}
        />
      </div>

      <div className="">
        <h2 className="text-lg font-semibold mb-4">Your Recent Trips</h2>
        {trips.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-8">
              <h3 className="text-xl font-medium mb-2">No trips yet.</h3>
              <p className="text-center mb-4 max-w-md">
                Start planning your next adventure by clicking the button above.
              </p>
              <Link href="/trips/new">
                <Button>Create Trip</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols:3 gap-4">
            {sortedTrips.slice(0, 6).map((trip, key) => (
              <Link href={`/trips/${trip.id}`} key={key}>
                <Card className="h-full hover:shadow-md transition-shadow">
                  <CardHeader>
                    <CardTitle className="line-clamp-1">{trip.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm mb-2 line-clamp-2">
                      {trip.description}
                    </p>
                    <p className="text-sm ">
                      {trip.startDate.toLocaleDateString()} -{" "}
                      {trip.endDate.toLocaleDateString()}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default page
