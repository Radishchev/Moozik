const token = localStorage.getItem("token")

if(!token){
    window.location="/login"
}

function enterRoom(code){
    window.location = `/room/${code}`
}

async function loadRooms(){

    const res = await fetch("/api/rooms/public")

    const rooms = await res.json()

    const list = document.getElementById("roomsList")

    if(!list) return

    list.innerHTML = ""

    rooms.forEach(r => {

        const div = document.createElement("div")

        div.className = "room"

        div.innerHTML = `
            <span>${r.name}</span>
            <button onclick="enterRoom('${r.code}')">Join</button>
        `

        list.appendChild(div)

    })

}


async function createRoom(){

    const name = document.getElementById("roomName").value.trim()

    if(!name){
        alert("Room name required")
        return
    }

    const isPrivate = document.getElementById("privateRoom").checked

    const res = await fetch("/api/rooms/create",{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "Authorization":"Bearer "+token
        },
        body:JSON.stringify({
            name:name,
            private:isPrivate
        })
    })

    const data = await res.json()

    if(data.room_code){

        if(data.invite_code){
            alert("Invite link:\n" + window.location.origin + "/room/" + data.room_code)
        }

        enterRoom(data.room_code)

    }else{
        alert("Error creating room")
    }

}


async function joinPrivate(){

    const code = document.getElementById("inviteCode").value.trim()

    if(!code){
        alert("Enter invite code")
        return
    }

    const res = await fetch(`/api/rooms/join/${code}`)

    const data = await res.json()

    if(data.room_code){

        enterRoom(data.room_code)

    }else{

        alert("Invalid invite")

    }

}


document.addEventListener("DOMContentLoaded", () => {
    loadRooms()
})