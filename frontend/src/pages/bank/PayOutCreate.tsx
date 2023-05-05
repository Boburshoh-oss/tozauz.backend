import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import {payOutServices} from "../../services/payOutServices";
import CircularProgress from "@mui/material/CircularProgress";
import Backdrop from "@mui/material/Backdrop";
import Toast from "../../components/Toast";

export default function PayOutCreate(props: any) {
    const [open, setOpen] = React.useState(false);
    const [amount, setAmount] = React.useState(0)
    const [loading, setLoading] = React.useState(false)

    const [openErrorToast, setOpenErrorToast] = React.useState(false)
    const [errorMessage, setErrorMessage] = React.useState('')

    const {userId, reload, setLoadPayOut} = props

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleSubmit = () => {
        if (amount < 0) {
            setErrorMessage('Pul miqdori 0 dan yuqori bo\'lishi kerak')
            setOpenErrorToast(true)
            return
        }

        setLoading(true)
        payOutServices.createPayOut(userId, amount).then((res) => {
            setLoading(false)

            if (res?.data.error) {
                if (res.data.error === "The user's capital is insufficient. Please try paying less") {
                    setErrorMessage('Hisobda bunday miqdorda pul yo\'q.')
                } else {
                    setErrorMessage(res.data.error)
                }
                console.log(errorMessage)
                setOpenErrorToast(true)
                return
            }
            setLoadPayOut(reload + 1)
            setOpen(false)
        })
    }

    return (
        <div>
            <Button variant="contained" onClick={handleClickOpen}>
                Pul o'tkazish
            </Button>
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Pul o'tkazish</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Ushbu foydalanuvchi yoki ishchi uchun to'lovni amalga oshirish
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        id="amount"
                        label="Pul summasi (so'mda)"
                        type="number"
                        fullWidth
                        variant="standard"
                        onChange={(e) => setAmount(Number(e.target.value))}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Bekor qilish</Button>
                    <Button onClick={handleSubmit}>Ok</Button>
                </DialogActions>
                <Toast
                    severity="error"
                    message={errorMessage}
                    isOpen={openErrorToast}
                    handleClose={() => setOpenErrorToast(false)}
                />
                <Backdrop
                    sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                    open={loading}
                >
                    <CircularProgress color="inherit" />
                </Backdrop>
            </Dialog>
        </div>
    );
}