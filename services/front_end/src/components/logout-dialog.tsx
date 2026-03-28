import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {useLogoutMutation} from "@/services/authApi.ts";

interface LogoutDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function LogoutDialog({open, onOpenChange}: LogoutDialogProps) {
    const [logout, {isLoading}] = useLogoutMutation();

    const handleLogout = async (scope: "current" | "all") => {
        try {
            await logout(scope).unwrap();
        } catch (err) {
            console.error("Logout failed:", err);
        } finally {
            onOpenChange(false);
        }
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Sign out</AlertDialogTitle>
                    <AlertDialogDescription>
                        Would you like to sign out of the current session or all sessions?
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isLoading}>Cancel</AlertDialogCancel>
                    <AlertDialogAction disabled={isLoading} onClick={() => handleLogout("current")}>
                        Current Session
                    </AlertDialogAction>
                    <AlertDialogAction disabled={isLoading} onClick={() => handleLogout("all")}>
                        All Sessions
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}
