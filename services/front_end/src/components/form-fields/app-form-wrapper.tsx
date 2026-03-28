import type {ReactNode} from "react";
import {AlertCircle, Loader2} from "lucide-react";
import {Button} from "@/components/ui/button";
import {Alert, AlertDescription} from "@/components/ui/alert";

interface AppFormWrapperProps {
    children: ReactNode;
    onSubmit: (e?: React.BaseSyntheticEvent) => Promise<void> | void;
    isLoading: boolean;
    error?: any;
    buttonText: string;
    className?: string;
}

export function AppFormWrapper({
    children,
    onSubmit,
    isLoading,
    error,
    buttonText,
    className = "space-y-6 w-full",
}: AppFormWrapperProps) {
    // Extract error message from RTK Query or generic error
    const errorMessage =
        error?.data?.message || error?.message || (error ? "An unexpected error occurred" : null);

    return (
        <form onSubmit={onSubmit} className={className}>
            {/* Global API Error Alert */}
            {errorMessage && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
            )}

            {/* Form Fields (AppTextField, AppSelect, etc.) */}
            <div className="space-y-4">{children}</div>

            {/* Main Action Button */}
            <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                    </>
                ) : (
                    buttonText
                )}
            </Button>
        </form>
    );
}
