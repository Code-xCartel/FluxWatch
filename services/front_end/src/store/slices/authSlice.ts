import {createSlice, type PayloadAction} from "@reduxjs/toolkit";
import {eraseCookie, getCookie, setCookie} from "@/utils/cookies";
import {REDUX_IDENTIFIERS} from "@/constants/redux-identifiers.ts";
import {HEADERS} from "@/constants/headers.ts";
import type {Account, AuthResponse} from "@/models/auth.ts";

interface AuthState {
    token: string | null;
    isAuthenticated: boolean;
    user: Account | null;
}

const initialState: AuthState = {
    token: getCookie(HEADERS.AUTH_TOKEN),
    isAuthenticated: !!getCookie(HEADERS.AUTH_TOKEN),
    user: null,
};

const authSlice = createSlice({
    name: REDUX_IDENTIFIERS.AUTH_REDUCER,
    initialState,
    reducers: {
        login: (state, {payload}: PayloadAction<AuthResponse>) => {
            state.user = payload.account;
            state.token = payload.accessToken;
            state.isAuthenticated = true;
            setCookie(HEADERS.AUTH_TOKEN, payload.accessToken, payload.ttl);
        },
        logout: (state) => {
            state.user = null;
            state.token = null;
            state.isAuthenticated = false;
            eraseCookie(HEADERS.AUTH_TOKEN);
        },
    },
});

export const {login, logout} = authSlice.actions;
export default authSlice;
