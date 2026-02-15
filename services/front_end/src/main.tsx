import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import {ThemeProvider} from "@/components/theme-provider.tsx";
import AuthLayout from "@/components/layout/AuthLayout.tsx";

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
            <AuthLayout>
                <App/>
            </AuthLayout>
        </ThemeProvider>
    </StrictMode>,
)
