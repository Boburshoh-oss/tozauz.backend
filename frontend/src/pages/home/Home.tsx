import "./home.scss"

import Widget from "../../components/widget/Widget"
import Featured from "../../components/featured/Featured"
import Chart from "../../components/chart/Chart"
// import DataTable from "../../components/table/Table"

const Home = () => {
    return (
        <div className="home">
            <div className="widgets">
                <Widget type="users" />
                <Widget type="earnings" />
                <Widget type="balance" />
                <Widget type="orders" />
            </div>
            <div className="charts">
                <Featured />
                <Chart />
            </div>
            {/*<div className="listContainer">*/}
            {/*    <div className="listTitle">Latest Transactions</div>*/}
            {/*    <DataTable />*/}
            {/*</div>*/}
        </div>
    )
}

export default Home
