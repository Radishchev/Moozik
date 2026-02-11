const room = 'default';
const username = prompt("Nickname:") || 'Anon';
let socket;

function initSocket() {
  if (socket) {
    try {
      socket.disconnect();
    } catch (e) {
      console.warn('Error disconnecting socket:', e);
    }
  }

  socket = io({
    transports: ['websocket'],
    upgrade: false,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 10000
  });

  socket.on('connect', () => {
    updateStatus("Connected");
    socket.emit('join', { room, username });
  });

  socket.on('connect_error', err => updateStatus("Connection error"));
  socket.on('disconnect', () => updateStatus("Disconnected"));
  socket.on('reconnect_attempt', () => updateStatus("Reconnecting..."));

  socket.on('chat', data => appendMessage(data.username, data.msg));
  socket.on('queue_updated', data => console.log('Queue:', data.queue));
  socket.on('song_stopped', handleStop);
  socket.on('song_changed', handleSongChange);
  socket.on('stream_ready', () => setTimeout(loadStream, 500));
}
