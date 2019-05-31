document.getElementById("domain_button").addEventListener("click", () => {
    const domains = [...document.getElementsByClassName("domain")];
    domains.forEach(domain => {
        const visible = domain.style.display;
        if (visible == "none") {
            domain.style.display = "";
        } else {
            domain.style.display = "none";
        }
    });
});
