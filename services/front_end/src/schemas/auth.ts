import * as z from "zod";

export const loginSchema = z.object({
    email: z.email("Invalid email address."),
    password: z.string().min(6, "Password must be at least 6 characters."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;


export const registerSchema = z.object({
    username: z.string().min(2, "Username must be at least 2 characters."),
    email: z.email("Invalid email address."),
    password: z.string().min(6, "Password must be at least 6 characters."),
    confirmPassword: z.string().min(6, "Please confirm your password."),
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
});

export type RegisterFormValues = z.infer<typeof registerSchema>;

