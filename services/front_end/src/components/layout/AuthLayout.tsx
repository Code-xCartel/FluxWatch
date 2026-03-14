import type {FC, ReactNode} from "react";
import RootLayout from "@/components/layout/RootLayout.tsx";

interface AuthLayoutOwnProps {
    children: ReactNode
}

// TODO - Configure Authentication
const AuthLayout: FC<AuthLayoutOwnProps> = ({children}) => {
    return (
        <RootLayout>
            {children}
        </RootLayout>
    )
}

export default AuthLayout