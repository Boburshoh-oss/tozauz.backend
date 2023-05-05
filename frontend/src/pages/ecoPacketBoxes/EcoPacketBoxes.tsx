import './ecoPacketBoxes.scss'

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

import {ecoPacketBoxesServices} from '../../services/ecoPacket/ecoPacketBoxes.services';
import {formatDateTime} from "../../services/utils";
import {categoriesServices} from "../../services/categories.services";
import {Link} from "react-router-dom";

const BoxCard = ({box}: any) => (
    <Box sx={{minWidth: 275}}>
        <Card variant="outlined">
            <CardContent>
                <Typography sx={{fontSize: 14}} color="text.secondary" gutterBottom>
                    {formatDateTime(box.cycle_created_at) || 'Ishga tushirilmagan'}
                </Typography>
                <Typography variant="h5" component="div">
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                    }}>
                        <span>{box.name}</span>
                        <span>{box.state || 0}%</span>
                    </div>
                </Typography>
                <Typography sx={{mb: 1.5}} color="text.secondary">
                    {box.category?.name}
                </Typography>
                <Typography variant="body2">
                    Sim moduli/Qr Kod: <i>{box.sim_module}</i>
                </Typography>
            </CardContent>
            <CardActions>
                <Link to={`/boxes/${box.id}`}>
                    <Button size="medium">Batafsil</Button>
                </Link>
            </CardActions>
        </Card>
    </Box>
);

const EcoPacketBoxes = () => {
    const [rows, setRows] = React.useState<any>([]);

    const [categories, setCategories] = React.useState<any>([]);

    React.useEffect(() => {
        ecoPacketBoxesServices.getAll().then((res: any) => {
            setRows(res.data);
        });
    }, []);

    React.useEffect(() => {
        categoriesServices.categories().then((res: any) => {
            setCategories(res);
        });
    }, []);

    return (
        <div className='ecoPacketBoxes'>
            <div
                className="header"
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '20px'
                }}
            >
                <h2>Header</h2>
                <Button variant="contained">Qo'shish</Button>
            </div>
            <div className="content">
                {
                    rows.map((row: any) => {
                        row.category = categories?.find((category: any) => category.id === row.category);
                        return (
                            <div
                                className="card"
                                key={row.id}
                                style={{
                                    border: '3px solid',
                                    borderRadius: '5px',
                                    borderColor: row.state > 80 ? 'red' : 'green'
                                }}
                            >
                                <BoxCard
                                    box={row}
                                />
                            </div>
                        )
                    })
                }
            </div>
        </div>
    )
}

export default EcoPacketBoxes