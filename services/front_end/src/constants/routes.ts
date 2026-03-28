const PUBLIC_ROUTES = {
    LOGIN: "/login",
    REGISTER: "/register",
    ACTIVATE: "/activate",
} as const;

const PROTECTED_ROUTES = {
    HOMEPAGE: "/",
} as const;

const APP_ROUTE = {
    ...PUBLIC_ROUTES,
    ...PROTECTED_ROUTES,
} as const;

export {APP_ROUTE, PUBLIC_ROUTES, PROTECTED_ROUTES};
