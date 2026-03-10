let audio = new Audio();
let hls;

audio.controls = false;
audio.autoplay = true;

document.body.appendChild(audio);

let seekBar = document.getElementById('seek');
let curTime = document.getElementById('curTime');
let durTime = document.getElementById('durTime');

function handleStop() {

  destroyHls();

  const cover = document.getElementById('cover')
  const title = document.getElementById('title')

  if(cover) cover.src = ''
  if(title) title.textContent = 'No song playing'

  updateStatus('');

  if(seekBar) seekBar.value = 0
  if(curTime) curTime.textContent = '0:00'
  if(durTime) durTime.textContent = '0:00'
}

function handleSongChange(data) {

  const cover = document.getElementById('cover')
  const title = document.getElementById('title')

  if(cover) cover.src = data.thumbnail || ''
  if(title) title.textContent = data.title || 'Unknown'

  if(durTime) durTime.textContent = formatTime(data.duration || 0)

  if(seekBar){
    seekBar.max = data.duration || 0
    seekBar.value = 0
  }

  updateStatus("Loading stream...");
}

function loadStream() {

  const url = `/hls/${room}/stream.m3u8?_=${Date.now()}`

  destroyHls()

  if (Hls.isSupported()) {

    hls = new Hls({ liveSyncDurationCount: 1 })

    hls.loadSource(url)

    hls.attachMedia(audio)

    hls.on(Hls.Events.MANIFEST_PARSED, () => {

      updateStatus("Stream ready")

      audio.play().catch(() => updateStatus("Click to play"))

    })

    hls.on(Hls.Events.ERROR, (event, data) => {

      if (data.fatal) {
        updateStatus("Stream error. Try refreshing.")
      }

    })

  } else {

    audio.src = url

    audio.load()

    audio.play().catch(() => updateStatus("Click to play"))

  }
}

function destroyHls() {

  if (hls) {

    try { hls.destroy() } catch {}

    hls = null
  }

  audio.pause()

  audio.src = ''

  audio.load()
}

function formatTime(sec) {

  const m = Math.floor(sec / 60)

  const s = sec % 60

  return m + ':' + String(s).padStart(2, '0')
}

if(seekBar){
  seekBar.addEventListener('input', () => {
    audio.currentTime = seekBar.value
  })
}

setInterval(() => {

  if (!isNaN(audio.currentTime) && seekBar) {

    seekBar.value = Math.floor(audio.currentTime)

    if(curTime){
      curTime.textContent = formatTime(Math.floor(audio.currentTime))
    }

  }

}, 250)
