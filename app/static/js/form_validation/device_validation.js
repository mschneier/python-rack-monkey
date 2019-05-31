$.validator.addMethod(
    "regex",
    function (value, element, regexp) {
        const re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    "Please check your input."
);
$(function () {
    $("#device").validate({
        rules: {
            dev_name: {
                required: true,
                rangelength: [1, 99],
                remote: {
                    type: "POST",
                    url: "/view/device_names/check_name/",
                    data: {
                        "dev_name": function () {
                            return $("#dev_name").val();
                        },
                        "type": "new",
                    },
                    dataType: "json",
                    onkeyup: false,
                }
            },
            domain: {
                min: 1,
                required: true,
            },
            rack_name: {
                required: true,
                min: 1
            },
            rack_pos: "required",
            manufacturer: {
                required: true,
                min: 1
            },
            model: "required",
            os: {
                required: true,
                min: 1
            },
            role: {
                required: true,
                min: 1
            },
            customer: {
                required: true,
                min: 1
            },
            service: {
                required: true,
                min: 1
            },
            key: {
                remote: {
                    type: "POST",
                    url: "/view/oses/check_key/",
                    data: {
                        "key": function () {
                            return $("#key").val();
                        },
                        "type": "new",
                    },
                    dataType: "json",
                    onkeyup: false,
                }
            },
            asset: {
                remote: {
                    type: "POST",
                    url: "/view/assets/check_asset/",
                    data: {
                        "asset": function () {
                            return $("#asset").val();
                        },
                        "type": "new",
                    },
                    dataType: "json",
                    onkeyup: false,
                }
            },
            serial: {
                remote: {
                    type: "POST",
                    url: "/view/serials/check_serial/",
                    data: {
                        "serial": function () {
                            return $("#serial").val();
                        },
                        "type": "new",
                    },
                    dataType: "json",
                    onkeyup: false,
                }
            },
            purchased: {
                regex: "(?:19|20)[0-9]{2}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1[0-9]|2[0-9])|(?:(?!02)(?:0[1-9]|1[0-2])-(?:30))|(?:(?:0[13578]|1[02])-31))"
            },
            notes: {
                rangelength: [0, 500]
            }
        },
        messages: {
            dev_name: {
                required: "Please enter the device's name.",
                rangelength: "Device name must be less than 100 characters.",
                remote: "This device name is already in use."
            },
            domain: "Please select the device's domain",
            rack_name: "Please select the device's rack.",
            rack_pos: "Please select the device's position.",
            manufacturer: "Please select the device's manufacturer.",
            model: "Please select the device's model.",
            os: "Please select the device's OS.",
            role: "Please select the device's role",
            customer: "Please select the device's customer",
            service: "Please select the device's service level.",
            key: "This licence key is already in use.",
            asset: "This asset # is already in use.",
            serial: "This serial # is already in use.",
            purchased: "Purchased date must be formatted in (YYYY-MM-DD) form.",
            notes: "Device notes must be less than 500 characters long."
        },
        submitHandler: (form) => {
            const url = window.location.href;
            let type = "";
            if (url.indexOf("/add/") >= 0) {
                type = "add";
            } else {
                type = "update";
            }
            const msg = confirm(`Are you sure you want to ${type} this device?`);
            if (msg) {
                form.submit();
            }
        }
    });
});
