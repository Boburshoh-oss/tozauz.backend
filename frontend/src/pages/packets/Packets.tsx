import '../qrcode/qrCodeList.scss';
import Paper from "@mui/material/Paper";
import EcoPacket from "./EcoPacket";
import OneTimePacket from "./OneTimePacket";

const Packets = () => {
    return (
        <div className="qrcodes">
            <div className="tableContainer left">
                <h3>Eko paket</h3>
                <Paper elevation={3}>
                    <EcoPacket/>
                </Paper>
            </div>
            <div className="tableContainer right">
                <h3>Bir martalik </h3>
                <Paper elevation={3}>
                    <OneTimePacket/>
                </Paper>
            </div>
        </div>
    );
}

export default Packets;