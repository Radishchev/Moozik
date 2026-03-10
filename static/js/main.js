function updateStatus(msg) {
  const el = document.getElementById('status');
  if (el) el.textContent = msg;
}

function appendMessage(user, msg) {

  const chat = document.getElementById('chat');
  if (!chat) return;

  const m = document.createElement('div');

  m.classList.add(
    'message',
    user === username ? 'self' : 'other'
  );

  const meta = document.createElement('div');
  meta.className = 'meta';
  meta.textContent = user;

  const txt = document.createElement('div');
  txt.textContent = msg;

  m.appendChild(meta);
  m.appendChild(txt);

  chat.appendChild(m);

  chat.scrollTop = chat.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {

  const sendBtn = document.getElementById('sendBtn');
  const msgInput = document.getElementById('msgInput');

  if (sendBtn && msgInput) {

    sendBtn.onclick = () => {

      const msg = msgInput.value.trim()

      if(!msg) return

      if(!socket || !socket.connected){

        appendMessage("System","Not connected. Reconnecting...")

        initSocket()

        return
      }

      socket.emit("chat",{
        room: room,
        msg: msg
      })

      msgInput.value = ""
    }

    msgInput.addEventListener("keypress", e => {
      if(e.key === "Enter"){
        e.preventDefault()
        sendBtn.click()
      }
    })

  }

  document.addEventListener('visibilitychange', function () {

    if (document.visibilityState === 'visible') {

      if (socket && !socket.connected) {
        initSocket();
      }

      if (socket) {
        socket.emit('check_stream', { room });
      }

    }

  });

  initSocket();

});
