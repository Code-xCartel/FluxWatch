import * as z from "zod";

export const loginSchema = z.object({
    email: z.email("Invalid email address."),
    password: z.string().min(6, "Password must be at least 6 characters."),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const registerSchema = z
    .object({
        name: z.string().min(2, "Username must be at least 2 characters."),
        email: z.email("Invalid email address."),
        password: z
            .string()
            .min(8, "Password must be at least 8 characters.")
            .max(64, "Password should nt exceed 64 characters."),
        confirmPassword: z
            .string()
            .min(8, "Confirm Password must be at least 8 characters.")
            .max(64, "Confirm Password should nt exceed 64 characters."),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords don't match",
        path: ["confirmPassword"],
    });

export type RegisterFormValues = z.infer<typeof registerSchema>;

export type SignUpFormValues = Omit<RegisterFormValues, "confirmPassword">;
