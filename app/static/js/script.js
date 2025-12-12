const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeBtn = document.getElementById('removeBtn');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const successMessage = document.getElementById('successMessage');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');

let selectedFile = null;

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
const ALLOWED_TYPES = [
    'text/csv'
];

const ALLOWED_EXTENSIONS = ['.csv'];

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

removeBtn.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    filePreview.classList.remove('active');
    submitBtn.disabled = true;
    hideError();
    hideSuccess();
});

submitBtn.addEventListener('click', async () => {
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    hideError();
    hideSuccess();
    submitBtn.textContent = 'Procesando';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/caminos_mas_cortos', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);
            saveFile(blobUrl, 'rutas.json');
            URL.revokeObjectURL(blobUrl);

            showSuccess('Archivo procesado con éxito.');
        } else {
            console.error('Error de procesamiento', response.statusText);
            throw new Error("Se produjo un error en el procesamiento.");
        }
    } catch (error) {
        console.error('Error de procesamiento:', error);
        showError('Error de procesamiento.');
    } finally {
        submitBtn.textContent = 'Procesar';
        submitBtn.disabled = false;
    }
});

function handleFile(file) {
    hideError();
    hideSuccess();

    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_TYPES.includes(file.type) && !ALLOWED_EXTENSIONS.includes(fileExtension)) {
        showError('Formato inválido. Solo puede procesar archivos CSV.');
        return;
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
        showError(`File size exceeds 100MB. Your file is ${formatFileSize(file.size)}.`);
        return;
    }

    // File is valid
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    filePreview.classList.add('active');
    submitBtn.disabled = false;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.add('active');
}

function hideError() {
    errorMessage.classList.remove('active');
}

function showSuccess(message) {
    successText.textContent = message;
    successMessage.classList.add('active');
}

function hideSuccess() {
    successMessage.classList.remove('active');
}

function saveFile(url, filename) {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename || "file-name";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
