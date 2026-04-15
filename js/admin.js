// js/admin.js
import { db, storage } from './firebase-config.js';
import { collection, addDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-firestore.js";
import { ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-storage.js";

const folderInput = document.getElementById('folderInput');
const logArea = document.getElementById('log-area');

function logAction(msg) {
    const p = document.createElement('div');
    p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logArea.appendChild(p);
    logArea.scrollTop = logArea.scrollHeight;
}

folderInput.addEventListener('change', async (event) => {
    const files = event.target.files;
    if (!files.length) return;

    logAction(`Found ${files.length} files. Starting batch upload...`);

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Example webkitRelativePath: "Website Image Scrape/Gold Page/image.webp"
        const pathParts = file.webkitRelativePath.split('/');
        
        if (pathParts.length >= 3) {
            const rootDir = pathParts[0]; // Website Image Scrape
            const collectionName = pathParts[1]; // Gold Page, Antiques Page, etc.
            const fileName = pathParts.slice(2).join('/'); // filename
            
            // Generate a clean product name from filename
            const cleanName = fileName.replace(/\.[^/.]+$/, "").replace(/-/g, " ");

            try {
                // 1. Upload to Storage
                logAction(`Uploading to Storage: ${collectionName}/${fileName}`);
                const storageRef = ref(storage, `${collectionName}/${fileName}`);
                const snapshot = await uploadBytes(storageRef, file);
                const downloadURL = await getDownloadURL(snapshot.ref);

                // 2. Add to Firestore Database Table
                logAction(`Writing Database Entry for: ${cleanName} into [${collectionName}]`);
                const collectionRef = collection(db, collectionName);
                await addDoc(collectionRef, {
                    name: cleanName,
                    price: 0, // Placeholder price
                    description: `Beautiful item from our ${collectionName} collection.`,
                    image: downloadURL,
                    category: collectionName.replace(' Page', '').toLowerCase(),
                    createdAt: serverTimestamp()
                });

                logAction(`SUCCESS >> ${fileName} created in ${collectionName}`);
            } catch (error) {
                logAction(`ERROR on ${fileName}: ${error.message}`);
                console.error(error);
            }
        } else {
            // Ignore system files or files at root level of the folder
            logAction(`Skipping root file: ${file.name}`);
        }
    }

    logAction("✅ FINISHED: Database population complete.");
});
