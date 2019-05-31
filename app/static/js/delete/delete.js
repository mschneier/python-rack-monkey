document.getElementById("submitButton").addEventListener("click", (e) => {
    e.preventDefault();
    const cat = document.getElementById("category").innerText;
    const msg = confirm(`Are you sure you want to delete this ${cat}? This cannot be undone!`);
    if (msg) {
        document.getElementById("delete_form").submit();
    }
});
