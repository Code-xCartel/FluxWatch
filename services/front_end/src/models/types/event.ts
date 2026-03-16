type EventEntity = {
    type: "user" | "order" | "system" | "session" | string;
    id: string;
}

type EventActor = {
  type: string;
  id: string;
};

type EventContext = {
  traceId?: string | null;
  sessionId?: string | null;
  source?: string | null;
}

type Event = {
  eventId: string;
  entity: EventEntity;
  eventType: string;
  producer: string;
  actor?: EventActor;
  context?: EventContext;
  payload: Record<string, any>;
  occurredAt: string;
  eventVersion?: number;
};

type EventsQuery = {
  page: number;
  pageSize: number;
};

type EventsResponse = {
  results: Event[];
  meta: any | null;
};

export type { Event, EventsQuery, EventsResponse };
