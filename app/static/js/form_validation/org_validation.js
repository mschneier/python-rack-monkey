$(function () {
    $("#org").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            descritption: {
                rangelength: [0, 500]
            },
            account: {
                rangelength: [0, 99]
            },
            types: "required",
            homepage: {
                url: true,
                rangelength: [0, 200]
            },
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the organization's name.",
                rangelength: "Name must be less than 100 characters long."
            },
            descritption: "Description must be less than 500 characters long.",
            account: "Account number must be less than 100 characters long.",
            types: "Please select at least one of the organization types.",
            homepage: {
                url: "Please enter a valid url.",
                rangelength: "Homepage must be less than 200 characters long."
            },
            notes: "Notes must be less than 500 characters long."
        },
        errorPlacement: function (error, element) {
            if (element.attr("name") == "types") {
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
            const msg = confirm(`Are you sure you want to ${type} this org?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
