$(function () {
    $("#hardware").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            manufacturer: {
                required: true,
                min: 1,
            },
            size: {
                required: true,
                range: [1, 20]
            },
            image: {
                rangelength: [0, 200]
            },
            support: {
                url: true,
                rangelength: [0, 200]
            },
            spec: {
                url: true,
                rangelength: [0, 200]
            }
        },
        messages: {
            name: {
                required: "Please enter the hardware name.",
                rangelength: "Hardware's name must be less than 100 characters long."
            },
            manufacturer: "Please select the manufacturer",
            size: {
                required: "Please enter the hardware size.",
                range: "The size must be between 1 and 20 units"
            },
            image: {
                rangelength: "Image path must be less than 200 characters long."
            },
            support: {
                url: "Please enter a valid url",
                rangelength: "URL must be less than 200 characters long."
            },
            spec: {
                url: "Please enter a valid url",
                rangelength: "URL must be less than 200 characters long."
            }
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this hardware?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
