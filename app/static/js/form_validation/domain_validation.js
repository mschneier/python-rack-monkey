$(function () {
    $("#domain").validate({
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
            name: "Please enter the domain's name.",
            description: "The description must be less than 500 characters.",
            notes: "The domain's notes must be less than 500 characters."
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this domain?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
