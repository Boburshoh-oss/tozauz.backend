import {useState} from "react";
import {IconButton} from "@mui/material";
import ModeEditOutlineIcon from "@mui/icons-material/ModeEditOutline";

import {User} from "../../types/users.types";
import {updateUser} from "../../services/users.services";
import FullScreenDialog from '../../components/FullScreenDialog'
import UserEditForm from "./UserEditForm";
import Toast from "../../components/Toast";
import Backdrop from "@mui/material/Backdrop";
import CircularProgress from "@mui/material/CircularProgress";

interface Props {
    setLoad: (val: boolean) => void;
    user: User;
}


const UserUpdate = (props: Props) => {
    const {setLoad, user} = props;

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
        updateUser(user).then(() => {
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
            <IconButton
                aria-label="view"
                onClick={() => setOpen(true)}
            >
                <ModeEditOutlineIcon/>
            </IconButton>
            <FullScreenDialog
                title="Foydalanuvchi ma'lumotlarini o'zgartirish"
                open={open}
                handleClose={handleClose}
            >
                <UserEditForm user={user} onSubmit={onSubmit}/>
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
                message="Foydalanuvchi muvaffaqiyatli yangilandi"
                isOpen={openSuccessToast}
                handleClose={() => setOpenSuccessToast(false)}
            />
        </div>
    )
}

export default UserUpdate