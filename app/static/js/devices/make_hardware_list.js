document.getElementById("manufacturer").addEventListener("change", make_hardware_list);
window.addEventListener("load", () => {
    const url = window.location.href;
    if (url.indexOf("/update/") < 0) {
        make_hardware_list();
    }
});

function make_hardware_list() {
    const manufacturer_sel = document.getElementById("manufacturer").selectedIndex;
    const manufacturer = document.getElementById("manufacturer").getElementsByTagName("option")[manufacturer_sel].innerText;
    const model_sel = document.getElementById("model");
    const hard_models = document.getElementById("hard_models").getElementsByTagName("li");
    let options = "";
    for (let i = 0; i < hard_models.length; i++) {
        const model = hard_models[i].innerText.split(", ");
        const id = model[0];
        const name = model[1];
        const model_manufacturer = model[2];
        if (manufacturer == model_manufacturer) {
            options += `<option value="${id}">${name}</option>`;
        }
    }
    if (manufacturer != "Select Manufacturer") {
        model_sel.removeAttribute("disabled");
        model_sel.innerHTML = options;
    } else {
        model_sel.setAttribute("disabled", "");
        model_sel.innerHTML = "<option value=''>Select a Manufacturer First</option>";
    }
}
