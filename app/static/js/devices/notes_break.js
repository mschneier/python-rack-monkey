window.addEventListener("load", () => {
    const notesEL = document.getElementById("notes");
    let notesText = notesEL.innerText;
    //Insert <br> tags.
    notesText = notesText.replace(/<brk>/g, "<br>");
    //Insert <b> tags.
    let bth = 1;
    notesText = notesText.replace(/\*\*\*/g, () => { //Replace *** w/ <b></b> tags.
        bth++;
        return (bth % 2 === 0) ? "<b>" : "</b>";
    });
    //Insert <em> tags.
    let eth = 1;
    notesText = notesText.replace(/\*\*/g, () => { //Replace ** w/ <em></em> tags.
        eth++;
        return (eth % 2 === 0) ? "<em>" : "</em>";
    });
    notesEL.innerHTML = notesText;
});
