import {requests} from "../requests";


export const packetServices = {
    get: (
        pageIndex: number,
        pageSize: number,
        selectedCategory: string,
        search: string,
    ) => {
        let url = `packet/packet-list/?page=${pageIndex}&page_size=${pageSize}`
        if (selectedCategory) {
            url += `&category=${selectedCategory}`
        }
        if (search) {
            url += `&search=${search}`
        }
        return requests('get', url)
    }
}

