import { authServices } from "./auth.services";

export const getHeaders = () => {
    const token = authServices.token;

    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Token ' + token
    };
    return headers;
}