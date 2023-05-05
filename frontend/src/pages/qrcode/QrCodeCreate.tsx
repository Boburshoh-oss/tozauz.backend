import './qrCodeCreate.scss'
import { useState } from 'react';

import { Backdrop, Button, CircularProgress, Container } from '@mui/material'
import Select from 'react-select';
import { categoriesServices } from '../../services/categories.services';
import { CategoryObj } from '../../types/categories.types';
import { createQrCodes } from '../../services/createQrCodes';

function exportUserInfo(qrCodes: string, fileName: string = "qr-codes.txt") {
    const blob = new Blob([qrCodes], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.download = fileName;
    link.href = url;
    link.click();
}


const QrCodeCreate = () => {
    const [categoryOptions, setCategoryOptions] = useState([] as { value: number, label: string }[])
    const [isLoading, setIsLoading] = useState(false)

    const [form, setForm] = useState({
        type: '',
        category: '',
        quantity: 0
    })

    useState(() => {
        setIsLoading(true)
        if (categoryOptions.length === 0) {
            categoriesServices.categories().then(res => {
                setCategoryOptions(res.map((item: CategoryObj) => {
                    return { value: item.id, label: item.name }
                }))
                setIsLoading(false)
            })
        }
    })

    const qrCodeTypes = [
        { value: 'box', label: 'Eko Paket' },
        { value: 'packet', label: 'Bir martalik' },
    ]

    const onSubmit = (e: any) => {
        e.preventDefault()

        if (!form.type) {
            alert('Turi tanlang')
            return
        }

        if (!form.category) {
            alert('Kategoriyani tanlang')
            return
        }

        if (!form.quantity) {
            alert('Miqdorini kiriting')
            return
        }

        if (form.quantity > 10000) {
            alert('Miqdor 10000 dan katta bo\'lmasligi kerak')
            return
        }

        setIsLoading(true)
        createQrCodes(form).then(res => {
            let qrCodes = ''
            res.data.qr_codes.forEach((item: any) => {
                qrCodes += item.qr_code + '\n'
            })
            exportUserInfo(
                qrCodes,
                `qr-codes-${form.type}-${categoryOptions.find((item) => item.value = Number(form.category))?.label}-${form.quantity}.txt`
            )
            setIsLoading(false)
        }).catch(() => {
            alert('Kutilmagan xatolik yuz berdi')
            setIsLoading(false)
        })
    }

    return (
        <div className="qrcodes">

            <Container maxWidth="sm">
                <h1 className='title'>Yangi QR KODLAR</h1>

                <div className="formElement">
                    <Select
                        className="basic-single"
                        classNamePrefix="select"
                        name="type"
                        onChange={(e: any) => setForm({ ...form, type: e.value })}
                        options={qrCodeTypes}
                        placeholder="Turi"
                    />
                </div>

                <div className="formElement">
                    <Select
                        className="basic-single"
                        classNamePrefix="select"
                        isLoading={isLoading}
                        name="category"
                        onChange={(e: any) => setForm({ ...form, category: e.value })}
                        options={categoryOptions}
                        placeholder="Kategoriyasi"
                    />
                </div>

                <div className="formElement">
                    <input
                        onChange={(e: any) => setForm({ ...form, quantity: Number(e.target.value) })}
                        className='numberInput'
                        name="quantity"
                        type="number"
                        placeholder="Miqdori"
                        maxLength={5}
                    />
                </div>

                <div className="formElement submitBtn">
                    <Button onClick={onSubmit} fullWidth variant="contained">Buyurtma berish</Button>
                </div>

            </Container>

            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                open={isLoading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        </div>
    )
}

export default QrCodeCreate
