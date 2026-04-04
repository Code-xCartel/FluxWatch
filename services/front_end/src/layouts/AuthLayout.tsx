import type {FC} from "react";
import {Outlet} from "react-router";
import {Loader2} from "lucide-react";
import {SidebarProvider, SidebarTrigger} from "@/components/ui/sidebar";
import {AppSidebar} from "@/components/app-sidebar";
import {useGetSelfQuery} from "@/services/accountApi";

const AuthLayout: FC = () => {
    const {isLoading} = useGetSelfQuery(undefined, {refetchOnMountOrArgChange: true});

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <Loader2 className="text-muted-foreground size-8 animate-spin" />
            </div>
        );
    }

    return (
        <SidebarProvider>
            <AppSidebar />
            <main className="flex h-screen min-w-0 flex-1 flex-col">
                <SidebarTrigger className="m-2 shrink-0" />
                <div className="min-w-0 flex-1 overflow-y-auto">
                    <Outlet />
                </div>
            </main>
        </SidebarProvider>
    );
};

export default AuthLayout;
