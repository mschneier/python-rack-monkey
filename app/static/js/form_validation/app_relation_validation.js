$(function () {
    $("#app_relation").validate({
        rules: {
            relationship: {
                required: true,
                min: 1,
            },
            device: {
                required: true,
                min: 1,
            }
        },
        messages: {
            relationship: "Please pick relationship type.",
            device: "Please pick device.",
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this app device relationship?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
