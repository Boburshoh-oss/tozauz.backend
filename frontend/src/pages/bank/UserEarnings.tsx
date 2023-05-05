import {Column} from "../../types/table.types";
import DataTable from "../../components/dataTable/DataTable";
import React, {useEffect, useState} from "react";
import {CategoryObj} from "../../types/categories.types";
import {categoriesServices} from "../../services/categories.services";
import {earningServices} from "../../services/earningServices";
import {formatDateTime, numberWithCommas} from "../../services/utils";

const UserEarnings = (props: any) => {
    const {userId, setEarningSumma} = props;
    const [categories, setCategories] = useState<CategoryObj[]>([]);
    const [rows, setRows] = useState<any>(undefined);

    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize, setPageSize] = useState(5);

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        categoriesServices.categories().then((res) => {
            setCategories(res);
        });
    }, [])

    useEffect(() => {
        setLoading(true)
        earningServices.getUserEarnings(userId, pageIndex + 1, pageSize).then((res) => {
            setRows(res.data)
            setEarningSumma(res.data.amount__sum)
            setLoading(false)
        })
    }, [userId, pageIndex, pageSize, setEarningSumma])

    const columns: readonly Column[] = [
        {
            id: "id",
            label: "Tranzaksiya raqami",
        },
        {
            id: "amount",
            label: "Miqdori",
            format: (row: any) => {
                return numberWithCommas(row.amount) + " so'm";
            }
        },
        {
            id: "created_at",
            label: "Vaqt",
            align: "center",
            format: (row: any) => {
                return formatDateTime(row.created_at);
            }
        },
        {
            id: "tarrif",
            label: "Kategoriya",
            align: "right",
            format: (row: any) => {
                const category = categories.find((item: CategoryObj) => item.id === row.tarrif);
                return category?.name;
            }
        }
    ]

    const handleChangePage = (event: unknown, newPage: number) => {
        setPageIndex(newPage);
    };

    const handleChangeRowsPerPage = (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        setPageSize(+event.target.value);
        setPageIndex(0);
    };

    return (
        <DataTable
            isLoading={loading}
            total={rows?.count}
            rows={rows?.results}
            columns={columns}
            page={pageIndex}
            rowsPerPage={pageSize}
            handleChangePage={handleChangePage}
            handleChangeRowsPerPage={handleChangeRowsPerPage}
        />
    )
}

export default UserEarnings