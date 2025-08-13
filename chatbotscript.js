document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.querySelector(".chatbot-message");
    if (!textarea) return;

    // Create hidden span for width measurement
    const mirror = document.createElement("span");
    mirror.style.position = "absolute";
    mirror.style.top = "-9999px";
    mirror.style.left = "-9999px";
    mirror.style.whiteSpace = "pre";
    mirror.style.visibility = "hidden";

    const cs = getComputedStyle(textarea);
    mirror.style.fontSize = cs.fontSize;
    mirror.style.fontFamily = cs.fontFamily;
    mirror.style.fontWeight = cs.fontWeight;
    mirror.style.letterSpacing = cs.letterSpacing;

    document.body.appendChild(mirror);

    const minWidth = 500; // px
    const maxWidth = 1000; // px
    const maxHeight = 200; // px (change as needed)

    function resize() {
        // Adjust width
        mirror.textContent = textarea.value || textarea.placeholder || "";
        const newWidth = Math.min(Math.max(mirror.offsetWidth + 20, minWidth), maxWidth);
        textarea.style.width = newWidth + "px";

        // Adjust height
        textarea.style.height = "auto"; // reset
        const scrollH = textarea.scrollHeight;
        if (scrollH > maxHeight) {
            textarea.style.height = maxHeight + "px";
            textarea.style.overflowY = "auto"; // enable scroll
        } else {
            textarea.style.height = scrollH + "px";
            textarea.style.overflowY = "hidden"; // no scroll
        }
    }

    textarea.addEventListener("input", resize);
    resize();
});
