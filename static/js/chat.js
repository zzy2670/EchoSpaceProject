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
    var div = document.createElement('div');
    div.className = 'message-item';
    div.setAttribute('data-msg-id', msg.id);
    div.innerHTML = '<strong>' + escapeHtml(msg.sender_name) + '</strong>: ' +
      escapeHtml(msg.content) + ' <span class="text-muted small">' + formatTime(msg.created_at) + '</span>';
    list.appendChild(div);
    scrollToBottom();
    lastMessageId = msg.id;
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
            if (input) input.value = '';
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
