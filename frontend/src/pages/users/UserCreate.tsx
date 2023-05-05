import { useState } from 'react'
import FullScreenDialog from '../../components/FullScreenDialog'
import { Button } from '@mui/material';
import PersonAddAlt1Icon from '@mui/icons-material/PersonAddAlt1';

import UserForm from './UserCreationForm'
import { User } from '../../types/users.types';

import { createUser } from '../../services/users.services';
import Toast from '../../components/Toast';

import Backdrop from '@mui/material/Backdrop';
import CircularProgress from '@mui/material/CircularProgress';

interface Props {
    setLoad: (val: boolean) => void;
}

const UserCreate = (props: Props) => {

    const { setLoad } = props;
    const [open, setOpen] = useState(false)
    const [openErrorToast, setOpenErrorToast] = useState(false)
    const [openSuccessToast, setOpenSuccessToast] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')

    const handleClose = () => {
        setOpen(false)
    }

    const onSubmit = (user: User) => {
        setIsLoading(true)
        createUser(user).then(() => {
            setIsLoading(false)
            setOpen(false)
            setOpenSuccessToast(true)
            setLoad(true)
        }).catch((err) => {
            if (err.response.data.phone_number?.[0] === 'user with this phone number already exists.') {
                setErrorMessage('Bunday telefon raqam bilan ro\'yhatdan foydalanuvchi mavjud')
            } else if (err.response.data.car_number?.[0] === 'Ensure this field has no more than 10 characters.') {
                setErrorMessage('Avto raqami 10 ta belgidan oshmasligi kerak')
            } else {
                setErrorMessage('Xatolik yuz berdi')
            }
            setIsLoading(false)
            setOpenErrorToast(true)
        })
    }

    return (
        <div>
            <Button onClick={() => setOpen(true)}>
                <PersonAddAlt1Icon />
            </Button>
            <FullScreenDialog
                title="Yangi foydalanuvchi qo'shish"
                open={open}
                handleClose={handleClose}
            >
                <div style={{ marginTop: '10px' }}>
                    <UserForm onSubmit={onSubmit} />
                </div>
                <Toast
                    severity="error"
                    message={errorMessage}
                    isOpen={openErrorToast}
                    handleClose={() => setOpenErrorToast(false)}
                />
                <Backdrop
                    sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                    open={isLoading}
                >
                    <CircularProgress color="inherit" />
                </Backdrop>
            </FullScreenDialog>
            <Toast
                severity="success"
                message="Foydalanuvchi muvaffaqiyatli qo'shildi"
                isOpen={openSuccessToast}
                handleClose={() => setOpenSuccessToast(false)}
            />
        </div>
    )
}

export default UserCreate