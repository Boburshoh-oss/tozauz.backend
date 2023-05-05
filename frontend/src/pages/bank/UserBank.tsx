import './userBank.scss'

import React from 'react'
import {useParams} from "react-router-dom";

import bankAccountServices from "../../services/bank/bankAccount";
import Paper from "@mui/material/Paper";
import UserEarnings from "./UserEarnings";
import UserPayouts from "./UserPayOuts";
import PayOutCreate from "./PayOutCreate";
import {numberWithCommas} from "../../services/utils";


const UserBank = () => {
    const {userId} = useParams<{ userId: string }>();
    const [userBank, setUserBank] = React.useState<any>(undefined)

    const [earningSumma, setEarningSumma] = React.useState(0)
    const [payOutSumma, setPayOutSumma] = React.useState(0)

    const [reloadPayOut, setReloadPayOut] = React.useState(1)

    React.useEffect(() => {
        if (userId === undefined) return
        bankAccountServices.get(userId).then(res => {
            setUserBank(res)
        })
    }, [userId, reloadPayOut])

    return (
        <div className="userBank">
            {userBank && (
                <>
                    {userBank.error
                        ? (
                            <Paper elevation={3} className="header">
                                <h1>Bank hisobi topilmadi</h1>
                            </Paper>
                        )
                        : (
                            <>
                                <Paper elevation={3} className="header">
                                    <h2 className="title">Bank Account</h2>
                                    <div className="content">
                                        <div className="item">
                                            <div className="label">Foydalanuvchi</div>
                                            <div
                                                className="value">{userBank.user?.last_name} {userBank.user?.first_name}</div>
                                        </div>

                                        <span className="divider"></span>

                                        <div className="item">
                                            <div className="label">Telefon raqami</div>
                                            <div className="value">{userBank.user?.phone_number}</div>
                                        </div>

                                        <span className="divider"></span>

                                        <div className="item">
                                            <div className="label">Hisob raqami</div>
                                            <div className="value">{userBank.id}</div>
                                        </div>

                                        <span className="divider"></span>

                                        <div className="item">
                                            <div className="label">Hisob mablag'i</div>
                                            <div className="value">{numberWithCommas(userBank.capital)}</div>
                                        </div>

                                        <span className="divider"></span>

                                        <div className="item">
                                            <PayOutCreate reload={reloadPayOut} setLoadPayOut={setReloadPayOut}
                                                          userId={userId}/>
                                        </div>

                                        <div></div>
                                    </div>
                                </Paper>
                                <div className="body">
                                    <div className="tableContainer left">
                                        <h2 className="title green">
                                            Kirimlar (Ishlab topilgan) <br/> {numberWithCommas(earningSumma)} so'm
                                        </h2>
                                        <Paper elevation={3}>
                                            <UserEarnings userId={userId} setEarningSumma={setEarningSumma}/>
                                        </Paper>
                                    </div>
                                    <div className="tableContainer right">
                                        <h2 className="title red">
                                            Chiqimlar (Yechib olingan) <br/> {numberWithCommas(payOutSumma)} so'm
                                        </h2>
                                        <Paper elevation={3}>
                                            <UserPayouts reload={reloadPayOut} userId={userId} setPayOutSumma={setPayOutSumma}/>
                                        </Paper>
                                    </div>
                                </div>
                            </>
                        )
                    }

                </>
            )
            }
        </div>
    )
}

export default UserBank