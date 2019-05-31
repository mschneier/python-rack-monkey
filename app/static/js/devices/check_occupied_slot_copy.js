["blur", "change", "click", "keydown", "keyup"].forEach(event => {
    document.getElementById("rack_pos").addEventListener(event, check_occupied_slot);
});
["blur", "change", "click", "keydown", "keyup"].forEach(event => {
    document.getElementById("model").addEventListener(event, check_occupied_slot);
});
document.getElementById("rack_name").addEventListener("change", set_max_rack_pos);
window.addEventListener("load", check_occupied_slot);
window.addEventListener("load", set_max_rack_pos);

function check_occupied_slot() {
    const rack = document.getElementById("rack_name").value;
    const rack_pos = document.getElementById("rack_pos").value;
    if (rack && rack_pos) {
        const model_id = document.getElementById("model").value;
        const hardware_models = document.getElementById("hard_models").getElementsByTagName("li");
        let size = 0;
        for (let i = 0; i < hardware_models.length; i++) {
            const model = hardware_models[i].innerText.split(", ");
            const id = model[0];
            if (id == model_id) {
                size = model[3];
            }
        }
        const button = document.getElementById("submitBtn");
        const rack_msg = document.getElementById("rack_msg");
        rack_msg.style.display = "";
        rack_msg.innerText = "Checking availability...";
        const occupied = document.getElementById("occupied").innerText.split(" ");
        if (occupied.indexOf(rack_pos) >= 0) {
            rack_msg.style.display = "";
            rack_msg.classList = "error";
            rack_msg.innerText = "This slot is filled.";
            button.setAttribute("disabled", "");
        } else {
            for (let j = 1; j < size; j++) {
                let pos = Number(rack_pos) + j;
                if (occupied.indexOf(pos.toString()) >= 0) {
                    rack_msg.style.display = "";
                    rack_msg.classList = "error";
                    rack_msg.innerText = "Slot is empty but hardware model is too big for space.";
                    button.setAttribute("disabled", "");
                    return;
                }
            }
            rack_msg.style.display = "";
            rack_msg.classList = "available";
            rack_msg.innerText = "Available!";
            button.removeAttribute("disabled");
        }
    } else {
        document.getElementById("rack_msg").innerText = "";
        document.getElementById("rack_msg").style.display = "none";
        return;
    }
    if (rack) {
        document.getElementById("rack_pos").removeAttribute("disabled");
    }
}

function set_max_rack_pos() {
    const rack_sizes = document.getElementById("rack_sizes").getElementsByTagName("li");
    const rack_pos = document.getElementById("rack_pos");
    const sel_rack = document.getElementById("rack_name").value;
    if (rack_pos.value) {
        document.getElementById("rack_msg").classList = "rack_loading";
        document.getElementById("rack_msg").innerText = "Checking Availability...";
    }
    if (sel_rack) {
        for (let i = 0; i < rack_sizes.length; i++) {
            const rack = rack_sizes[i].innerText.split(", ");
            const id = rack[0];
            const size = rack[1];
            if (sel_rack == id) {
                rack_pos.setAttribute("max", size);
                rack_pos.removeAttribute("disabled");
            }
        }
        fill_occupied_slots(sel_rack);
    } else {
        rack_pos.setAttribute("disabled", "");
        rack_pos.value = "";
    }
}

function fill_occupied_slots(id) {
    const occupied_slots = document.getElementById("occupied_slots").getElementsByTagName("li");
    const occupied = document.getElementById("occupied");
    let slots = "";
    for (let i = 0; i < occupied_slots.length; i++) {
        let occ_slots = occupied_slots[i].innerText.split(", ");
        let rack = occ_slots[0].replace("\"", "");
        if (id == rack) {
            slots = occ_slots[1].replace("\"", "");
        }
    }
    occupied.innerText = slots;
    check_occupied_slot();
}
