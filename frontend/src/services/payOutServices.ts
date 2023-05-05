import {requests} from "./requests";

export const payOutServices = {
    getUserPayOuts: (
        userId: string,
        pageIndex: number,
        pageSize: number
    ) => requests('GET', `bank/payout-list/${userId}/?page=${pageIndex}&page_size=${pageSize}`),

    createPayOut: (userId: string, amount: number) => requests('POST', 'bank/payout-list-create/', {
        user: userId,
        amount: amount
    }),
}
