const room = document.querySelector(".room");
const sessionId = room.dataset.sessionId;
const currentUser = room.dataset.currentUser;
const scheme = window.location.protocol === "https:" ? "wss" : "ws";
const socket = new WebSocket(`${scheme}://${window.location.host}/ws/study-room/${sessionId}/`);


// This file controls the live study room experience.
// the browser uses:
// 1. WebSocket messages to coordinate the room, chat, whiteboard, and WebRTC setup.
// 2. WebRTC to send camera, microphone, and screen-sharing media between students.
// 3. DOM event listeners to react when users click buttons, type chat, draw, or enter Focus Mode.
// Good demo path: join a room, turn mic/camera on or off, send chat, draw on the board,
// share the screen, enable Focus Mode, then explain how each section below supports that flow.

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
  // Sends a small JSON message to Django Channels.
  // These messages do not carry the video itself; they coordinate room events.
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(payload));
  }
}

async function startMedia() {
  // Asks the browser for permission to use the camera and microphone.
  // If permission is denied, the app still allows chat and whiteboard use.
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
  // Creates the WebRTC connection used for direct browser-to-browser media.
  // The STUN server helps browsers discover how to connect across networks.
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
  // Handles every real-time event coming from the server:
  // presence updates, WebRTC offers/answers, ICE candidates, chat, and whiteboard drawing.
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
  // Enables or disables the user's microphone track without leaving the room.
  localStream?.getAudioTracks().forEach(track => track.enabled = !track.enabled);
});

document.getElementById("toggleCamera").addEventListener("click", () => {
  // Enables or disables the user's camera track without ending the WebRTC connection.
  localStream?.getVideoTracks().forEach(track => track.enabled = !track.enabled);
});

document.getElementById("shareScreen").addEventListener("click", async () => {
  // Replaces the camera video track with the screen-sharing track.
  // When screen sharing stops, the app switches the connection back to the camera.
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
  // Sends chat text through the WebSocket and immediately shows it for the sender.
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  send({ type: "chat", message });
  appendChat("You", message);
  chatInput.value = "";
});

function appendChat(user, message) {
  // Adds one chat line to the chat panel and keeps the latest message visible.
  const line = document.createElement("p");
  line.innerHTML = `<strong>${user}:</strong> ${escapeHtml(message)}`;
  chatMessages.appendChild(line);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(value) {
  // Prevents typed chat text from being treated as HTML by the browser.
  return value.replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

document.querySelectorAll("[data-tab]").forEach(button => {
  // Switches between the study room side panels, such as chat and whiteboard tools.
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
  // Clears the local whiteboard and tells the other participant to clear theirs too.
  boardContext.clearRect(0, 0, whiteboard.width, whiteboard.height);
  send({ type: "clear_board" });
});

function pointerPosition(event) {
  // Converts the pointer position on the visible canvas into the canvas drawing coordinates.
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
  // Draws a line locally. If shouldSend is true, the same line is sent to the other user.
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
  // Focus Mode encourages fewer distractions by changing the room style and requesting fullscreen.
  room.classList.toggle("focus-active");
  focusWarning.classList.remove("hidden");
  try { await document.documentElement.requestFullscreen(); } catch (error) {}
});

document.addEventListener("visibilitychange", () => {
  // The app cannot block phone or system notifications, but it can warn when the tab is hidden.
  if (document.hidden) {
    tabWarnings += 1;
    focusWarning.textContent = `Focus reminder: you have switched tabs ${tabWarnings} time(s). Enable Do Not Disturb for phone notifications.`;
    focusWarning.classList.remove("hidden");
  }
});
document.addEventListener("fullscreenchange", () => {
  // Reminds the student that Focus Mode works best when the page stays fullscreen.
  if (!document.fullscreenElement) {
    focusWarning.textContent = "Fullscreen ended. The app cannot block device notifications, but Focus Mode works best in fullscreen with Do Not Disturb enabled.";
    focusWarning.classList.remove("hidden");
  }
});

let seconds = 0;
setInterval(() => {
  // Updates the visible study timer once per second.
  seconds += 1;
  const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
  const secs = String(seconds % 60).padStart(2, "0");
  document.getElementById("sessionTimer").textContent = `${mins}:${secs}`;
}, 1000);

document.getElementById("noiseButton").addEventListener("click", () => {
  // Starts or stops a quiet focus tone using the browser's Web Audio API.
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
