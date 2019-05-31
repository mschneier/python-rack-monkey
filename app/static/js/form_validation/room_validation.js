$(function () {
    $("#room").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            building: {
                required: true,
                min: 1,
            },
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the room's name.",
                rangelength: "Name must be less than 100 characters long."
            },
            building: "Please select the buidling the room is in.",
            notes: "Notes must be less than 500 characters."
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this room?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
