const { ipcRenderer } = require('electron');

// Function to display duplicates in the table
function displayDuplicates(duplicates) {
    const tableBody = document.querySelector('#duplicatesTable tbody');
    tableBody.innerHTML = ''; // Clear previous entries

    duplicates.forEach(duplicate => {
        duplicate.locations.forEach(location => {
            const row = document.createElement('tr');
            
            // Filename cell
            const filenameCell = document.createElement('td');
            filenameCell.textContent = duplicate.filenames.join(', ');
            row.appendChild(filenameCell);

            // Location cell
            const locationCell = document.createElement('td');
            locationCell.textContent = location;
            row.appendChild(locationCell);

            // Action cell with delete button
            const actionCell = document.createElement('td');
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', async () => {
                const response = await ipcRenderer.invoke('deleteLocalFile', location);
                if (response.status === 'success') {
                    row.remove(); // Remove the row from the table
                    document.getElementById('status').innerText = 'File deleted successfully!';
                } else {
                    document.getElementById('status').innerText = 'Failed to delete file.';
                }
            });
            actionCell.appendChild(deleteButton);
            row.appendChild(actionCell);

            tableBody.appendChild(row);
        });
    });
}

// Handle folder selection
document.getElementById('selectFolder').addEventListener('click', async () => {
    const folderPath = await ipcRenderer.invoke('dialog:openFolder');
    
    if (folderPath) {
        document.getElementById('folderPath').innerText = `Selected Folder: ${folderPath}`;
        document.getElementById('uploadFiles').disabled = false;

        // Store the selected folder path
        window.selectedFolderPath = folderPath;
    }
});

// Handle file upload
document.getElementById('uploadFiles').addEventListener('click', async () => {
    const folderPath = window.selectedFolderPath;

    if (!folderPath) {
        document.getElementById('status').innerText = 'Please select a folder first!';
        return;
    }

    document.getElementById('status').innerText = 'Uploading files...';
    
    const response = await ipcRenderer.invoke('uploadFiles', folderPath);

    if (response.status === 'success') {
        document.getElementById('status').innerText = 'Files uploaded successfully!';
        // Fetch and display duplicates after upload
        const duplicates = await ipcRenderer.invoke('getDuplicates');
        displayDuplicates(duplicates);
    } else {
        document.getElementById('status').innerText = 'Failed to upload files.';
    }
});
