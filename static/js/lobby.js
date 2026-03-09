(function () {
  'use strict';
  var POLL_INTERVAL_MS = 8000;

  function fetchRooms() {
    fetch('/chat/api/rooms/', {
      method: 'GET',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'same-origin'
    })
      .then(function (res) { return res.ok ? res.json() : null; })
      .then(function (data) {
        if (!data || !data.ok || !data.data) return;
        var rooms = data.data;
        rooms.forEach(function (room) {
          var el = document.querySelector('.room-current-count[data-room-id="' + room.id + '"]');
          if (el) el.textContent = room.current_count;
        });
      })
      .catch(function () {});
  }

  if (document.querySelector('.room-current-count')) {
    setInterval(fetchRooms, POLL_INTERVAL_MS);
  }
})();
