import {
    Table,
    TableBody,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { HeadCell, ColumnVisibilityControls } from "@/hooks/use-data-table.tsx";
import type { ReactNode } from "react";
import { Columns3, MoreHorizontal } from "lucide-react";

// ── Exported row-actions helper ────────────────────────────────────────

export interface RowAction {
    label: string;
    icon?: ReactNode;
    onClick: () => void;
    variant?: "default" | "destructive";
}

export function RowActionsMenu({ actions }: { actions: RowAction[] }) {
    if (actions.length === 0) return null;
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon-xs" className="text-muted-foreground">
                    <MoreHorizontal className="size-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                {actions.map((action, i) => (
                    <DropdownMenuItem
                        key={i}
                        variant={action.variant}
                        onClick={action.onClick}
                    >
                        {action.icon}
                        {action.label}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

// ── Variant styles ─────────────────────────────────────────────────────
// Both variants use border-separate so sticky right/top works
// (Tailwind preflight sets border-collapse:collapse which breaks sticky)

const variantStyles = {
    simple: {
        table: "border-separate border-spacing-0",
        head: "[&_th]:px-3 [&_th]:py-2.5 [&_th]:text-xs [&_th]:font-semibold [&_th]:uppercase [&_th]:tracking-wider [&_th]:text-muted-foreground [&_th]:bg-muted [&_th]:border-b [&_th]:border-r [&_th]:border-border [&_th:last-child]:border-r-0",
        body: "[&_td]:h-[42px] [&_td]:border-b [&_td]:border-r [&_td]:border-border [&_td:last-child]:border-r-0",
        headerRow: "hover:bg-transparent [&_th]:border-b-2",
    },
    plain: {
        table: "border-separate border-spacing-0",
        head: "[&_th]:px-3 [&_th]:py-2.5 [&_th]:text-xs [&_th]:font-semibold [&_th]:uppercase [&_th]:tracking-wider [&_th]:text-muted-foreground [&_th]:bg-muted [&_th]:border-b [&_th]:border-border",
        body: "[&_td]:h-[42px] [&_td]:border-b [&_td]:border-border",
        headerRow: "hover:bg-transparent [&_th]:border-b-2",
    },
} as const;

// ── Table skeleton loader ──────────────────────────────────────────────

function TableLoader({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
    return (
        <div className="flex flex-col gap-3 p-4">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-4">
                    {Array.from({ length: columns }).map((_, j) => (
                        <Skeleton key={j} className="h-4 flex-1" />
                    ))}
                </div>
            ))}
        </div>
    );
}

// ── Column toggle dropdown ─────────────────────────────────────────────

