import {useState} from "react";
import {type Control, Controller, type FieldPath, type FieldValues} from "react-hook-form";
import {Eye, EyeOff} from "lucide-react";
import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {BaseField} from "./base-field";

export function AppPasswordField<T extends FieldValues>({
    name,
    control,
    label,
    placeholder,
    disabled,
}: {
    name: FieldPath<T>;
    control: Control<T>;
    label: string;
    placeholder?: string;
    disabled?: boolean;
}) {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <Controller
            name={name}
            control={control}
            render={({field, fieldState: {error}}) => (
                <BaseField label={label} error={error?.message}>
                    <div className="relative">
                        <Input
                            {...field}
                            type={showPassword ? "text" : "password"}
                            placeholder={placeholder}
                            disabled={disabled}
                            className="pr-10"
                            value={field.value ?? ""}
                        />
                        <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute top-0 right-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowPassword(!showPassword)}
                            disabled={disabled}
                        >
                            {showPassword ? (
                                <EyeOff className="text-muted-foreground h-4 w-4" />
                            ) : (
                                <Eye className="text-muted-foreground h-4 w-4" />
                            )}
                        </Button>
                    </div>
                </BaseField>
            )}
        />
    );
}
