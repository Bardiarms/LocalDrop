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


const downloadProgress = document.getElementById("download-progress");
const downloadProgressText = document.getElementById("download-progress-text");
const downloadButtons = document.querySelectorAll(".download-button");

downloadButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        const downloadUrl = button.dataset.url;
        const filename = button.dataset.filename;

        downloadProgress.value = 0;
        downloadProgressText.textContent = "0%";

        const xhr = new XMLHttpRequest();

        xhr.open("GET", downloadUrl);
        xhr.responseType = "blob";

        xhr.addEventListener("progress", function (event) {
            if (event.lengthComputable) {
                const percent = Math.round((event.loaded / event.total) * 100);

                downloadProgress.value = percent;
                downloadProgressText.textContent = `${percent}%`;
            } else {
                downloadProgressText.textContent = "Downloading...";
            }
        });

        xhr.addEventListener("load", function () {
            if (xhr.status >= 200 && xhr.status < 400) {
                const blob = xhr.response;
                const objectUrl = URL.createObjectURL(blob);

                const temporaryLink = document.createElement("a");
                temporaryLink.href = objectUrl;
                temporaryLink.download = filename;

                document.body.appendChild(temporaryLink);
                temporaryLink.click();

                document.body.removeChild(temporaryLink);
                URL.revokeObjectURL(objectUrl);

                downloadProgress.value = 100;
                downloadProgressText.textContent = "100%";
            } else {
                alert("Download failed. Status: " + xhr.status);
            }
        });

        xhr.addEventListener("error", function () {
            alert("Download failed because of a network error.");
        });

        xhr.send();
    });
});