function ColumnToggleDropdown({ columnVisibility }: { columnVisibility: ColumnVisibilityControls }) {
    const { allHeadCells, visibilityMap, toggleColumn } = columnVisibility;
    const toggleableColumns = allHeadCells.filter((hc) => hc.hideable !== false);

    if (toggleableColumns.length === 0) return null;

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon-xs" className="text-muted-foreground">
                    <Columns3 className="size-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuLabel>Toggle columns</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {toggleableColumns.map((column) => (
                    <DropdownMenuCheckboxItem
                        key={column.id}
                        checked={visibilityMap[column.id] !== false}
                        onCheckedChange={() => toggleColumn(column.id)}
                        onSelect={(e) => e.preventDefault()}
                    >
                        {column.label}
                    </DropdownMenuCheckboxItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

// ── Props ──────────────────────────────────────────────────────────────

interface DataTableProps<T extends Record<string, unknown>> {
    headCells: HeadCell[];
    rows: T[];
    renderHeadCell: (headCell: HeadCell, index: number) => ReactNode;
    renderDefaultBody: (
        rows: T[],
        headCells: HeadCell[],
        selectableRows?: boolean,
        onRowClick?: (row: T) => void,
        styleCell?: (columnId: string, value: unknown) => string | undefined,
    ) => ReactNode;
    renderCheckAllCell?: () => ReactNode;
    columnVisibility?: ColumnVisibilityControls;
    showColumnToggle?: boolean;
    showPinnedColumn?: boolean;
    toolbarLeft?: ReactNode;
    selectableRows?: boolean;
    checkboxOnly?: boolean;
    onRowClick?: (row: T) => void;
    isLoading?: boolean;
    styleCell?: (columnId: string, value: unknown) => string | undefined;
    loadingRows?: number;
    loadingColumns?: number;
    size?: "sm" | "default";
    variant?: "simple" | "plain";
    noDataMessage?: ReactNode;
    stickyHeader?: boolean;
    maxHeight?: string | number;
    height?: string | number;
    className?: string;
}

// ── Component ──────────────────────────────────────────────────────────

export default function DataTable<T extends Record<string, unknown>>({
    headCells,
    rows,
    renderHeadCell,
    renderDefaultBody,
    renderCheckAllCell,
    columnVisibility,
    showColumnToggle = true,
    showPinnedColumn,
    toolbarLeft,
    selectableRows,
    checkboxOnly,
    onRowClick,
    isLoading,
    styleCell,
    loadingRows = 5,
    loadingColumns,
    size = "default",
    variant = "simple",
    noDataMessage = "No Data Found",
    stickyHeader = false,
    maxHeight,
    height,
    className,
}: DataTableProps<T>) {
    const styles = variantStyles[variant];
    const effectiveHeadCells = columnVisibility?.visibleHeadCells ?? headCells;
    const renderColumnToggle = showColumnToggle && !!columnVisibility;
    const hasPinnedColumn = showPinnedColumn ?? (renderColumnToggle || false);
    const hasToolbar = !!toolbarLeft;

    return (
        <div className={cn("flex min-w-0 flex-col", className)}>
            {hasToolbar && (
                <div className="flex items-center gap-2 pb-3">
                    {toolbarLeft}
                </div>
            )}

            {/* Scroll container */}
            <div
                className={cn(
                    "relative w-full overflow-auto rounded-md border",
                    selectableRows && !checkboxOnly && "[&_tbody]:cursor-pointer",
                )}
                style={{ maxHeight, height }}
            >
                <Table
                    noContainer
                    className={cn(
                        "w-max min-w-full",
                        size === "sm" && "text-xs",
                        styles.table,
                        styles.head,
                        styles.body,
                    )}
                >
                    <TableHeader
                        className={cn(
                            stickyHeader && "sticky top-0 z-20 bg-background",
                        )}
                    >
                        <TableRow className={styles.headerRow}>
                            {selectableRows && renderCheckAllCell?.()}
                            {effectiveHeadCells.map((headCell, index) =>
                                renderHeadCell(headCell, index),
                            )}
                            {/* Pinned column: column-toggle in header, row-actions in body */}
                            {hasPinnedColumn && (
                                <TableHead className="sticky right-0 z-30 w-10 border-l border-border bg-muted p-0 text-center">
                                    {renderColumnToggle && (
                                        <ColumnToggleDropdown columnVisibility={columnVisibility!} />
                                    )}
                                </TableHead>
                            )}
                        </TableRow>
                    </TableHeader>

                    {!isLoading && (
                        <TableBody>
                            {renderDefaultBody(
                                rows,
                                effectiveHeadCells,
                                selectableRows,
                                onRowClick,
                                styleCell,
                            )}
                        </TableBody>
                    )}
                </Table>

                {isLoading && (
                    <div className="sticky left-0">
                        <TableLoader
                            rows={loadingRows}
                            columns={loadingColumns ?? effectiveHeadCells.length}
                        />
                    </div>
                )}

                {!isLoading && (!rows || rows.length === 0) && (
                    <div className="sticky left-0 my-2 flex items-center justify-center rounded-md p-4">
                        <p className="text-muted-foreground text-sm">{noDataMessage}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
