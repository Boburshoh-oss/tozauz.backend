import { Admin, AdminFetchResponse, AdminLoginData } from "../types/users.types";
import { requests } from "./requests";


const initialAdmin: Admin = localStorage.getItem('admin')
    ? JSON.parse(localStorage.getItem('admin') as string)
    : {
        id: 0,
        firstName: null,
        phoneNumber: '',
    };


export const authServices = {

    admin: initialAdmin,

    token: localStorage.getItem('token') || '',

    isAuthenticated: function () {
        return this.token !== '';
    },

    login: async function (data: AdminLoginData) {
        return await requests('POST', 'account/admin-login/', data, false);
    },

    logout: function () {
        this.admin = initialAdmin;
        this.token = '';
        localStorage.removeItem('admin');
        localStorage.removeItem('token');
    },

    setUser: function (user: AdminFetchResponse) {
        this.admin = user.user;
        this.token = user.token;
        localStorage.setItem('admin', JSON.stringify(user.user));
        localStorage.setItem('token', user.token);
    },
}
