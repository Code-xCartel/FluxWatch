import {useGetEventsQuery} from "@/services/eventsApi";

const Events = () => {
    const {data, isLoading, isError} = useGetEventsQuery({
        pageSize: 20,
        page: 1,
    });

    if (isLoading) return <div className="p-4">Loading…</div>;
    if (isError) return <div className="p-4">Error loading events</div>;

    return (
        <>
            <div className="p-4">
                <h1 className="mb-4 text-xl font-semibold">Events</h1>

                <div className="space-y-2">
                    {data?.results?.map((e) => (
                        <div
                            key={e.eventId}
                            className="flex flex-col gap-1 rounded-xl border p-3 text-sm"
                        >
                            <div className="font-medium">{e.eventType}</div>
                            <div className="text-muted-foreground">
                                {e.entity.type} / {e.entity.id} • producer: {e.producer}
                            </div>
                            <div className="text-muted-foreground text-xs">{e.occurredAt}</div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
};

export default Events;
