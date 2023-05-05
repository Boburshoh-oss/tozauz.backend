import "./widget.scss"
import React from "react";
import { WidgetProps } from "../../types/props.types";

import KeyboardArrowUpOutlinedIcon from "@mui/icons-material/KeyboardArrowUpOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import CurrencyExchangeOutlinedIcon from "@mui/icons-material/CurrencyExchangeOutlined";
import BalanceOutlinedIcon from "@mui/icons-material/BalanceOutlined";
import ShoppingCartOutlinedIcon from "@mui/icons-material/ShoppingCartOutlined";

const Widget = (props: WidgetProps) => {
    const { type } = props

    let title: string
    let icon: React.ReactNode

    switch (type) {
        case "users":
            title = "USERS";
            icon = (
                <PersonOutlinedIcon
                    className="icon"
                    style={{
                        color: "crimson",
                        backgroundColor: "rgb(255, 0, 0, 0.2)"
                    }}
                />
            )
            break

        case "earnings":
            title = "EARNINGS"
            icon = (
                <CurrencyExchangeOutlinedIcon
                    className="icon"
                    style={{
                        color: "green",
                        backgroundColor: "rgb(0, 255, 0, 0.2)"
                    }}
                />
            )
            break

        case "balance":
            title = "BALANCE"
            icon = (
                <BalanceOutlinedIcon
                    className="icon"
                    style={{
                        color: "golden",
                        backgroundColor: "rgb(218, 165, 32, 0.2)"
                    }}
                />
            )
            break

        case "orders":
            title = "ORDERS"
            icon = (
                <ShoppingCartOutlinedIcon
                    className="icon"
                    style={{
                        color: "purple",
                        backgroundColor: "rgb(128, 0, 128, 0.2)"
                    }}
                />
            )
            break

        default:
            title = ""
            icon = <></>
            break;
    }


    return (
        <div className="widget">
            <div className="left">
                <div className="title">{title}</div>
                <div className="counter">1223</div>
                <div className="link">See all users</div>
            </div>
            <div className="right">
                <div className="percentage positive">  {/* positive or negative */}
                    <KeyboardArrowUpOutlinedIcon />
                    20 %
                </div>
                {icon}
            </div>
        </div>
    )
}

export default Widget