import {useState} from "react";
import {Home, LogOut} from "lucide-react";
import {useLocation, useNavigate} from "react-router";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import {LogoutDialog} from "@/components/logout-dialog";
import {APP_ROUTE} from "@/constants/routes.ts";

const navItems = [{title: "Events", icon: Home, path: APP_ROUTE.HOMEPAGE}];

export function AppSidebar() {
    const [logoutOpen, setLogoutOpen] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <>
            <Sidebar>
                <SidebarContent>
                    <SidebarGroup>
                        <SidebarGroupLabel>FluxWatch</SidebarGroupLabel>
                        <SidebarGroupContent>
                            <SidebarMenu>
                                {navItems.map((item) => (
                                    <SidebarMenuItem key={item.title}>
                                        <SidebarMenuButton
                                            isActive={location.pathname === item.path}
                                            onClick={() => navigate(item.path)}
                                        >
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </SidebarMenuButton>
                                    </SidebarMenuItem>
                                ))}
                            </SidebarMenu>
                        </SidebarGroupContent>
                    </SidebarGroup>
                </SidebarContent>

                <SidebarFooter>
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <SidebarMenuButton onClick={() => setLogoutOpen(true)}>
                                <LogOut />
                                <span>Logout</span>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarFooter>
            </Sidebar>

            <LogoutDialog open={logoutOpen} onOpenChange={setLogoutOpen} />
        </>
    );
}
