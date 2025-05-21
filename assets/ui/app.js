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
  statusText.textContent = "Uploading...";
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
      statusText.textContent = "Done! Subtitles burned in.";
      progressBar.style.width = "100%";
    } else {
      statusText.textContent = "Something went wrong.";
      progressBar.style.width = "0%";
    }
  } catch (err) {
    statusText.textContent = "Error occurred during upload.";
    progressBar.style.width = "0%";
  }
});
