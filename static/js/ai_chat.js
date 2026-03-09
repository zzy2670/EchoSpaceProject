(function () {
  'use strict';
  var csrfToken = window.csrfToken || '';
  var conversationId = window.conversationId || '';

  var form = document.getElementById('ai-send-form');
  var input = document.getElementById('ai-prompt-input');
  var messagesEl = document.getElementById('ai-messages');
  var errorEl = document.getElementById('ai-error');
  var loadingEl = document.getElementById('ai-loading');
  var sendBtn = document.getElementById('ai-send-btn');
  var convIdInput = document.getElementById('conversation-id');

  function showError(msg) {
    if (errorEl) {
      errorEl.textContent = msg;
      errorEl.classList.remove('d-none');
    }
  }

  function hideError() {
    if (errorEl) errorEl.classList.add('d-none');
  }

  function setLoading(on) {
    if (loadingEl) loadingEl.classList.toggle('d-none', !on);
    if (sendBtn) sendBtn.disabled = on;
  }

  function escapeHtml(s) {
    var div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function appendMessage(role, content) {
    if (!messagesEl) return;
    var div = document.createElement('div');
    div.className = 'ai-msg ai-msg-' + role + ' mb-2';
    var label = role === 'user' ? 'You' : 'AI';
    div.innerHTML = '<strong>' + label + ':</strong> ' + escapeHtml(content);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var prompt = (input && input.value) ? input.value.trim() : '';
      if (!prompt) return;
      hideError();
      setLoading(true);
      var body = JSON.stringify({
        prompt: prompt,
        conversation_id: conversationId ? parseInt(conversationId, 10) : null
      });
      fetch('/ai/api/send/', {
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
          setLoading(false);
          if (data.ok) {
            appendMessage('user', data.user_message);
            appendMessage('assistant', data.assistant_message);
            if (data.conversation_id) {
              conversationId = String(data.conversation_id);
              if (convIdInput) convIdInput.value = conversationId;
            }
            if (input) input.value = '';
          } else {
            showError(data.error || 'Something went wrong');
          }
        })
        .catch(function () {
          setLoading(false);
          showError('Request failed. Please try again.');
        });
    });
  }
})();
