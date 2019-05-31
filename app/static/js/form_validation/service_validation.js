$(function () {
    $("#service").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            description: {
                rangelength: [0, 500]
            },
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the service level's name.",
                rangelength: "Name must be less than 100 characters long."
            },
            description: "Description must be less than 500 characters long.",
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
            const msg = confirm(`Are you sure you want to ${type} this service?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
