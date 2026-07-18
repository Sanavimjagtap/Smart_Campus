const input = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("messages");

// Suggestion chips
document.querySelectorAll(".suggestions button").forEach(button => {

    button.addEventListener("click", function(){

        input.value = this.dataset.question;
        sendMessage();

    });

});

// Send button
sendBtn.addEventListener("click", sendMessage);

// Press Enter
input.addEventListener("keypress", function(e){

    if(e.key === "Enter"){

        e.preventDefault();
        sendMessage();

    }

});

function sendMessage(){

    let question = input.value.trim();

    if(question === "")
        return;

    // User Bubble
    messages.innerHTML += `
        <div class="user-message">
            ${question}
        </div>
    `;

    input.value = "";

    // Scroll
    messages.scrollTop = messages.scrollHeight;

    // Loading bubble
    let loading = document.createElement("div");

    loading.className = "bot-message";

    loading.innerHTML = `
        <strong>Campus AI</strong><br><br>
        Thinking...
    `;

    messages.appendChild(loading);

    fetch("/ask_chatbot",{

        method:"POST",

        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },

        body:"question="+encodeURIComponent(question)

    })

    .then(response=>response.json())

    .then(data=>{

        loading.innerHTML=`
            <strong>Campus AI</strong><br><br>
            ${data.answer.replace(/\n/g,"<br>")}
        `;

        messages.scrollTop=messages.scrollHeight;

    });

}