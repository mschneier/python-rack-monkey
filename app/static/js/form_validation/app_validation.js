$(function () {
    $("#app").validate({
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
                required: "Please enter the app name.",
                rangelength: "Name must be less than 100 characters."
            },
            description: "The description must be less than 500 characters.",
            notes: "The app's notes must be less than 500 characters."
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this app?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
