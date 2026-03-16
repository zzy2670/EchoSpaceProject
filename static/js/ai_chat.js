const config = window.AI_CHAT_CONFIG;

const msgList = document.getElementById('ai-message-list');
const form = document.getElementById('ai-form');
const input = document.getElementById('ai-input');
const btn = document.getElementById('ai-btn');

function scrollToBottom() { 
    if (msgList) msgList.scrollTop = msgList.scrollHeight; 
}
scrollToBottom();

function getSafeTime() {
    const now = new Date();
    let hh = now.getHours().toString().padStart(2, '0');
    let mm = now.getMinutes().toString().padStart(2, '0');
    return hh + ':' + mm;
}


async function deleteChat(convId, event) {
    event.preventDefault();
    event.stopPropagation();
    
    if (!confirm("Are you sure you want to delete this conversation?")) return;
    
    const targetDeleteUrl = config.deleteUrlTemplate.replace('999999999', convId);
    
    try {
        const response = await fetch(targetDeleteUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': config.csrfToken }
        });
        
        if (response.ok) {
            if (config.currentConvId == convId) {

                window.location.href = config.chatHomeUrl;
            } else {
                window.location.reload();
            }
        } else {
            alert("Failed to delete conversation.");
        }
    } catch (err) {
        console.error("Delete Error:", err);
        alert("Network error.");
    }
}

window.deleteChat = deleteChat;


if(form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        
        const timeNow = getSafeTime();
        msgList.innerHTML += `
            <div class="align-self-end mb-3 msg-wrapper d-flex flex-column align-items-end" style="max-width: 85%;">
                <div class="d-flex align-items-baseline mb-1 px-1">
                    <span class="text-muted me-2" style="font-size: 0.65rem;">${timeNow}</span>
                    <strong class="text-primary" style="font-size: 0.75rem;">Me</strong>
                </div>
                <div class="d-flex align-items-start justify-content-end w-100">
                    <div class="bubble-self">${text.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
                </div>
            </div>`;
        scrollToBottom();
        
        const typingId = 'typing-' + Date.now();
        msgList.innerHTML += `<div id="${typingId}" class="align-self-start mb-3 msg-wrapper"><div class="bubble-other typing-indicator"><span></span><span></span><span></span></div></div>`;
        scrollToBottom();
        btn.disabled = true;

        try {
            const response = await fetch(config.apiUrl, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': config.csrfToken 
                },
                body: JSON.stringify({ message: text, conversation_id: config.currentConvId || null })
            });
            
            if (!response.ok) throw new Error("Server error");
            const data = await response.json();
            
            if(data.conversation_id && !config.currentConvId) { 
                const targetUrl = config.conversationUrlTemplate.replace('999999999', data.conversation_id);
                window.location.href = targetUrl;
                return;
            }

            document.getElementById(typingId).remove();
            msgList.innerHTML += `
                <div class="align-self-start mb-3 msg-wrapper d-flex flex-column align-items-start" style="max-width: 85%;">
                    <div class="d-flex align-items-baseline mb-1 px-1">
                        <strong class="text-dark me-2" style="font-size: 0.75rem;">EchoBot</strong>
                        <span class="text-muted" style="font-size: 0.65rem;">${getSafeTime()}</span>
                    </div>
                    <div class="bubble-other">${data.reply}</div>
                </div>`;
            scrollToBottom();
        } catch (err) {
            if(document.getElementById(typingId)){
                document.getElementById(typingId).remove();
            }
            msgList.innerHTML += `<div class="align-self-center text-danger small mt-2">Error connecting to EchoBot.</div>`;
        } finally { 
            btn.disabled = false; 
            input.focus(); 
        }
    });
}