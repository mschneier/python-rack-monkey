document.getElementById("show_style_syntax").addEventListener("click", () => {
    const syntax = document.getElementById("style_syntax");
    const button = document.getElementById("show_style_syntax");
    if (syntax.style.display == "none") {
        syntax.style.display = "";
        button.value = "Hide Style Syntax";
    } else {
        syntax.style.display = "none";
        button.value = "Show Style Syntax";
    }
});

