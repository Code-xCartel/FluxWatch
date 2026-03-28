import {type FC} from "react";
import {Outlet} from "react-router";
import {ModeToggle} from "@/components/mode-toggle.tsx";

const RootLayout: FC = () => {
    return (
        <div className="bg-background text-foreground relative min-h-screen">
            <ModeToggle />
            <Outlet />
        </div>
    );
};

export default RootLayout;
