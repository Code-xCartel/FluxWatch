import {type Control, Controller, type FieldPath, type FieldValues} from "react-hook-form";
import {Input} from "@/components/ui/input";
import {BaseField} from "./base-field";

interface AppTextFieldProps<T extends FieldValues> {
    name: FieldPath<T>;
    control: Control<T>;
    label?: string;
    placeholder?: string;
    type?: "text" | "password" | "email" | "number";
    disabled?: boolean;
}

export function AppTextField<T extends FieldValues>({
    name,
    control,
    label,
    type = "text",
    ...props
}: AppTextFieldProps<T>) {
    return (
        <Controller
            name={name}
            control={control}
            render={({field, fieldState: {error}}) => (
                <BaseField label={label} error={error?.message}>
                    <Input
                        {...field}
                        {...props}
                        type={type}
                        value={field.value ?? ""}
                        onChange={(e) =>
                            field.onChange(
                                type === "number" ? e.target.valueAsNumber : e.target.value,
                            )
                        }
                    />
                </BaseField>
            )}
        />
    );
}
