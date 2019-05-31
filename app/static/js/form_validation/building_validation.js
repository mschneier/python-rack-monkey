$.validator.addMethod(
    "lessThan",
    function (value, element) {
        const name = $("#name").val().length;
        const short = value.length;
        return this.optional(element) || short < name;
    },
    "Short name must be shorter than full name."
);

$(function () {
    $("#building").validate({
        rules: {
            name: {
                required: true,
                rangelength: [1, 99]
            },
            short: "lessThan",
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            name: {
                required: "Please enter the building's name.",
                rangelength: "Name must be less than 100 characters long."
            },
            short: "Short name must be shorter than full name.",
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
            const msg = confirm(`Are you sure you want to ${type} this building?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
