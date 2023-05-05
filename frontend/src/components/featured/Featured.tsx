import "./featured.scss"
import "react-circular-progressbar/dist/styles.css"

import { CircularProgressbar } from "react-circular-progressbar"
import MoreVertOutlinedIcon from "@mui/icons-material/MoreVertOutlined"
import KeyboardArrowUpOutlinedIcon from "@mui/icons-material/KeyboardArrowUpOutlined"
import KeyboardArrowDownOutlinedIcon from "@mui/icons-material/KeyboardArrowDownOutlined"

const Featured = () => {
    return (
        <div className="featured">
            <div className="top">
                <h2 className="title">Featured</h2>
                <MoreVertOutlinedIcon className="icon" />
            </div>
            <div className="bottom">
                <div className="featuredChart">
                    <CircularProgressbar
                        value={70}
                        text="70 %"
                        strokeWidth={5}
                    />
                </div>
                <p className="title">Total sales made today</p>
                <p className="amout">$420</p>
                <p className="description">Lorem ipsum, dolor sit amet consectetur adipisicing elit. Unde, neque!</p>
                <div className="summary">
                    <div className="item">
                        <h4 className="itemTitle">Target</h4>
                        <div className="resultAmount negative">
                            <KeyboardArrowDownOutlinedIcon className="icon" />
                            $12.4k
                        </div>
                    </div>
                    <div className="item">
                        <h4 className="itemTitle">Target</h4>
                        <div className="resultAmount positive">
                            <KeyboardArrowUpOutlinedIcon className="icon" />
                            $12.4k
                        </div>
                    </div>
                    <div className="item">
                        <h4 className="itemTitle">Target</h4>
                        <div className="resultAmount positive">
                            <KeyboardArrowUpOutlinedIcon className="icon" />
                            $12.4k
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Featured