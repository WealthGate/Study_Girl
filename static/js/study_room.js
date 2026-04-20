const room = document.querySelector(".room");
const sessionId = room.dataset.sessionId;
const currentUser = room.dataset.currentUser;
const scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${scheme}://${window.location.host}/ws/study-room/${sessionId}/`);

const localVideo = document.getElementById("localVideo");
const remoteVideo = document.getElementById("remoteVideo");
const screenVideo = document.getElementById("screenVideo");
const screenTile = document.getElementById("screenTile");
const statusBanner = document.getElementById("statusBanner");
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const whiteboard = document.getElementById("whiteboard");
const boardContext = whiteboard.getContext("2d");
const focusWarning = document.getElementById("focusWarning");

let localStream;
let peer;
let isDrawing = false;
let tool = "pencil";
let tabWarnings = 0;
let audioContext;
let oscillator;

const peerConfig = { iceServers: [{ urls: "stun:stun.l.google.com:19302" }] };

function send(payload) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(payload));
  }
}

async function startMedia() {
  try {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;
    createPeer();
    statusBanner.textContent = "Room ready. Invite your study sister to join.";
  } catch (error) {
    statusBanner.textContent = "Camera or microphone permission was denied. Chat and whiteboard still work.";
  }
}

function createPeer() {
  peer = new RTCPeerConnection(peerConfig);
  localStream.getTracks().forEach(track => peer.addTrack(track, localStream));
  peer.ontrack = event => {
    remoteVideo.srcObject = event.streams[0];
  };
  peer.onicecandidate = event => {
    if (event.candidate) send({ type: "ice", candidate: event.candidate });
  };
}

socket.addEventListener("open", startMedia);
socket.addEventListener("message", async event => {
  const data = JSON.parse(event.data);
  if (data.type === "presence") {
    statusBanner.textContent = `${data.user} ${data.status} the room.`;
    if (data.status === "joined" && peer && localStream) {
      const offer = await peer.createOffer();
      await peer.setLocalDescription(offer);
      send({ type: "offer", offer });
    }
  }
  if (data.user === currentUser) return;
  if (data.type === "offer" && peer) {
    await peer.setRemoteDescription(new RTCSessionDescription(data.offer));
    const answer = await peer.createAnswer();
    await peer.setLocalDescription(answer);
    send({ type: "answer", answer });
  }
  if (data.type === "answer" && peer) {
    await peer.setRemoteDescription(new RTCSessionDescription(data.answer));
  }
  if (data.type === "ice" && peer && data.candidate) {
    try { await peer.addIceCandidate(new RTCIceCandidate(data.candidate)); } catch (error) {}
  }
  if (data.type === "chat") appendChat(data.user, data.message);
  if (data.type === "draw") drawLine(data.x1, data.y1, data.x2, data.y2, data.color, data.width, false);
  if (data.type === "clear_board") boardContext.clearRect(0, 0, whiteboard.width, whiteboard.height);
});

document.getElementById("toggleMic").addEventListener("click", () => {
  localStream?.getAudioTracks().forEach(track => track.enabled = !track.enabled);
});

document.getElementById("toggleCamera").addEventListener("click", () => {
  localStream?.getVideoTracks().forEach(track => track.enabled = !track.enabled);
});

document.getElementById("shareScreen").addEventListener("click", async () => {
  try {
    const screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
    screenVideo.srcObject = screenStream;
    screenTile.classList.remove("hidden");
    const screenTrack = screenStream.getVideoTracks()[0];
    const sender = peer?.getSenders().find(item => item.track && item.track.kind === "video");
    if (sender) sender.replaceTrack(screenTrack);
    screenTrack.onended = () => {
      screenTile.classList.add("hidden");
      const cameraTrack = localStream?.getVideoTracks()[0];
      if (sender && cameraTrack) sender.replaceTrack(cameraTrack);
    };
  } catch (error) {
    statusBanner.textContent = "Screen sharing was cancelled or denied by the browser.";
  }
});

chatForm.addEventListener("submit", event => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  send({ type: "chat", message });
  appendChat("You", message);
  chatInput.value = "";
});

function appendChat(user, message) {
  const line = document.createElement("p");
  line.innerHTML = `<strong>${user}:</strong> ${escapeHtml(message)}`;
  chatMessages.appendChild(line);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

document.querySelectorAll("[data-tab]").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-tab]").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelectorAll(".tool-panel").forEach(panel => panel.classList.add("hidden"));
    document.getElementById(`${button.dataset.tab}Panel`).classList.remove("hidden");
  });
});

document.getElementById("pencilTool").addEventListener("click", () => tool = "pencil");
document.getElementById("eraserTool").addEventListener("click", () => tool = "eraser");
document.getElementById("clearBoard").addEventListener("click", () => {
  boardContext.clearRect(0, 0, whiteboard.width, whiteboard.height);
  send({ type: "clear_board" });
});

function pointerPosition(event) {
  const rect = whiteboard.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left) * (whiteboard.width / rect.width),
    y: (event.clientY - rect.top) * (whiteboard.height / rect.height)
  };
}

let lastPoint = null;
whiteboard.addEventListener("pointerdown", event => {
  isDrawing = true;
  lastPoint = pointerPosition(event);
});
whiteboard.addEventListener("pointermove", event => {
  if (!isDrawing) return;
  const point = pointerPosition(event);
  const color = tool === "eraser" ? "#ffffff" : "#c43b6d";
  const width = tool === "eraser" ? 18 : 4;
  drawLine(lastPoint.x, lastPoint.y, point.x, point.y, color, width, true);
  lastPoint = point;
});
window.addEventListener("pointerup", () => isDrawing = false);

function drawLine(x1, y1, x2, y2, color, width, shouldSend) {
  boardContext.strokeStyle = color;
  boardContext.lineWidth = width;
  boardContext.lineCap = "round";
  boardContext.beginPath();
  boardContext.moveTo(x1, y1);
  boardContext.lineTo(x2, y2);
  boardContext.stroke();
  if (shouldSend) send({ type: "draw", x1, y1, x2, y2, color, width });
}

document.getElementById("focusMode").addEventListener("click", async () => {
  room.classList.toggle("focus-active");
  focusWarning.classList.remove("hidden");
  try { await document.documentElement.requestFullscreen(); } catch (error) {}
});

document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    tabWarnings += 1;
    focusWarning.textContent = `Focus reminder: you have switched tabs ${tabWarnings} time(s). Enable Do Not Disturb for phone notifications.`;
    focusWarning.classList.remove("hidden");
  }
});
document.addEventListener("fullscreenchange", () => {
  if (!document.fullscreenElement) {
    focusWarning.textContent = "Fullscreen ended. The app cannot block device notifications, but Focus Mode works best in fullscreen with Do Not Disturb enabled.";
    focusWarning.classList.remove("hidden");
  }
});

let seconds = 0;
setInterval(() => {
  seconds += 1;
  const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
  const secs = String(seconds % 60).padStart(2, "0");
  document.getElementById("sessionTimer").textContent = `${mins}:${secs}`;
}, 1000);

document.getElementById("noiseButton").addEventListener("click", () => {
  if (oscillator) {
    oscillator.stop();
    oscillator = null;
    return;
  }
  audioContext = new (window.AudioContext || window.webkitAudioContext)();
  oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = "sine";
  oscillator.frequency.value = 174;
  gain.gain.value = 0.03;
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start();
});
