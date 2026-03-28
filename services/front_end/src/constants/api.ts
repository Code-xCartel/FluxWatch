export const HTTP_METHODS = {
    GET: "GET",
    POST: "POST",
    PUT: "PUT",
    DELETE: "DELETE",
} as const;

export const API_ENDPOINTS = {
    AUTH: {
        SIGN_IN: "/auth/sign-in",
        SIGN_OUT: "/auth/sign-out",
        SIGN_UP: "/auth/sign-up",
        ACTIVATE: "/auth/activate",
        RESEND_EMAIL: "/auth/resend-email",
    },
    EVENTS: {
        LIST: "/events",
        DETAIL: (id: string) => `/events/${id}`,
    },
} as const;
