import {type Control, Controller, type FieldPath, type FieldValues} from "react-hook-form";
import {Checkbox} from "@/components/ui/checkbox";
import {BaseField} from "./base-field";

export function AppCheckbox<T extends FieldValues>({
    name,
    control,
    label,
}: {
    name: FieldPath<T>;
    control: Control<T>;
    label: string;
}) {
    return (
        <Controller
            name={name}
            control={control}
            render={({field, fieldState: {error}}) => (
                <BaseField label={label} error={error?.message} isCheckbox>
                    <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                </BaseField>
            )}
        />
    );
}
