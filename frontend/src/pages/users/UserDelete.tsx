import { useState } from "react";

import { IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

import ConfirmDialog from "../../components/ConfirmDialog"
import { deleteUser } from "../../services/users.services";

const UserDelete = (props: any) => {

    const [open, setOpen] = useState(false)

    const { row, setLoad } = props

    const showDialog = () => {
        setOpen(true)
    }

    const hideDialog = () => {
        setOpen(false)
    }

    const handleDelete = () => {
        setOpen(false)
        deleteUser(row.id).then(() => {
            setLoad(true)
        })
    }

    return (
        <div>
            <IconButton
                aria-label="delete"
                onClick={showDialog}
            >
                <DeleteIcon />
            </IconButton>

            <ConfirmDialog
                open={open}
                title="Delete user"
                content="Are you sure to delete this user?"
                cancelText="Cancel"
                confirmText="Delete"
                onConfirm={handleDelete}
                onCancel={hideDialog}
            />
        </div>
    )
}

export default UserDelete