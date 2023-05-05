import { requests } from "./requests";

export const createQrCodes = (data: any) => {
    const { type, category, quantity } = data;

    const requestData = {
        num_of_qrcodes: quantity,
        category: category,
    }

    const url = type === 'box' ? 'ecopacket/create-eco-qr-codes/' : 'packet/create-packet-qr-codes/';

    return requests('POST', url, requestData);
}
