// room is provided by chat.html
// <script>const room = "{{ room_code }}"</script>

let socket
let username = null

if(!room){
  window.location = "/rooms"
}


async function fetchCurrentUser(){

  try{

    const res = await fetch("/api/me",{
      credentials: "include"
    })

    if(!res.ok){
      window.location = "/login"
      return
    }

    const data = await res.json()

    username = data.username

  }catch(err){

    console.error("Failed to fetch user:", err)
    window.location = "/login"

  }

}


function initSocket(){

  if(socket){
    try{
      socket.disconnect()
    }catch(e){}
  }

  socket = io({
    withCredentials: true,
    transports: ["websocket"]
  })


  socket.on("connect", () => {

    console.log("Socket connected")

    updateStatus("Connected")

    socket.emit("join", {
      room: room
    })

  })


  socket.on("connect_error", (err) => {

    console.error("Socket error:", err)

    updateStatus("Connection error")

  })


  socket.on("disconnect", () => {

    console.log("Socket disconnected")

    updateStatus("Disconnected")

  })


  socket.on("chat", data => {

    appendMessage(data.username, data.msg)

  })


  socket.on("queue_updated", data => {

    console.log("Queue:", data.queue)

  })


  socket.on("song_stopped", handleStop)

  socket.on("song_changed", handleSongChange)

  socket.on("stream_ready", () => {

    setTimeout(loadStream, 500)

  })

}


document.addEventListener("DOMContentLoaded", async () => {

  await fetchCurrentUser()

  initSocket()

})