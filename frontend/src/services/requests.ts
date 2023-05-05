import axios from 'axios';
import { getHeaders } from './getHeaders';

export const BASE_URL = 'http://tozauz-api.saminjonov.uz/api/v1/';

export const requests = async (method: string = 'GET', path: string, data?: any, withAuth: boolean = true) => {
    if (withAuth) {
        return axios({
            method: method,
            url: BASE_URL + path,
            data: data,
            headers: getHeaders()
        });
    } else {
        return axios({
            method: method,
            url: BASE_URL + path,
            data: data
        });
    }
}
