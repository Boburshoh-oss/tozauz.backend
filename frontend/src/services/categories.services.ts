import { requests } from "./requests";
import { CategoryObj } from "../types/categories.types";



export const categoriesServices = {
    getCategories: async () => {
        return await requests('GET', 'packet/categories/');
    },

    updateCategory: async (data: CategoryObj) => {
        const id = data.id;
        return await requests('PUT', `packet/categories/${id}/`, data);
    },

    _categories: [] as CategoryObj[],

    categories: async function (fromServer: boolean = false) {
        if (this._categories.length === 0 || fromServer) {
            const res = await this.getCategories();
            this._categories = res.data;
        }
        return this._categories;
    },

    loadCategories: async function () {
        const res = await this.getCategories();
        this._categories = res.data;
    }
}