// ---------------- LOGIN ----------------

async function handleLogin(e){

    e.preventDefault()

    const username = document.getElementById("loginUsername").value
    const password = document.getElementById("loginPassword").value

    const res = await fetch("/api/login",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        credentials:"include",
        body:JSON.stringify({username,password})
    })

    const data = await res.json()

    if(!res.ok){
        document.getElementById("loginError").innerText = data.error
        return
    }

    window.location = "/rooms"

}


// ---------------- REGISTER ----------------

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
        credentials:"include",
        body:JSON.stringify({username,email,password})
    })

    const data = await res.json()

    if(!res.ok){
        document.getElementById("registerError").innerText = data.error
        return
    }

    window.location = "/rooms"

}



async function handleGoogleResponse(response){

    try{

        const res = await fetch("/api/google-login",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            credentials:"include",
            body:JSON.stringify({
                credential: response.credential
            })
        });

        if(res.ok){
            window.location = "/rooms";
        }else{
            alert("Google login failed");
        }

    }catch(err){
        console.error(err);
    }

}


// ---------------- GOOGLE BUTTON ----------------

function googleLogin(){

    if(!window.google){
        console.error("Google script not loaded")
        return
    }

    google.accounts.id.initialize({
        client_id: "154714697233-tbadlqhrv6je2hma95u6i8ndsjqjk7pe.apps.googleusercontent.com",
        callback: handleGoogleResponse
    });

    google.accounts.id.prompt();

}


// ---------------- TAB SWITCHING ----------------

function setupTabs(){

    document.querySelectorAll('.auth-tab').forEach(tab => {

        tab.addEventListener('click', function(){

            const tabName = this.getAttribute('data-tab')

            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'))
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'))

            this.classList.add('active')
            document.getElementById(tabName + 'Form').classList.add('active')

        })

    })


    document.querySelectorAll('.switch-tab').forEach(link => {

        link.addEventListener('click', function(e){

            e.preventDefault()

            const tabName = this.getAttribute('data-tab')

            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'))
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'))

            document.querySelector('[data-tab="' + tabName + '"]').classList.add('active')
            document.getElementById(tabName + 'Form').classList.add('active')

        })

    })

}


// ---------------- INIT ----------------

document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm")
    const registerForm = document.getElementById("registerForm")

    if(loginForm){
        loginForm.addEventListener("submit",handleLogin)
    }

    if(registerForm){
        registerForm.addEventListener("submit",handleRegister)
    }

    setupTabs()

})