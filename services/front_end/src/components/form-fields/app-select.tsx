// src/components/shared/Form/AppSelect.tsx
import {type Control, Controller, type FieldPath, type FieldValues} from "react-hook-form";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {BaseField} from "./base-field";

interface AppSelectProps<T extends FieldValues> {
    name: FieldPath<T>;
    control: Control<T>;
    label?: string;
    placeholder?: string;
    options: {label: string; value: string}[];
}

export function AppSelect<T extends FieldValues>({
    name,
    control,
    label,
    options,
    placeholder,
}: AppSelectProps<T>) {
    return (
        <Controller
            name={name}
            control={control}
            render={({field, fieldState: {error}}) => (
                <BaseField label={label} error={error?.message}>
                    <Select onValueChange={field.onChange} value={field.value}>
                        <SelectTrigger>
                            <SelectValue placeholder={placeholder} />
                        </SelectTrigger>
                        <SelectContent>
                            {options.map((opt) => (
                                <SelectItem key={opt.value} value={opt.value}>
                                    {opt.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </BaseField>
            )}
        />
    );
}
