$(function () {
    $("#login_form").validate({
        rules: {
            username: {
                required: true,
                rangelength: [1, 99]
            },
            password: {
                required: true,
                rangelength: [1, 999]
            }
        },
        messages: {
            username: {
                required: "Please enter your username.",
                rangelength: "Username must be less than 100 characters long."
            },
            password: {
                required: "Please enter your password.",
                rangelength: "Password must be less than 1000 characters long."
            }
        },
    });
});
