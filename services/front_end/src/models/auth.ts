export interface Account {
    id: string;
    name: string;
    principal: string;
    isActive: boolean;
    isLocked: boolean;
    failedLoginAttempts: number;
}

export interface AuthResponse {
    accessToken: string;
    account: Account;
    ttl: string;
}

export type LogoutScope = "current" | "all";
