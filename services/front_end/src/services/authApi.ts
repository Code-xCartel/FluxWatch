import {baseApi} from "./baseApi.ts";
import {login, logout} from "@/store/slices/authSlice.ts";
import {eraseCookie} from "@/utils/cookies";
import {toBase64} from "@/utils";
import {type LoginFormValues, type SignUpFormValues} from "@/schemas/auth.ts";
import {API_ENDPOINTS, HTTP_METHODS} from "@/constants/api.ts";
import {HEADERS} from "@/constants/headers.ts";
import type {AuthResponse, LogoutScope} from "@/models/auth.ts";

export const authApi = baseApi.injectEndpoints({
    endpoints: (builder) => ({
        login: builder.mutation<AuthResponse, LoginFormValues>({
            query: (credentials) => ({
                url: API_ENDPOINTS.AUTH.SIGN_IN,
                method: HTTP_METHODS.POST,
                headers: {
                    [HEADERS.AUTHORIZATION]: `${HEADERS.RESIDENT} ${toBase64(`${credentials.password}:${credentials.email}`)}`,
                },
            }),
            async onQueryStarted(_args, {dispatch, queryFulfilled}) {
                try {
                    const {data} = await queryFulfilled;
                    dispatch(login(data));
                } catch (error) {
                    console.error("Login Side-effect failed:", error);
                }
            },
        }),

        register: builder.mutation<AuthResponse, SignUpFormValues>({
            query: (credentials) => ({
                url: API_ENDPOINTS.AUTH.SIGN_UP,
                method: HTTP_METHODS.POST,
                body: credentials,
            }),
        }),

        activate: builder.mutation<{msg: string}, string>({
            query: (token) => ({
                url: API_ENDPOINTS.AUTH.ACTIVATE,
                method: HTTP_METHODS.POST,
                headers: {
                    [HEADERS.AUTHORIZATION]: `${HEADERS.TOKEN} ${token}`,
                },
            }),
        }),

        resendEmail: builder.mutation<{msg: string}, string>({
            query: (token) => ({
                url: API_ENDPOINTS.AUTH.RESEND_EMAIL,
                method: HTTP_METHODS.POST,
                headers: {
                    [HEADERS.AUTHORIZATION]: `${HEADERS.TOKEN} ${token}`,
                },
            }),
        }),

        logout: builder.mutation<void, LogoutScope>({
            query: (scope) => ({
                url: `${API_ENDPOINTS.AUTH.SIGN_OUT}?scope=${scope}`,
                method: HTTP_METHODS.DELETE,
            }),
            async onQueryStarted(_args, {dispatch, queryFulfilled}) {
                await queryFulfilled;
                eraseCookie(HEADERS.AUTH_TOKEN);
                dispatch(logout());
            },
        }),
    }),
});

export const {
    useLoginMutation,
    useRegisterMutation,
    useActivateMutation,
    useResendEmailMutation,
    useLogoutMutation,
} = authApi;
