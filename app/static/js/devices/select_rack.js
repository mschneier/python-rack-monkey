window.addEventListener("load", () => {
    const search = new URLSearchParams(window.location.search);
    const sel_rack = search.get("sel_rack");
    const racks = [...document.getElementById("rack_name").getElementsByTagName("option")];
    racks.forEach(rack => {
        if (!rack.value) {
            rack.removeAttribute("selected");
        }
        if (rack.value == sel_rack) {
            rack.setAttribute("selected", "");
        }
    });
});
