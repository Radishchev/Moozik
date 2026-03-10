const room = 'default'

let socket
let username = null


function parseJwt(token){
  try{
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g,'+').replace(/_/g,'/')
    return JSON.parse(atob(base64))
  }catch(e){
    return null
  }
}


const token = localStorage.getItem("token")

if(token){

  const payload = parseJwt(token)

  if(payload){

    username = payload.username

    document.addEventListener("DOMContentLoaded", () => {

      const el = document.getElementById("sidebarUsername")

      if(el){
        el.textContent = username
      }

    })

  }

}


function initSocket(){

  if(!token){
    window.location="/login"
    return
  }

  if(socket){
    try{
      socket.disconnect()
    }catch(e){}
  }

  socket = io({
    auth: {
      token: token
    },
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

  socket.on("stream_ready", () => setTimeout(loadStream, 500))

}
