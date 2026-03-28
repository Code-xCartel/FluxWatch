import type {FC} from "react";
import {Outlet} from "react-router";
import {SidebarProvider, SidebarTrigger} from "@/components/ui/sidebar";
import {AppSidebar} from "@/components/app-sidebar";

const AuthLayout: FC = () => {
    return (
        <SidebarProvider>
            <AppSidebar />
            <main className="flex-1">
                <SidebarTrigger className="m-2" />
                <Outlet />
            </main>
        </SidebarProvider>
    );
};

export default AuthLayout;
