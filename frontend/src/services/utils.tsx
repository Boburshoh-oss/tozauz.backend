export const formatDateTime = (date: string | undefined | null) => {
    if (!date) return "";

    const d = new Date(date);
    const year = d.getFullYear();
    const month = `0${d.getMonth() + 1}`.slice(-2);
    const _date = `0${d.getDate()}`.slice(-2);
    const hour = `0${d.getHours()}`.slice(-2);
    const minute = `0${d.getMinutes()}`.slice(-2);
    return (
        <span style={{
            color: "blue",
            fontWeight: "bold",
        }}>
            {year}-{month}-{_date} {hour}:{minute}
        </span>
    );
}


export function numberWithCommas(x: number | null | undefined): string {
    if (x === null || x === undefined) return "0";
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}