// Access camera, draw framing overlay, capture and send to backend
const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const captureBtn = document.getElementById('captureBtn');

async function initCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
    video.srcObject = stream;
    drawOverlay();
  } catch (err) {
    statusEl.textContent = 'No se pudo acceder a la cámara: ' + err.message;
  }
}

function drawOverlay() {
  const ctx = overlay.getContext('2d');
  function paint() {
    const w = overlay.width = overlay.clientWidth;
    const h = overlay.height = overlay.clientHeight;
    ctx.clearRect(0,0,w,h);
    const boxW = Math.min(w * 0.75, h * 0.75);
    const boxH = boxW;
    const x = (w - boxW) / 2;
    const y = (h - boxH) / 2;
    // darken around
    ctx.fillStyle = 'rgba(0,0,0,.35)';
    ctx.fillRect(0,0,w,y);
    ctx.fillRect(0,y,x,boxH);
    ctx.fillRect(x+boxW,y,w-(x+boxW),boxH);
    ctx.fillRect(0,y+boxH,w,h-(y+boxH));
    // corner marks
    const r = 16;
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#7c4dff';
    const l = 28;
    // corners
    ctx.beginPath();
    // TL
    ctx.moveTo(x, y+l); ctx.lineTo(x, y); ctx.lineTo(x+l, y);
    // TR
    ctx.moveTo(x+boxW-l, y); ctx.lineTo(x+boxW, y); ctx.lineTo(x+boxW, y+l);
    // BR
    ctx.moveTo(x+boxW, y+boxH-l); ctx.lineTo(x+boxW, y+boxH); ctx.lineTo(x+boxW-l, y+boxH);
    // BL
    ctx.moveTo(x+l, y+boxH); ctx.lineTo(x, y+boxH); ctx.lineTo(x, y+boxH-l);
    ctx.stroke();
    requestAnimationFrame(paint);
  }
  paint();
}

async function capture() {
  statusEl.textContent = 'Procesando...';
  // draw current frame into an offscreen canvas at 480x640 (portrait-ish)
  const off = document.createElement('canvas');
  const w = 480, h = 640;
  off.width = w; off.height = h;
  const ctx = off.getContext('2d');
  // Draw video to canvas preserving aspect
  const vw = video.videoWidth, vh = video.videoHeight;
  const scale = Math.max(w/vw, h/vh);
  const dw = vw*scale, dh = vh*scale;
  const dx = (w - dw)/2, dy = (h - dh)/2;
  ctx.drawImage(video, dx, dy, dw, dh);
  const dataURL = off.toDataURL('image/jpeg', 0.9);

  try {
    const res = await fetch('/api/verify', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ image: dataURL })
    });
    const json = await res.json();
    if (json.ok) {
      window.location.href = json.redirect;
    } else {
      statusEl.textContent = 'Error: ' + (json.error || 'No verificado');
    }
  } catch (e) {
    statusEl.textContent = 'Error de red: ' + e.message;
  }
}

captureBtn?.addEventListener('click', capture);
initCamera();
