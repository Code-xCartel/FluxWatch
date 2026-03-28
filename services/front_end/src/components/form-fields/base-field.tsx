import type {ReactNode} from "react";
import {Field, FieldError, FieldLabel} from "@/components/ui/field";

interface BaseFieldProps {
    label?: string;
    error?: string;
    children: ReactNode;
    isCheckbox?: boolean;
}

export const BaseField = ({label, error, children, isCheckbox}: BaseFieldProps) => (
    <Field className={isCheckbox ? "flex flex-row items-start space-y-0 space-x-3" : ""}>
        {!isCheckbox && label && <FieldLabel>{label}</FieldLabel>}
        {children}
        {isCheckbox && label && <FieldLabel className="text-sm font-medium">{label}</FieldLabel>}
        <FieldError>{error}</FieldError>
    </Field>
);
