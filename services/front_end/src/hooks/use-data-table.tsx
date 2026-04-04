import { useCallback, useMemo, useState, type ReactNode } from "react";
import {
    TableCell,
    TableHead,
    TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";

// ── Types ──────────────────────────────────────────────────────────────

export interface HeadCell {
    id: string;
    label: string;
    numeric?: boolean;
    disablePadding?: boolean;
    isSortable?: boolean;
    width?: string | number;
    className?: string;
    visible?: boolean;
    hideable?: boolean;
}

export interface SortHandler {
    sort: { by: string; direction: "asc" | "desc" };
    handleSort: (columnId: string) => void;
}

export type ColumnVisibilityMode =
    | { mode: "client" }
    | { mode: "server"; onVisibilityChange: (visibility: Record<string, boolean>) => void };

export interface ColumnVisibilityControls {
    visibilityMap: Record<string, boolean>;
    toggleColumn: (columnId: string) => void;
    visibleHeadCells: HeadCell[];
    allHeadCells: HeadCell[];
}

interface SelectableOptions {
    multiple?: boolean;
    onSelect?: ((event: React.MouseEvent, row: Record<string, unknown>) => void) | null;
    checkboxOnly?: boolean;
}

export interface UseDefaultTableOptions<T extends Record<string, unknown>> {
    sortHandler?: SortHandler;
    identifier?: string;
    selectable?: SelectableOptions;
    columnVisibility?: ColumnVisibilityMode;
    rowActions?: (row: T) => ReactNode;
}

// ── Selection hook (internal) ──────────────────────────────────────────

function useSelectedList<T extends Record<string, unknown>>(
    array: T[],
    identifier: string,
    multiple: boolean,
) {
    const [selected, setSelected] = useState<unknown[]>([]);
    const [selectedRows, setSelectedRows] = useState<T[]>([]);

    const handleClick = useCallback(
        (_event: React.MouseEvent, value: unknown) => {
            if (multiple) {
                setSelected((prev) => {
                    const idx = prev.indexOf(value);
                    if (idx === -1) return [...prev, value];
                    return prev.filter((_, i) => i !== idx);
                });
                setSelectedRows((prev) => {
                    const row = array.find((r) => r[identifier] === value);
                    const exists = prev.some((r) => r[identifier] === value);
                    if (exists) return prev.filter((r) => r[identifier] !== value);
                    return row ? [...prev, row] : prev;
                });
            } else {
                setSelected((prev) => (prev[0] === value ? [] : [value]));
                setSelectedRows(() => {
                    const row = array.find((r) => r[identifier] === value);
                    return row ? [row] : [];
                });
            }
        },
        [array, identifier, multiple],
    );

    const handleSelectAllClick = useCallback(() => {
        const allIds = array.map((r) => r[identifier]);
        const allSelected = allIds.every((id) => selected.includes(id));
        if (allSelected) {
            setSelected([]);
            setSelectedRows([]);
        } else {
            setSelected(allIds);
            setSelectedRows([...array]);
        }
    }, [array, identifier, selected]);

    const handleResetSelection = useCallback(() => {
        setSelected([]);
        setSelectedRows([]);
    }, []);

    const isSelected = useCallback(
        (value: unknown) => selected.includes(value),
        [selected],
    );

    return {
        selected,
        selectedRows,
        isSelected,
        numSelected: selected.length,
        handleClick,
        setSelected,
        setSelectedRows,
        handleSelectAllClick,
        handleResetSelection,
    };
}

// ── Main hook ──────────────────────────────────────────────────────────

export function useDataTable<T extends Record<string, unknown>>(
    array: T[] = [],
    headCells: HeadCell[] = [],
    options: UseDefaultTableOptions<T> = {},
) {
    const {
        sortHandler,
        identifier = "id",
        selectable = {},
        columnVisibility: columnVisibilityMode,
        rowActions,
    } = options;

    const selectableOptions = useMemo<Required<SelectableOptions>>(
        () => ({
            multiple: true,
            onSelect: null,
            checkboxOnly: false,
            ...selectable,
        }),
        [selectable],
    );

    const {
        setSelected,
        setSelectedRows,
        handleClick,
        isSelected,
        numSelected,
        selected,
        selectedRows,
        handleSelectAllClick,
        handleResetSelection,
    } = useSelectedList(array, identifier, selectableOptions.multiple);

    const rowCount = array.length;

    // ── Column visibility ──────────────────────────────────────────────

    const [visibilityOverrides, setVisibilityOverrides] = useState<Record<string, boolean>>({});

    // Merge headCells defaults with user overrides — no effect needed
    const visibilityMap = useMemo(() => {
        const map: Record<string, boolean> = {};
        for (const hc of headCells) {
            map[hc.id] = hc.id in visibilityOverrides
                ? visibilityOverrides[hc.id]
                : hc.visible !== false;
        }
        return map;
    }, [headCells, visibilityOverrides]);

    const toggleColumn = useCallback(
        (columnId: string) => {
            setVisibilityOverrides((prev) => {
                const currentVisible = columnId in prev ? prev[columnId] : true;
                const next = { ...prev, [columnId]: !currentVisible };
                // Prevent hiding all columns
                const allHidden = headCells.every((hc) =>
                    hc.id in next ? !next[hc.id] : hc.visible === false,
                );
                if (allHidden) return prev;
                if (columnVisibilityMode?.mode === "server") {
                    const fullMap: Record<string, boolean> = {};
                    for (const hc of headCells) {
                        fullMap[hc.id] = hc.id in next ? next[hc.id] : hc.visible !== false;
                    }
                    columnVisibilityMode.onVisibilityChange(fullMap);
                }
                return next;
            });
        },
        [columnVisibilityMode, headCells],
    );

    const visibleHeadCells = useMemo(
        () => headCells.filter((hc) => visibilityMap[hc.id] !== false),
        [headCells, visibilityMap],
    );

    const columnVisibility: ColumnVisibilityControls | undefined = columnVisibilityMode
        ? { visibilityMap, toggleColumn, visibleHeadCells, allHeadCells: headCells }
        : undefined;

    // ── Render helpers ─────────────────────────────────────────────────

    const renderHeadCell = useCallback(
        (headCell: HeadCell, index: number) => {
            const isSorted = sortHandler?.sort.by === headCell.id;
            const direction = sortHandler?.sort.direction;

            return (
                <TableHead
                    key={headCell.id ?? index}
                    className={cn(
                        headCell.numeric && "text-right",
                        headCell.disablePadding && "p-0",
                        headCell.className,
                    )}
                    style={{ width: headCell.width }}
                >
                    {headCell.isSortable && sortHandler ? (
                        <button
                            type="button"
                            className="inline-flex items-center gap-1 hover:text-foreground cursor-pointer"
                            onClick={() => sortHandler.handleSort(headCell.id)}
                        >
                            {headCell.label}
                            {isSorted ? (
                                direction === "asc" ? (
                                    <ArrowUp className="size-3.5" />
                                ) : (
                                    <ArrowDown className="size-3.5" />
                                )
                            ) : (
                                <ArrowUpDown className="size-3.5 opacity-50" />
                            )}
                        </button>
                    ) : (
                        headCell.label
                    )}
                </TableHead>
            );
        },
        [sortHandler],
    );

    const renderBodyCell = useCallback(
        (label: ReactNode, className?: string) => {
            return <TableCell className={className}>{label}</TableCell>;
        },
        [],
    );

    const renderCheckAllCell = useCallback(() => {
        const allIds = array.map((item) => item[identifier]);
        const pageHasSomeSelected = allIds.some((id) => selected.includes(id));
        const pageHasAllSelected =
            allIds.length > 0 && allIds.every((id) => selected.includes(id));

        return (
            <TableHead className="w-10 pr-0">
                {selectableOptions.multiple && (
                    <Checkbox
                        checked={
                            pageHasAllSelected
                                ? true
                                : pageHasSomeSelected
                                  ? "indeterminate"
                                  : false
                        }
                        onCheckedChange={() => handleSelectAllClick()}
                        aria-label="Select all"
                    />
                )}
            </TableHead>
        );
    }, [array, identifier, selected, selectableOptions.multiple, handleSelectAllClick]);

    const handleSelectRow = useCallback(
        (event: React.MouseEvent, row: T) => {
            if (selectableOptions.onSelect) {
                selectableOptions.onSelect(event, row);
            } else {
                handleClick(event, row[identifier]);
            }
        },
        [selectableOptions, handleClick, identifier],
    );

    const renderCheckRowCell = useCallback(
        (isItemSelected: boolean, onClick: (event: React.MouseEvent) => void) => {
            return (
                <TableCell className="w-10 pr-0" onClick={onClick}>
                    <Checkbox checked={isItemSelected} aria-label="Select row" />
                </TableCell>
            );
        },
        [],
    );

    const renderDefaultBody = useCallback(
        (
            rows: T[] = [],
            headerColumns: HeadCell[],
            selectableRows?: boolean,
            onClick?: (row: T) => void,
            styleCell?: (columnId: string, value: unknown) => string | undefined,
        ) => {
            return rows.map((row, index) => {
                const itemId = row[identifier];
                const isItemSelected = isSelected(itemId);

                return (
                    <TableRow
                        key={String(itemId ?? index)}
                        data-state={isItemSelected ? "selected" : undefined}
                        className={cn(
                            (onClick || (selectableRows && !selectableOptions.checkboxOnly)) &&
                                "cursor-pointer",
                        )}
                        onClick={(event) => {
                            if (onClick) {
                                onClick(row);
                            } else if (selectableRows && !selectableOptions.checkboxOnly) {
                                handleSelectRow(event, row);
                            }
                        }}
                    >
                        {selectableRows &&
                            renderCheckRowCell(isItemSelected, (event) => {
                                event.stopPropagation();
                                handleSelectRow(event, row);
                            })}
                        {headerColumns.map((column) => {
                            const cellClass = styleCell?.(column.id, row[column.id]);
                            return (
                                <TableCell key={column.id} className={cellClass}>
                                    {row[column.id] as ReactNode}
                                </TableCell>
                            );
                        })}
                        {/* Trailing cell: row actions OR empty spacer to match column-toggle header */}
                        {(rowActions || columnVisibilityMode) && (
                            <TableCell
                                className="w-10 p-0 text-center"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {rowActions?.(row)}
                            </TableCell>
                        )}
                    </TableRow>
                );
            });
        },
        [identifier, isSelected, selectableOptions.checkboxOnly, handleSelectRow, renderCheckRowCell, rowActions, columnVisibilityMode],
    );

    return {
        handleClick,
        handleSelectAllClick,
        handleResetSelection,
        isSelected,
        setSelected,
        setSelectedRows,
        renderHeadCell,
        renderBodyCell,
        renderCheckAllCell,
        renderCheckRowCell,
        renderDefaultBody,
        numSelected,
        rowCount,
        selected,
        selectedRows,
        columnVisibility,
    };
}
