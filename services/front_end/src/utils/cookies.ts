const setCookie = (name: string, value: string, ttl: string) => {
    const expires = "; expires=" + new Date(ttl).toUTCString();
    console.log();
    // Secure: only over HTTPS; SameSite=Strict: prevents CSRF
    document.cookie = `${name}=${value || ""}${expires}; path=/; SameSite=Strict; Secure`;
};

const getCookie = (name: string) => {
    const nameEQ = name + "=";
    const ca = document.cookie.split(";");
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === " ") c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
};

const eraseCookie = (name: string) => {
    document.cookie = name + "=; Max-Age=-99999999; path=/;";
};

export {setCookie, getCookie, eraseCookie};
