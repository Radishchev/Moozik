function enterRoom(code){
    window.location = `/room/${code}`
}

async function loadRooms(){

    const res = await fetch("/api/rooms/public",{
        credentials: "include"
    })

    const rooms = await res.json()

    const list = document.getElementById("roomsList")

    if(!list) return

    list.innerHTML = ""

    rooms.forEach(r => {

        const div = document.createElement("div")

        div.className = "room"

        const name = document.createElement("span")
        name.textContent = r.name

        const btn = document.createElement("button")
        btn.textContent = "Join"
        btn.onclick = () => enterRoom(r.code)

        div.appendChild(name)
        div.appendChild(btn)

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
        credentials:"include",
        headers:{
            "Content-Type":"application/json"
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
        alert(data.error || "Error creating room")
    }

}


async function joinPrivate(){

    const code = document.getElementById("inviteCode").value.trim()

    if(!code){
        alert("Enter invite code")
        return
    }

    const res = await fetch(`/api/rooms/join/${code}`,{
        credentials:"include"
    })

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