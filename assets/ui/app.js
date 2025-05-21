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
