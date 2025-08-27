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

        // fetch bot response as stream
        // create bot message bubble
        const botMsg = document.createElement("p");
        botMsg.className = "bubble-bot";
        chatCell.appendChild(botMsg);

        try {
            const response = await fetch(`/api/chat/${botName}`, {
                method: "POST",
                credentials: "same-origin",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message})
            });
            if (!response.ok) {
                const errorData = await response.json();
                botMsg.textContent = `Error: ${errorData.error || response.statusText}`;
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            let doneRead = false;
            while (!doneRead) {
                const {done, value} = await reader.read();
                doneRead = done;
                buffer += decoder.decode(value || new Uint8Array(), {stream: true});
                let newlineIndex;
                while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
                    const chunk = buffer.slice(0, newlineIndex).trim();
                    buffer = buffer.slice(newlineIndex + 1);
                    if (!chunk) continue;
                    try {
                        const {content} = JSON.parse(chunk);
                        botMsg.textContent += content;
                        // scroll as new content arrives
                        chatCell.parentElement.scrollTop = chatCell.parentElement.scrollHeight;
                    } catch (e) {
                        console.error("Stream parse error:", e, chunk);
                    }
                }
            }
            if (buffer.trim()) {
                try {
                    const {content} = JSON.parse(buffer.trim());
                    botMsg.textContent += content;
                } catch (e) {
                    console.error("Final parse error:", e, buffer);
                }
            }
        } catch (error) {
            console.error("Error sending message:", error);
        }
        // final scroll to bottom
        chatCell.parentElement.scrollTop = chatCell.parentElement.scrollHeight;
    }
});
