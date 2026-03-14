(function () {
  'use strict';
  var roomId = window.roomId;
  var csrfToken = window.csrfToken;
  var lastMessageId = window.lastMessageId || 0;
  var POLL_INTERVAL_MS = 3000;

  var form = document.getElementById('send-message-form');
  var input = document.getElementById('message-input');
  var list = document.getElementById('message-list');
  var countEl = document.getElementById('room-member-count');

  function scrollToBottom() {
    if (list) list.scrollTop = list.scrollHeight;
  }

  function addMessage(msg) {
    if (!list) return;
    
    var isMe = (msg.sender_name === window.currentUsername);
    
    var timeStr = formatTime(msg.created_at);
    var safeContent = escapeHtml(msg.content);
    var safeSender = escapeHtml(msg.sender_name || 'Unknown');
    var msgId = msg.id;

    var div = document.createElement('div');
    div.setAttribute('data-msg-id', msgId);

    if (isMe) {
      div.className = "align-self-end mb-3 msg-wrapper d-flex flex-column align-items-end";
      div.style.maxWidth = "85%";
      div.innerHTML = `
          <div class="d-flex align-items-baseline mb-1 px-1">
              <span class="text-muted me-2" style="font-size: 0.65rem;">${timeStr}</span>
              <strong class="text-primary" style="font-size: 0.75rem;">Me</strong>
          </div>
          <div class="d-flex align-items-start justify-content-end w-100">
              <button class="btn btn-sm btn-light text-danger rounded-circle shadow-sm withdraw-btn me-2 mt-1 d-flex align-items-center justify-content-center" title="Withdraw message" onclick="withdrawMessage(${msgId})">×</button>
              <div class="bubble-self">${safeContent}</div>
          </div>
      `;
    } else {
      div.className = "align-self-start mb-3 msg-wrapper d-flex flex-column align-items-start";
      div.style.maxWidth = "85%";
      div.innerHTML = `
          <div class="d-flex align-items-baseline mb-1 px-1">
              <strong class="text-dark me-2" style="font-size: 0.75rem;">${safeSender}</strong>
              <span class="text-muted" style="font-size: 0.65rem;">${timeStr}</span>
          </div>
          <div class="bubble-other">${safeContent}</div>
      `;
    }

    list.appendChild(div);
    scrollToBottom();
    lastMessageId = msgId;
  }

  function escapeHtml(s) {
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function formatTime(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    return d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0');
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var content = (input && input.value) ? input.value.trim() : '';
      if (!content) return;
      
      input.value = '';
      
      var body = JSON.stringify({ content: content });
      fetch('/chat/api/rooms/' + roomId + '/messages/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: body,
        credentials: 'same-origin'
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (data.ok && data.data) {
            addMessage(data.data);
          } else {
            alert(data.error || 'Failed to send');
          }
        })
        .catch(function () { alert('Failed to send message'); });
    });
  }

  function pollMessages() {
    fetch('/chat/api/rooms/' + roomId + '/messages/?after_id=' + lastMessageId, {
      method: 'GET',
      credentials: 'same-origin'
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.ok && data.data && data.data.length) {
          data.data.forEach(addMessage);
        }
      })
      .catch(function () {});
  }

  function pollStats() {
    fetch('/chat/api/rooms/' + roomId + '/stats/', { credentials: 'same-origin' })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.ok && data.data && countEl) {
          countEl.textContent = data.data.current_count;
        }
      })
      .catch(function () {});
  }

  scrollToBottom();
  setInterval(pollMessages, POLL_INTERVAL_MS);
  setInterval(pollStats, POLL_INTERVAL_MS);
})();