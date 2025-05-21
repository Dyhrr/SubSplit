function sendFile() {
    const input = document.getElementById("videoInput");
    const file = input.files[0];
    if (!file) return alert("No file selected");

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("status").innerText = "Processing...";

    fetch("http://127.0.0.1:8000/transcribe", {
        method: "POST",
        body: formData
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "subtitled_output.mp4";
        a.click();
        document.getElementById("status").innerText = "Done!";
    })
    .catch(err => {
        console.error(err);
        document.getElementById("status").innerText = "Error occurred.";
    });
}

document.getElementById("submitBtn").addEventListener("click", async () => {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const statusText = document.getElementById("statusText");
  const progressContainer = document.getElementById("progressContainer");
  const progressBar = document.getElementById("progressBar");

  if (!file) {
    statusText.textContent = "Please choose a file first.";
    return;
  }

  // Reset
 statusText.innerHTML = "⏳ <em>Uploading your file...</em>";
  progressContainer.classList.remove("hidden");
  progressBar.style.width = "10%";

  const formData = new FormData();
  formData.append("file", file);

  try {
    progressBar.style.width = "40%";
    const res = await fetch("/transcribe", {
      method: "POST",
      body: formData,
    });

    progressBar.style.width = "90%";

    if (res.ok) {
      statusText.innerHTML = "✅ <strong>Done! Subtitles burned in.</strong>"
      progressBar.style.width = "100%";
    } else {
      statusText.innerHTML = "❌ Something went wrong. Try again.";
      progressBar.style.width = "0%";
    }
  } catch (err) {
    statusText.textContent = "Error occurred during upload.";
    progressBar.style.width = "0%";
  }
});


particlesJS("particles-js", {
  "particles": {
    "number": { "value": 40, "density": { "enable": true, "value_area": 800 } },
    "color": { "value": "#00b894" },
    "opacity": { "value": 0.4 },
    "size": { "value": 3 },
    "move": { "enable": true, "speed": 0.6 }
  },
  "interactivity": {
    "events": { "onhover": { "enable": true, "mode": "repulse" } }
  }
});


particlesJS("particles-js", {
  particles: {
    number: { value: 30, density: { enable: true, value_area: 800 } },
    color: { value: "#10b981" },
    shape: { type: "circle" },
    opacity: { value: 0.25 },
    size: { value: 2 },
    move: { enable: true, speed: 0.6 }
  },
  interactivity: {
    events: {
      onhover: { enable: true, mode: "repulse" }
    }
  }
});


// Drag & Drop Setup
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("bg-emerald-800/20");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("bg-emerald-800/20");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("bg-emerald-800/20");

  const droppedFiles = e.dataTransfer.files;
  if (droppedFiles.length) {
    fileInput.files = droppedFiles;

    // Optionally auto-submit
    document.getElementById("submitBtn").click();
  }
});
