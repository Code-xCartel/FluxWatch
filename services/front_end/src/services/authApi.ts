import {baseApi} from "./baseApi.ts";
import {login, logout} from "@/store/slices/authSlice.ts";
import {eraseCookie, setCookie} from "@/utils/cookies";
import {toBase64} from "@/utils";
import {type LoginFormValues, type RegisterFormValues} from "@/schemas/auth.ts";
import {API_ENDPOINTS, HTTP_METHODS} from "@/constants/api.ts";
import {HEADERS} from "@/constants/headers.ts";
import type {AuthResponse} from "@/models/auth.ts";

export const authApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        login: builder.mutation<AuthResponse, LoginFormValues>({
            query: (credentials) => ({
                url: API_ENDPOINTS.AUTH.SIGN_IN,
                method: HTTP_METHODS.POST,
                headers: {
                    [HEADERS.RESIDENT]: toBase64(`${credentials.email}:${credentials.password}`),
                },
            }),
            async onQueryStarted(_args, {dispatch, queryFulfilled}) {
                try {
                    const {data} = await queryFulfilled;
                    setCookie(HEADERS.AUTH_TOKEN, data.token);
                    dispatch(login({user: data.user, token: data.token}));
                } catch (error) {
                    console.error("Login Side-effect failed:", error);
                }
            },
        }),

        register: builder.mutation<AuthResponse, RegisterFormValues>({
            query: (credentials) => ({
                url: API_ENDPOINTS.AUTH.SIGN_UP,
                method: HTTP_METHODS.POST,
                body: credentials,
            }),

            async onQueryStarted(_args, {dispatch, queryFulfilled}) {
                try {
                    const {data} = await queryFulfilled;
                    setCookie(HEADERS.AUTH_TOKEN, data.token);
                    dispatch(login({user: data.user, token: data.token}));
                } catch (error) {
                    console.log(error)
                }
            },
        }),

        logout: builder.mutation<void, void>({
            query: () => ({url: API_ENDPOINTS.AUTH.SIGN_OUT, method: HTTP_METHODS.POST}),
            async onQueryStarted(_args, {dispatch, queryFulfilled}) {
                await queryFulfilled;
                eraseCookie(HEADERS.AUTH_TOKEN);
                dispatch(logout());
            },
        }),
    }),
});

export const {useLoginMutation, useRegisterMutation, useLogoutMutation} = authApi;
