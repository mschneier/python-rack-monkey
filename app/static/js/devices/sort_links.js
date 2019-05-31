window.addEventListener("load", () => {
    const heads = document.getElementsByClassName("table_head");
    const url_string = window.location.search;
    const searchParams = new URLSearchParams(url_string);
    const customer = searchParams.get("customer");
    const role = searchParams.get("role");
    const hardware = searchParams.get("hardware");
    const os = searchParams.get("os");
    if (!window.location.href.includes("search")) {
        for (let i = 1; i < heads.length; i++) {
            const a = heads[i].getElementsByTagName("a")[0];
            a.href += `&customer=${customer}&role=${role}&hardware=${hardware}&os=${os}`;
        }
    } else {
        const search = searchParams.get("search");
        for (let i = 1; i < heads.length; i++) {
            const a = heads[i].getElementsByTagName("a")[0];
            a.href += `&search=${search}&customer=${customer}&role=${role}&hardware=${hardware}&os=${os}`;
        }
    }
});
