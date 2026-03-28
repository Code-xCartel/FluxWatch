import {configureStore} from "@reduxjs/toolkit";
import authSlice from "@/store/slices/authSlice.ts";
import {baseApi} from "@/services/baseApi.ts";
import {setupListeners} from "@reduxjs/toolkit/query";

export const store = configureStore({
    reducer: {
        [authSlice.name]: authSlice.reducer,
        [baseApi.reducerPath]: baseApi.reducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(baseApi.middleware),
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
