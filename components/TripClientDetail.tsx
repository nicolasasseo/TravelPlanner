"use client"
import React, { useState } from "react"
import { Trip } from "@/app/generated/prisma"
import Image from "next/image"
import { Calendar, Plus } from "lucide-react"
import Link from "next/link"
import { Button } from "./ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"

interface TripDetailClientProps {
  trip: Trip
}

const TripClientDetail = ({ trip }: TripDetailClientProps) => {
  const [activeTab, setActiveTab] = useState("overview")
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {trip.imageUrl && (
        <div className="w-full h-72 md:h-96 overflow-hidden rounded-xl shadow-lg relative">
          <Image
            src={trip.imageUrl}
            alt={trip.title}
            className="object-cover"
            fill
            priority
          />
        </div>
      )}
      <div className="bg-white p-6 shadow rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900">
            {trip.title}
          </h1>
          <div className="flex items-center text-gray-500 mt-2">
            <Calendar className="h-5 w-5 mr-2" />
            <span className="text-lg">
              {trip.startDate.toLocaleDateString()} -{" "}
              {trip.endDate.toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="mt-4 md:mt-0">
          <Link href={`/trips/${trip.id}/itinerary/new`}>
            <Button>
              <Plus className="h-5 w-5 mr-2" />
              Add Location
            </Button>
          </Link>
        </div>
      </div>
      <div className="bg-white p-6 shadow rounded-lg">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="overview" className="text-lg">
              Overview
            </TabsTrigger>
            <TabsTrigger value="itinerary" className="text-lg">
              Itinerary
            </TabsTrigger>
            <TabsTrigger value="map" className="text-lg">
              Map
            </TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h2 className="text-2xl font-semibold mb-4"> </h2>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <Calendar className="h-6 w-6 mr-2 text-gray-500" />
                    <div>
                      <p className="text-gray-700 font-medium">Dates</p>
                      <p className="text-gray-500 text-sm">
                        {trip.startDate.toLocaleDateString()} -{" "}
                        {trip.endDate.toLocaleDateString()}
                        <br />
                        {`${Math.round(
                          (trip.endDate.getTime() - trip.startDate.getTime()) /
                            (1000 * 60 * 60 * 24)
                        )} days`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start"></div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default TripClientDetail
