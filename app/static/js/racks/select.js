document.getElementById("select_all").addEventListener("click", (e) => {
    e.preventDefault();
    const inputs = [...document.getElementById("rack_table").getElementsByTagName("input")];
    inputs.forEach(input => {
        if (input.type == "checkbox") {
            if (input.checked == true) {
                input.checked = false;
            } else {
                input.checked = true;
            }
        }
    });
});

["change", "click", "load"].forEach(event => {
    document.addEventListener(event, () => {
        let checks = [];
        const inputs = [...document.getElementById("rack_table").getElementsByTagName("input")].slice(1);
        inputs.forEach(input => {
            if (input.type == "checkbox" && input.checked == true) {
                if (input.checked == true) {
                    checks.push(input);
                }
            }
        });
        if (checks.length > 0) {
            document.getElementById("view_sel_racks").removeAttribute("disabled");
        } else {
            document.getElementById("view_sel_racks").setAttribute("disabled", "");
        }
    });
});

document.getElementById("view_sel_racks").addEventListener("click", () => {
    // Get all inputs except the 1st two (search and all_check toggle).
    const inputs = [...document.getElementById("rack_table").getElementsByTagName("input")].slice(1);
    let rack_ids = "";
    inputs.forEach(input => {
        if (input.type == "checkbox" && input.checked == true) {
            rack_ids += input.value + ",";
        }
    });
    if (rack_ids.length > 0) {
        window.location.href = `/view/racks/list/simple/?rack_list=${rack_ids}`;
    }
});
