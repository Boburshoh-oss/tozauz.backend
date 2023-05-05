import '../qrcode/table.scss'

import React, {useEffect, useState} from "react";
import {Link} from "react-router-dom";
import Select from "react-select";
import {TextField} from "@mui/material";

import {Column} from "../../types/table.types";
import {CategoryObj} from "../../types/categories.types";
import {UserFetchResponse} from "../../types/users.types";
import DataTable from "../../components/dataTable/DataTable";
import {categoriesServices} from "../../services/categories.services";
import {packetServices} from "../../services/qrcodes/packet.services";
import {formatDateTime} from "../../services/utils";

const OneTimePacket = (props: any) => {

    const [categories, setCategories] = useState<CategoryObj[]>([]);
    const [rows, setRows] = useState<UserFetchResponse>({
        count: 0,
        next: null,
        previous: null,
        results: [],
    } as UserFetchResponse);

    const [pageIndex, setPageIndex] = useState(0);
    const [pageSize, setPageSize] = useState(5);
    const [search, setSearch] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<any>('');

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        categoriesServices.categories().then((res) => {
            setCategories(res);
        });
    }, [])

    useEffect(() => {
        setLoading(true)
        packetServices.get(
            pageIndex + 1,
            pageSize,
            selectedCategory,
            search
        ).then((res) => {
            setRows(res.data)
            setLoading(false)
        })
    }, [pageIndex, pageSize, selectedCategory, search])

    const columns: readonly Column[] = [
        {
            id: "qr_code",
            label: "Qr Code",
            format: (row: any) => {
                return row.qr_code;
            }
        },
        {
            id: "employee",
            label: "Hodim",
            align: "center",
            format: (row: any) => {
                return <Link to={`/user-bank/${row.employee.id}`}>{row.employee.first_name}</Link>;
            }
        },
        {
            id: "category",
            label: "Kategoriya",
            align: "center",
            format: (row: any) => {
                const category = categories.find((item: CategoryObj) => item.id === row.category);
                return category?.name;
            }
        },
        {
            id: "created_at",
            label: "Yaratilgan vaqti",
            align: "center",
            format: (row: any) => {
                return formatDateTime(row.created_at);
            }
        },
        {
            id: "scannered_at",
            label: "Skaner qilingan vaqti",
            align: "right",
            format: (row: any) => {
                return formatDateTime(row.scannered_at);
            }
        },
    ]

    const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
    }

    const handleCategorySelect = (event: any) => {
        setSelectedCategory(event.value);
    }

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
        <>
            <div className="tableHeader">
                <div className="tableFilter">
                    <TextField
                        label="Qidirish"
                        type="search"
                        sx={{
                            backgroundColor: "white",
                            borderRadius: "5px",
                        }}
                        size={"small"}
                        onChange={handleSearch}
                    />
                    <Select
                        options={
                            [
                                {value: "", label: "Barchasi"},
                                ...categories.map((item: any) => {
                                    return {value: item.id, label: item.name}
                                })
                            ]
                        }
                        defaultValue={{value: "", label: "Barchasi"}}
                        className="basic-multi-select"
                        classNamePrefix="select"
                        name="category"
                        isSearchable={true}
                        onChange={(e: any) => {
                            handleCategorySelect(e);
                        }}
                    />
                </div>
            </div>
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
        </>

    )
}

export default OneTimePacket;