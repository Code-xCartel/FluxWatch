import {useSelector} from "react-redux";
import {Navigate, Outlet} from "react-router";
import {type RootState} from "@/store/store";
import {PUBLIC_ROUTES} from "@/constants/routes.ts";

export const PrivateRoute = () => {
    const {isAuthenticated} = useSelector((state: RootState) => state.auth);
    return isAuthenticated ? <Outlet /> : <Navigate to={PUBLIC_ROUTES.LOGIN} replace />;
};

export const PublicRoute = () => {
    return <Outlet />;
};
