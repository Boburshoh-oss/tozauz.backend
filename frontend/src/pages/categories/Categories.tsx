import './categories.scss'

import { useEffect, useState } from "react"

import { categoriesServices } from "../../services/categories.services"
import { CategoryObj } from "../../types/categories.types"

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import { CardActionArea, CardActions, Divider } from '@mui/material';

import CategoryEditDialog from './CategoryEditDialog'

function CardItem({ category, loadList }: { category: CategoryObj, loadList: (value: boolean) => void }) {
    return (
        <Card sx={{
            maxWidth: 345,
            WebkitBoxShadow: "2px 4px 10px 1px rgba(0, 0, 0, 0.47)",
            boxShadow: "2px 4px 10px 1px rgba(201, 201, 201, 0.47)"
        }}>
            <CardActionArea>
                <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
                        {category.name}
                    </Typography>
                    <Divider variant="fullWidth" sx={{ margin: "10px 0" }} />
                    <Typography variant="body2" color="text.secondary">
                        Beriladigan summa: <b>{category.summa}</b>
                    </Typography>
                    <Divider variant="fullWidth" sx={{ margin: "10px 0" }} />
                    <Typography variant="body2" color="text.secondary">
                        Kategoriyaga bog'langanlar: <b>{category.count_user || 0} ta</b>
                    </Typography>
                </CardContent>
            </CardActionArea>
            <CardActions>
                <CategoryEditDialog category={category} loadList={loadList} />
            </CardActions>
        </Card>
    );
}

const Categories = () => {
    const [fromServer, setFromServer] = useState(false);
    const [categories, setCategories] = useState([] as CategoryObj[])

    useEffect(() => {
        categoriesServices.categories(fromServer).then((res) => {
            setCategories(res)
        })
        setFromServer(false)
    }, [fromServer])

    return (
        <div className='categories'>
            <div className="cards-list">
                {categories.map((category) => (
                    <CardItem category={category} key={category.id} loadList={setFromServer} />
                ))}
            </div>
        </div>
    )
}

export default Categories