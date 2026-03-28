import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card";
import {AppTextField} from "@/components/form-fields/app-text-field";
import {AppPasswordField} from "@/components/form-fields/app-password-filed";
import {AppFormWrapper} from "@/components/form-fields/app-form-wrapper";
import {Link} from "react-router";
import {useLoginMutation} from "@/services/authApi.ts";
import {useForm} from "react-hook-form";
import {type LoginFormValues, loginSchema} from "@/schemas/auth.ts";
import {zodResolver} from "@hookform/resolvers/zod";
import {APP_ROUTE} from "@/constants/routes.ts";

export default function Login() {
    const [login, {isLoading, error}] = useLoginMutation();
    const form = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
        defaultValues: {email: "", password: ""},
    });

    const onSubmit = form.handleSubmit(async (values) => {
        try {
            await login(values).unwrap();
        } catch (err) {
            console.log(err)
        }
    });

    return (
        <div className="min-h-screen w-full flex items-center justify-center p-4 bg-muted/40">
            <Card className="w-full max-w-md shadow-lg border-muted">
                <CardHeader className="space-y-1 text-center">
                    <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
                    <CardDescription>
                        Enter your credentials to access your dashboard
                    </CardDescription>
                </CardHeader>

                <CardContent>
                    <AppFormWrapper
                        onSubmit={onSubmit}
                        isLoading={isLoading}
                        error={error}
                        buttonText="Sign In"
                    >
                        <AppTextField
                            name="email"
                            label="Email"
                            type="email"
                            placeholder="john@example.com"
                            control={form.control}
                            disabled={isLoading}
                        />
                        <AppPasswordField
                            name="password"
                            label="Password"
                            control={form.control}
                            disabled={isLoading}
                        />
                    </AppFormWrapper>
                </CardContent>

                <CardFooter className="flex flex-wrap items-center justify-center gap-1 text-sm text-muted-foreground">
                    <span>Don't have an account?</span>
                    <Link to={APP_ROUTE.REGISTER} className="text-primary font-medium hover:underline">
                        Create an account
                    </Link>
                </CardFooter>
            </Card>
        </div>
    );
}
