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

    // Send message on button click or Enter key
    const botName = window.location.pathname.split("/").pop();
    const sendButton = document.getElementById("send-button");
    sendButton.addEventListener("click", sendMessage);
    textarea.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = textarea.value.trim();
        if (!message) return;
        const chatCell = document.querySelector(".chatbot-chat-table td");
        // append user message bubble
        const userMsg = document.createElement("p");
        userMsg.className = "bubble-user";
        userMsg.textContent = message;
        chatCell.appendChild(userMsg);

        textarea.value = "";
        resize();

        // fetch bot response
        try {
            const response = await fetch(`/api/chat/${botName}`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });
            const data = await response.json();
            const answer = data.answer || data.error;
            const botMsg = document.createElement("p");
            botMsg.className = "bubble-bot";
            botMsg.textContent = answer;
            chatCell.appendChild(botMsg);
        } catch (error) {
            console.error("Error sending message:", error);
        }

        // scroll to bottom of chat
        chatCell.parentElement.scrollTop = chatCell.parentElement.scrollHeight;
    }
});
