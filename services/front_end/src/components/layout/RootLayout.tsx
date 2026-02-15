import {type FC, type ReactNode} from "react";
import {ModeToggle} from "@/components/mode-toggle.tsx";

interface AuthLayoutOwnProps {
    children: ReactNode;
}

const RootLayout: FC<AuthLayoutOwnProps> = ({ children }) => {
    return (
        <div className="relative h-screen">
            <ModeToggle/>
            {children}
        </div>
    );
}

export default RootLayout;