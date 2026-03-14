import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import {ThemeProvider} from "@/components/theme-provider.tsx";
import AuthLayout from "@/components/layout/AuthLayout.tsx";
import {Provider} from "react-redux";
import {store} from "@/store/store.ts";

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
            <AuthLayout>
                <Provider store={store}>
                    <App/>
                </Provider>
            </AuthLayout>
        </ThemeProvider>
    </StrictMode>,
)
