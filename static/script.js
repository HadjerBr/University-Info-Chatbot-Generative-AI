// ---------- DOM ELEMENTS ----------

const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Our Flask endpoint that returns the chatbot answer
const API_URL = "/get";


// ---------- CALL FLASK BACKEND ----------

async function generateResponse(prompt) {
    // Sends the user's message to your Flask /get route
    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ msg: prompt }),
        // This matches: request.form.get("msg") in your Flask route
    });

    if (!response.ok) {
        throw new Error("Failed to get response from server");
    }

    // Your Flask route currently returns a plain string
    const text = await response.text();
    return text;
}


// ---------- UTILITIES ----------

function cleanMarkdown(text) {
    return text
        .replace(/#{1,6}\s?/g, "")   // remove markdown headers
        .replace(/\*\*/g, "")        // remove bold
        .replace(/\n{3,}/g, "\n\n")  // reduce excessive newlines
        .trim();
}

function addMessage(message, isUser) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message");
    messageElement.classList.add(isUser ? "user-message" : "bot-message");

    const profileImage = document.createElement("img");
    profileImage.classList.add("profile-image");
    profileImage.src = isUser ? "/static/user.jpeg" : "/static/bot.jpeg";
    profileImage.alt = isUser ? "User" : "Bot";

    const messageContent = document.createElement("div");
    messageContent.classList.add("message-content");
    messageContent.textContent = message;

    messageElement.appendChild(profileImage);
    messageElement.appendChild(messageContent);

    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


// ---------- MAIN HANDLER ----------

async function handleUserInput() {
    const userMessage = userInput.value.trim();

    if (userMessage) {
        addMessage(userMessage, true);
        userInput.value = "";

        sendButton.disabled = true;
        userInput.disabled = true;

        try {
            const botMessage = await generateResponse(userMessage);
            addMessage(cleanMarkdown(botMessage), false);
        } catch (error) {
            console.error("Error:", error);
            addMessage("Sorry, I encountered an error. Please try again.", false);
        } finally {
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    }
}


// ---------- EVENT LISTENERS ----------

sendButton.addEventListener("click", handleUserInput);

userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleUserInput();
    }
});
