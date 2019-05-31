document.getElementById("search_form").addEventListener("submit", (e) => {
    e.preventDefault();
    const search = document.getElementById("search_text").value;
    window.location.href = `/view/devices/search/?search=${search}`;
});
