import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { API_URL } from "@/config.ts";
import type { EventsQuery, EventsResponse, Event } from "@/models/types/event.ts";

export const events = createApi({
  reducerPath: "eventsApi",
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
    prepareHeaders: (headers) => headers,
  }),
  endpoints: (builder) => ({
    getEvents: builder.query<EventsResponse, EventsQuery>({
      query: (params) => ({
        url: "/events",
        params,
      }),
    }),

    getEventById: builder.query<Event, string>({
      query: (eventId) => `/events/${eventId}`,
    }),
  }),
});

export const {
  useGetEventsQuery,
  useGetEventByIdQuery,
} = events;
