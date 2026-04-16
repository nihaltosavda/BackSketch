'use strict';

// Basic Settings
const MAX_SIZE_MB = 5;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

// Get HTML Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const processBtn = document.getElementById('process-btn');
const imgOriginal = document.getElementById('img-original');
const imgProcessed = document.getElementById('img-processed');
const downloadLink = document.getElementById('download-link');
const colorPicker = document.getElementById('color-picker');
const chkColor = document.getElementById('chk-color');
const errorMsg = document.getElementById('error-msg');

let selectedFile = null;

// Show Error
function showError(msg) {
  errorMsg.textContent = msg;
}

// Validate File
function validateFile(file) {
  if (!ALLOWED_TYPES.includes(file.type)) {
    showError("Only JPG, PNG, WEBP allowed");
    return false;
  }

  if (file.size > MAX_SIZE_BYTES) {
    showError("File too large (max 5MB)");
    return false;
  }

  return true;
}

// Select File
fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];

  if (file && validateFile(file)) {
    selectedFile = file;

    // Show preview
    imgOriginal.src = URL.createObjectURL(file);
  }
});

// Process Image
processBtn.addEventListener('click', async () => {
  if (!selectedFile) {
    showError("Please select a file first");
    return;
  }

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);

    let url = "/api/remove-bg";

    // If color option selected
    if (chkColor.checked) {
      url = "/api/replace-bg";
      formData.append('color', colorPicker.value);
    }

    // Send request to backend
    const response = await fetch(url, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error("Server error");
    }

    const blob = await response.blob();
    const imageUrl = URL.createObjectURL(blob);

    // Show processed image
    imgProcessed.src = imageUrl;

    // Download link
    downloadLink.href = imageUrl;
    downloadLink.download = "output.png";

  } catch (err) {
    showError("Something went wrong");
  }
});