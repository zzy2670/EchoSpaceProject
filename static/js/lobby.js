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


window.filterRooms = function() {
    const query = document.getElementById('roomSearchInput').value.toLowerCase();
    const rooms = document.querySelectorAll('.room-item');
    
    rooms.forEach(room => {
        const name = room.querySelector('.room-name').textContent.toLowerCase();
        room.style.display = name.includes(query) ? 'block' : 'none';
    });
};