import {useEffect} from "react";
import {Link, useSearchParams} from "react-router";
import {AlertCircle, CheckCircle, Loader2, MailCheck} from "lucide-react";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {useActivateMutation, useResendEmailMutation} from "@/services/authApi";
import {APP_ROUTE} from "@/constants/routes";

export default function Activate() {
    const [searchParams] = useSearchParams();
    const token = searchParams.get("t");
    const [activate, {isLoading, isSuccess, isError, error}] = useActivateMutation();
    const [resendEmail, {isLoading: isResending, isSuccess: isResent}] = useResendEmailMutation();

    useEffect(() => {
        if (token) {
            activate(token);
        }
    }, [token, activate]);

    const getErrorMessage = () => {
        if (!token)
            return "No activation token provided. Please check your email for the correct link.";
        if (error && "data" in error) {
            const data = error.data as {detail?: string};
            return data?.detail || "Activation failed. The link may have expired.";
        }
        return "Activation failed. The link may have expired or is invalid.";
    };

    const handleResend = () => {
        if (token) {
            resendEmail(token);
        }
    };

    return (
        <div className="bg-muted/40 flex min-h-screen w-full items-center justify-center p-4">
            <Card className="border-muted w-full max-w-md shadow-lg">
                <CardHeader className="space-y-1 text-center">
                    <CardTitle className="text-2xl font-bold">Account Activation</CardTitle>
                    <CardDescription>
                        {isLoading && "Verifying your account..."}
                        {isSuccess && "Your email has been verified"}
                        {(isError || !token) && "We couldn't activate your account"}
                    </CardDescription>
                </CardHeader>

                <CardContent className="flex flex-col items-center gap-4 py-6">
                    {isLoading && (
                        <Loader2 className="text-muted-foreground h-12 w-12 animate-spin" />
                    )}

                    {isSuccess && (
                        <>
                            <CheckCircle className="text-primary h-12 w-12" />
                            <p className="text-muted-foreground text-center text-sm">
                                Your account has been activated successfully. You can close this tab
                                now.
                            </p>
                            <Link
                                to={APP_ROUTE.LOGIN}
                                className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex h-9 items-center justify-center rounded-md px-6 text-sm font-medium"
                            >
                                Go to Login
                            </Link>
                        </>
                    )}

                    {(isError || !token) && (
                        <>
                            <AlertCircle className="text-destructive h-12 w-12" />
                            <p className="text-muted-foreground text-center text-sm">
                                {getErrorMessage()}
                            </p>

                            {isResent ? (
                                <div className="text-muted-foreground flex items-center gap-2 text-sm">
                                    <MailCheck className="h-4 w-4" />
                                    <span>A new verification email has been sent.</span>
                                </div>
                            ) : (
                                token && (
                                    <button
                                        onClick={handleResend}
                                        disabled={isResending}
                                        className="bg-primary text-primary-foreground hover:bg-primary/90 inline-flex h-9 items-center justify-center rounded-md px-6 text-sm font-medium disabled:pointer-events-none disabled:opacity-50"
                                    >
                                        {isResending ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Sending...
                                            </>
                                        ) : (
                                            "Resend Email"
                                        )}
                                    </button>
                                )
                            )}
                        </>
                    )}
                </CardContent>

                <CardFooter className="text-muted-foreground flex flex-wrap items-center justify-center gap-1 text-sm">
                    <span>Need help?</span>
                    <Link
                        to={APP_ROUTE.REGISTER}
                        className="text-primary font-medium hover:underline"
                    >
                        Create a new account
                    </Link>
                </CardFooter>
            </Card>
        </div>
    );
}
