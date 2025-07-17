function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text/plain", ev.target.dataset.img);
}

function drop(ev, toTier) {
    ev.preventDefault();
    const imgName = ev.dataTransfer.getData("text/plain");
    const imgEl = document.querySelector(`img[data-img='${imgName}']`);
    const targetContainer = document.getElementById(toTier);
    
    if (imgEl && targetContainer) {
        targetContainer.appendChild(imgEl);

        fetch("/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imgName, to: toTier })
        });
    }
}
