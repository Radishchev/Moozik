async function handleLogin(e){

    e.preventDefault()

    const username = document.getElementById("loginUsername").value
    const password = document.getElementById("loginPassword").value

    const res = await fetch("/api/login",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({username,password})
    })

    const data = await res.json()

    if(!res.ok){
        document.getElementById("loginError").innerText = data.error
        return
    }

    localStorage.setItem("token",data.token)

    window.location = "/rooms"

}


async function handleRegister(e){

    e.preventDefault()

    const username = document.getElementById("regUsername").value
    const email = document.getElementById("regEmail").value
    const password = document.getElementById("regPassword").value

    const res = await fetch("/api/register",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({username,email,password})
    })

    const data = await res.json()

    if(!res.ok){
        document.getElementById("registerError").innerText = data.error
        return
    }

    localStorage.setItem("token",data.token)

    window.location = "/rooms"

}


document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm")
    const registerForm = document.getElementById("registerForm")

    if(loginForm){
        loginForm.addEventListener("submit",handleLogin)
    }

    if(registerForm){
        registerForm.addEventListener("submit",handleRegister)
    }

})