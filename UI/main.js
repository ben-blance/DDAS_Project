const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const FormData = require('form-data');

const UPLOAD_URL = 'http://127.0.0.1:8000/upload';
const DUPLICATES_URL = 'http://127.0.0.1:8000/duplicate';

// Create the main window
function createWindow() {
    const win = new BrowserWindow({
        webPreferences: {
            preload: path.join(__dirname, 'renderer.js'),
            nodeIntegration: true,
            contextIsolation: false
        }
    });
    win.maximize();
    win.loadFile('pages/index.html');
}

// Handle folder selection
ipcMain.handle('dialog:openFolder', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({ properties: ['openDirectory'] });
    if (!canceled && filePaths.length > 0) {
        return filePaths[0];
    }
    return null;
});

// Handle file upload
ipcMain.handle('uploadFiles', async (event, folderPath) => {
    try {
        const files = fs.readdirSync(folderPath);

        for (const file of files) {
            const filePath = path.join(folderPath, file);
            const fileBuffer = fs.readFileSync(filePath);
            const formData = new FormData();
            formData.append('file', fileBuffer, path.basename(filePath));
            formData.append('file_location', filePath);

            const response = await axios.post(UPLOAD_URL, formData, {
                headers: {
                    ...formData.getHeaders(),
                },
            });

            console.log(`Uploaded ${file}:`, response.data);
        }

        return { status: 'success', message: 'Files uploaded successfully' };
    } catch (error) {
        console.error('Error uploading files:', error);
        return { status: 'error', message: 'Failed to upload files' };
    }
});

// Fetch duplicates
ipcMain.handle('getDuplicates', async () => {
    try {
        const response = await axios.get(DUPLICATES_URL);
        return response.data;
    } catch (error) {
        console.error('Error fetching duplicates:', error);
        return [];
    }
});

// Delete a local file
ipcMain.handle('deleteLocalFile', async (event, filePath) => {
    try {
        fs.unlinkSync(filePath);
        return { status: 'success' };
    } catch (error) {
        console.error('Error deleting file:', error);
        return { status: 'error' };
    }
});

app.whenReady().then(() => {
    createWindow();
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
