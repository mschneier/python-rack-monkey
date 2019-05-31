$(function () {
    $("#os").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            developer: {
                required: true,
                min: 1,
            },
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the name of the OS.",
                rangelength: "Name must be less than 100 characters long."
            },
            developer: "Please choose the developer.",
            notes: "Notes must be less than 500 characters long."
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this OS?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
