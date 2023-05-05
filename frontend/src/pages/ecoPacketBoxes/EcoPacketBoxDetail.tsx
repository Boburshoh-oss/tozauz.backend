import './ecoPacketBoxDetail.scss'

import React, {useEffect, useState} from "react";
import {useParams} from "react-router-dom";
import Paper from "@mui/material/Paper";
import {ecoPacketBoxesServices} from "../../services/ecoPacket/ecoPacketBoxes.services";
import {formatDateTime} from "../../services/utils";

const EcoPacketBoxDetail = () => {

    const {boxId} = useParams<{ boxId: string }>();

    const [box, setBox] = useState<any>(null);

    useEffect(() => {
        if (typeof boxId === 'undefined') return;
        ecoPacketBoxesServices.getOne(boxId).then((res: any) => {
            setBox(res.data);
        })
    }, [boxId]);

    return (
        <div className={"boxDetail"}>
            <Paper elevation={3} className="header">
                <h2 className="title">Quti ma'lumotlari</h2>
                {box && (
                    <div className="content">
                        <div className="item">
                            <div className="label">Nomi</div>
                            <div className="value">{box.name}</div>
                        </div>

                        <span className="divider"></span>

                        <div className="item">
                            <div className="label">Sim module</div>
                            <div className="value">{box.sim_module}</div>
                        </div>

                        <span className="divider"></span>

                        <div className="item">
                            <div className="label">Qr Kod</div>
                            <div className="value">{box.qr_code}</div>
                        </div>

                        <span className="divider"></span>

                        <div className="item">
                            <div className="label">Quti qo'shilgan sanasi</div>
                            <div className="value">{formatDateTime(box.created_at)}</div>
                        </div>

                        <span className="divider"></span>

                        <div className="item">
                            Button
                        </div>

                    </div>
                )}
            </Paper>
        </div>
    )
}

export default EcoPacketBoxDetail