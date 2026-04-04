import { useCallback, useMemo } from "react";
import { useGetEventsQuery } from "@/services/eventsApi";
import DataTable from "@/components/common/data-table";
import { RowActionsMenu, type RowAction } from "@/components/common/data-table";
import { useDataTable, type HeadCell } from "@/hooks/use-data-table.tsx";
import { Eye, Trash2 } from "lucide-react";

const headCells: HeadCell[] = [
    { id: "eventType", label: "Event Type", hideable: false, width: 300 },
    { id: "entity", label: "Entity", width: 300 },
    { id: "producer", label: "Producer", width: 250 },
    { id: "actor", label: "Actor", width: 300 },
    { id: "occurredAt", label: "Occurred At", width: 300 },
];

type EventRow = Record<string, unknown> & {
    eventId: string;
    eventType: string;
    entity: string;
    producer: string;
    actor: string;
    occurredAt: string;
};

const Events = () => {
    const { data, isLoading, isError } = useGetEventsQuery({
        pageSize: 20,
        page: 1,
    });

    const rows = useMemo<EventRow[]>(
        () =>
            (data?.results ?? []).map((e) => ({
                eventId: e.eventId,
                eventType: e.eventType,
                entity: `${e.entity.type} / ${e.entity.id}`,
                producer: e.producer,
                actor: e.actor ? `${e.actor.type} / ${e.actor.id}` : "—",
                occurredAt: e.occurredAt,
            })),
        [data],
    );

    const getRowActions = useCallback((row: EventRow): RowAction[] => [
        {
            label: "View",
            icon: <Eye />,
            onClick: () => console.log("View", row.eventId),
        },
        {
            label: "Delete",
            icon: <Trash2 />,
            variant: "destructive",
            onClick: () => console.log("Delete", row.eventId),
        },
    ], []);

    const renderRowActions = useCallback(
        (row: EventRow) => <RowActionsMenu actions={getRowActions(row)} />,
        [getRowActions],
    );

    const { renderHeadCell, renderDefaultBody, columnVisibility } =
        useDataTable(rows, headCells, {
            identifier: "eventId",
            columnVisibility: { mode: "client" },
            rowActions: renderRowActions,
        });

    if (isError) return <div className="p-4">Error loading events</div>;

    return (
        <div className="p-4">
            <h1 className="mb-4 text-xl font-semibold">Events</h1>

            <DataTable
                headCells={headCells}
                rows={rows}
                renderHeadCell={renderHeadCell}
                renderDefaultBody={renderDefaultBody}
                columnVisibility={columnVisibility}
                isLoading={isLoading}
                variant="simple"
                stickyHeader
                maxHeight="75vh"
                noDataMessage="No events found"
            />
        </div>
    );
};

export default Events;
