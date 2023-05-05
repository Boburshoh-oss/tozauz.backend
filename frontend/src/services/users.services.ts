import {User} from "../types/users.types";
import {requests} from "./requests";

export const getUsers = async (
    search: string,
    selectedRole: string,
    pageIndex: number,
    pageSize: number
) => {
    let url = `account/admin-register/?page=${pageIndex}&page_size=${pageSize}`
    if (search) {
        url += `&search=${search}`
    }
    if (selectedRole) {
        url += `&role=${selectedRole}`
    }
    return await requests('GET', url);
}


export const getUser = async (id: Number) => {
    return await requests('GET', `account/admin-register/${id}/`);
}


export const createUser = async (data: User) => {
    return await requests('POST', 'account/admin-register/', data);
}

export const updateUser = async (data: User) => {
    const id = data.id;
    return await requests('PUT', `account/admin-register/${id}/`, data);
}

export const deleteUser = async (id: Number) => {
    return await requests('DELETE', `account/admin-register/${id}/`);
}