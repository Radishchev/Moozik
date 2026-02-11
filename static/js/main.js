function updateStatus(msg) {
  document.getElementById('status').textContent = msg;
}

function appendMessage(user, msg) {
  const m = document.createElement('div');
  m.classList.add('message', user === username ? 'self' : 'other');
  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = user;
  m.appendChild(meta);
  const txt = document.createElement('div');
  txt.textContent = msg;
  m.appendChild(txt);
  document.getElementById('chat').appendChild(m);
  document.getElementById('chat').scrollTop = 1e9;
}

document.getElementById('sendBtn').onclick = () => {
  const msg = document.getElementById('msgInput').value.trim();
  if (!msg) return;
  if (!socket.connected) {
    appendMessage('System', 'Not connected. Reconnecting...');
    initSocket();
    return;
  }
  socket.emit('chat', { room, username, msg });
  document.getElementById('msgInput').value = '';
};

document.getElementById('msgInput').addEventListener('keypress', e => {
  if (e.key === 'Enter') {
    e.preventDefault();
    document.getElementById('sendBtn').click();
  }
});

document.addEventListener('visibilitychange', function () {
  if (document.visibilityState === 'visible') {
    if (socket && !socket.connected) initSocket();
    socket.emit('check_stream', { room });
  }
});

// Mobile Hamburger Toggle
const hamburger = document.getElementById('hamburger');
const leftPanel = document.getElementById('left');

hamburger.addEventListener('click', () => {
  leftPanel.classList.toggle('open');
});

initSocket();

