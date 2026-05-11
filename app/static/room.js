const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const uploadProgress = document.getElementById("upload-progress");
const uploadProgressText = document.getElementById("upload-progress-text");

uploadForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        alert("Please choose a file first.");
        return;
    }

    const formData = new FormData();
    formData.append("uploaded_file", file);

    const xhr = new XMLHttpRequest();

    xhr.open("POST", uploadForm.action);

    xhr.upload.addEventListener("progress", function (event) {
        if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);

            uploadProgress.value = percent;
            uploadProgressText.textContent = `${percent}%`;
        }
    });

    xhr.addEventListener("load", function () {
        if (xhr.status >= 200 && xhr.status < 400) {
            window.location.reload();
        } else {
            alert("Upload failed.");
        }
    });

    xhr.addEventListener("error", function () {
        alert("Upload failed because of a network error.");
    });

    xhr.send(formData);
});