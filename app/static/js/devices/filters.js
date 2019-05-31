window.addEventListener("load", () => {
    const search = new URLSearchParams(window.location.search);
    const cust_val = search.get("customer");
    const cust_sel = document.getElementById("customer");
    const role_val = search.get("role");
    const role_sel = document.getElementById("role");
    const hard_val = search.get("hardware");
    const hard_sel = document.getElementById("hardware");
    const os_val = search.get("os");
    const os_sel = document.getElementById("os");
    if (cust_val && cust_val != "null") {
        cust_sel.value = cust_val;
    }
    if (role_val && role_val != "null") {
        role_sel.value = role_val;
    }
    if (hard_val && hard_val != "null") {
        hard_sel.value = hard_val;
    }
    if (os_val && os_val != "null") {
        os_sel.value = os_val;
    }
});

document.getElementById("filter_toggle").addEventListener("click", () => {
    const button = document.getElementById("filter_toggle");
    const filters = document.getElementById("filters");
    if (filters.style.display == "") {
        filters.style.display = "none";
        button.value = "Show Filters";
    } else {
        filters.style.display = "";
        button.value = "Hide Filters";
    }
});

document.getElementById("filters").addEventListener("change", () => {
    const url_string = window.location.href;
    const searchParams = new URLSearchParams(window.location.search);
    const sort = searchParams.get("sort");
    const cust_val = document.getElementById("customer").value;
    const role_val = document.getElementById("role_filter").value;
    const hard_val = document.getElementById("hardware_filter").value;
    const os_val = document.getElementById("os_filter").value;
    if (url_string.includes("asset")) {
        window.location.href = `/view/devices/asset/?sort=${sort}&customer=${cust_val}&role=${role_val}&hardware=${hard_val}&os=${os_val}`;
    } else if (url_string.includes("extended")) {
        window.location.href = `/view/devices/extended/?sort=${sort}&customer=${cust_val}&role=${role_val}&hardware=${hard_val}&os=${os_val}`;
    } else if (url_string.includes("unracked")) {
        window.location.href = `/view/devices/unracked/?sort=${sort}&customer=${cust_val}&role=${role_val}&hardware=${hard_val}&os=${os_val}`;
    } else if (url_string.includes("search")) {
        const search = searchParams.get("search");
        window.location.href = `/view/devices/search/?search=${search}&sort=${sort}&customer=${cust_val}&role=${role_val}&hardware=${hard_val}&os=${os_val}`;
    } else {
        window.location.href = `/view/devices/default/?sort=${sort}&customer=${cust_val}&role=${role_val}&hardware=${hard_val}&os=${os_val}`;
    }
});
