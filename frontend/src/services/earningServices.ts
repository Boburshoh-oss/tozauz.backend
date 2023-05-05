import {requests} from "./requests";

export const earningServices = {
    getUserEarnings: (
        userId: string,
        pageIndex: number,
        pageSize: number
    ) => requests('GET', `bank/earning-list/${userId}/?page=${pageIndex}&page_size=${pageSize}`),

    get: (
        pageIndex: number,
        pageSize: number,
        selectedCategory: number,
        search: string,
        startDate: string,
        endDate: string
    ) => {
        let url = `bank/earning-list/?page=${pageIndex}&page_size=${pageSize}`
        if (selectedCategory) {
            url += `&tarrif=${selectedCategory}`
        }
        if (search) {
            url += `&search=${search}`
        }
        if (startDate) {
            url += `&start_date=${startDate}`
        }
        if (endDate) {
            url += `&end_date=${endDate}`
        }
        return requests('get', url)
    },
}