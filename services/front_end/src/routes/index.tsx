import {createBrowserRouter, RouterProvider} from "react-router";
import {PrivateRoute, PublicRoute} from "@/routes/guard.tsx";
import RootLayout from "@/layouts/RootLayout.tsx";
import {APP_ROUTE} from "@/constants/routes.ts";
import Login from "@/pages/auth/login.tsx";
import AuthLayout from "@/layouts/AuthLayout.tsx";
import Events from "@/pages/events";
import Register from "@/pages/auth/register.tsx";
import Activate from "@/pages/auth/activate.tsx";

const Routes = () => {
    const router = createBrowserRouter([
        {
            Component: RootLayout,
            children: [
                // PUBLIC-ROUTES
                {
                    Component: PublicRoute,
                    children: [
                        {
                            path: APP_ROUTE.LOGIN,
                            Component: Login,
                        },
                        {
                            path: APP_ROUTE.REGISTER,
                            Component: Register,
                        },
                        {
                            path: APP_ROUTE.ACTIVATE,
                            Component: Activate,
                        },
                    ],
                },

                // PROTECTED-ROUTES
                {
                    Component: PrivateRoute,
                    children: [
                        {
                            Component: AuthLayout,
                            children: [
                                {
                                    path: APP_ROUTE.HOMEPAGE,
                                    Component: Events,
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ]);

    return <RouterProvider router={router} />;
};

export default Routes;
