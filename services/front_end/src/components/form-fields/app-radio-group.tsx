import {type Control, Controller, type FieldPath, type FieldValues} from "react-hook-form";
import {RadioGroup, RadioGroupItem} from "@/components/ui/radio-group";
import {Label} from "@/components/ui/label";
import {BaseField} from "./base-field";
import {cn} from "@/lib/utils";

interface RadioOption {
    label: string;
    value: string;
    description?: string;
}

interface AppRadioGroupProps<T extends FieldValues> {
    name: FieldPath<T>;
    control: Control<T>;
    label?: string;
    options: RadioOption[];
    variant?: "default" | "card";
}

export function AppRadioGroup<T extends FieldValues>({
    name,
    control,
    label,
    options,
    variant = "default",
}: AppRadioGroupProps<T>) {
    return (
        <Controller
            name={name}
            control={control}
            render={({field, fieldState: {error}}) => (
                <BaseField label={label} error={error?.message}>
                    <RadioGroup
                        onValueChange={field.onChange}
                        value={field.value}
                        className={
                            variant === "card"
                                ? "grid grid-cols-1 gap-4 md:grid-cols-2"
                                : "flex flex-col space-y-3"
                        }
                    >
                        {options.map((option) => {
                            const id = `${name}-${option.value}`;
                            const isSelected = field.value === option.value;

                            return (
                                <div key={option.value}>
                                    <RadioGroupItem
                                        value={option.value}
                                        id={id}
                                        className="sr-only"
                                    />
                                    <Label
                                        htmlFor={id}
                                        className={cn(
                                            "border-muted bg-popover hover:bg-accent hover:text-accent-foreground flex cursor-pointer flex-col items-start justify-between rounded-md border-2 p-4",
                                            isSelected ? "border-primary" : "opacity-80",
                                        )}
                                    >
                                        <span className="font-bold tracking-tight">
                                            {option.label}
                                        </span>
                                        {option.description && (
                                            <span className="text-muted-foreground mt-1 text-xs">
                                                {option.description}
                                            </span>
                                        )}
                                    </Label>
                                </div>
                            );
                        })}
                    </RadioGroup>
                </BaseField>
            )}
        />
    );
}
