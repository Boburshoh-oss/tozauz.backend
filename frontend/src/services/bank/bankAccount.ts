import {requests} from "../requests";

const bankAccountServices = {

    getAll: async () => {
        const bankAccounts = await requests('GET', 'bank/bank-accounts/');
        return bankAccounts.data;
    },

    get: async (userId: string) => {
        const bankAccount = await requests('GET', `bank/admin-bank-account/${userId}/`);
        return bankAccount.data;
    },
}

export default bankAccountServices;
