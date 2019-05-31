document.getElementById("reset_button").addEventListener("click", () => {
    const url = window.location.href;
    if (url.includes("asset")) {
        window.location.href = "/view/devices/asset/";
    } else if (url.includes("extended")) {
        window.location.href = "/view/devices/extended/";
    } else if (url.includes("unracked")) {
        window.location.href = "/view/devices/unracked/";
    } else if (url.includes("search")) {
        window.location.href = "/view/devices/search/";
    } else {
        window.location.href = "/view/devices/";
    }
});
