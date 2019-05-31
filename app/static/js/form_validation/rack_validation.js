$(function () {
    $("#rack").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            room: {
                min: 1,
                required: true,
            },
            size: {
                required: true,
                range: [1, 99]
            },
            order: "required",
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the name of the rack.",
                rangelength: "Name must be less than 100 characters long."
            },
            room: "Please select the room the rack is located in.",
            size: {
                required: "Please select the rack's size.",
                range: "Size must be less than 100 units."
            },
            order: "Please select the numbering order.",
            notes: "Notes must be less than 500 characters long."
        },
        errorPlacement: function (error, element) {
            if (element.attr("name") == "order") {
                element.parent().parent().append(error);
            } else {
                error.insertAfter(element);
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
            const msg = confirm(`Are you sure you want to ${type} this rack?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
