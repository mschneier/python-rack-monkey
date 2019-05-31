window.addEventListener("load", () => {
    const url = window.location.href;
    const msg = document.getElementById("msg");
    const values = msg.innerText.slice(1, -1).split(", ");
    const id = values[0];
    const device = values[1].slice(1, -1);
    let link = "";
    if (url.indexOf("/add/device/copy") >= 0) {
        link = `No device with this id. Did you mean to copy this device: <a href='/add/device/copy/${id}' title='Copy device ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/add/rack/copy") >= 0) {
        link = `No rack with this id. Did you mean to copy this rack: <a href='/add/rack/copy/${id}' title='Copy device ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/device") >= 0) {
        link = `No device with this id. Did you mean to update this device: <a href='/update/device/${id}' title='Update device ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/rack") >= 0) {
        link = `No rack with this id. Did you mean to update this rack: <a href='/update/rack/${id}' title='Update rack ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/app") >= 0) {
        link = `No app with this id. Did you mean to update this app: <a href='/update/app/${id}' title='Update app ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/building") >= 0) {
        link = `No building with this id. Did you mean to update this building: <a href='/update/building/${id}' title='Update building ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/domain") >= 0) {
        link = `No domain with this id. Did you mean to update this domain: <a href='/update/domain/${id}' title='Update domain ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/hardware") >= 0) {
        link = `No hardware with this id. Did you mean to update this hardware: <a href='/update/hardware/${id}' title='Update hardware ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/org") >= 0) {
        link = `No org with this id. Did you mean to update this org: <a href='/update/org/${id}' title='Update org ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/os") >= 0) {
        link = `No os with this id. Did you mean to update this os: <a href='/update/os/${id}' title='Update os ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/role") >= 0) {
        link = `No role with this id. Did you mean to udpate this role: <a href='/update/role/${id}' title='Update role ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/room") > 0) {
        link = `No room with this id. Did you mean to update this room: <a href='/update/room/${id}' title='Update room ${device}'>${device}</a> ?`;
    } else if (url.indexOf("/update/service") >= 0) {
        link = `No service level with this id. Did you mean to update this service: <a href='/update/service/${id}' title='Update service level ${device}'>${device}</a> ?`;
    }
    msg.innerHTML = link;
});
