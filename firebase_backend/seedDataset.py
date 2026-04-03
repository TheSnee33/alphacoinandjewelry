import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import time

# ==============================================================================
# SECURE CONFIGURATION: ALPHA COIN & JEWELRY ONLY
# DO NOT REUSE EXISTING COLEMAN APP CREDENTIALS
# ==============================================================================

SERVICE_ACCOUNT_PATH = 'serviceAccountKey.json'
PRODUCT_IMG_DIR = r'../productimgdir'
CLOUD_STORAGE_BUCKET = 'alpha-coin-jewelry.appspot.com'  # Replace with actual Alpha Coin bucket

def initialize_firebase():
    """Initializes the secure isolated Alpha Coin Firebase environment."""
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        print(f"Error: {SERVICE_ACCOUNT_PATH} not found.")
        print("Please download the new Alpha Coin & Jewelry Service Account Key from your Google Console and place it here.")
        exit(1)

    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': CLOUD_STORAGE_BUCKET
        })
        print("Successfully connected to the isolated Alpha Coin Firebase environment.")
        return firestore.client(), storage.bucket()
    except Exception as e:
        print(f"Failed to connect to Firebase: {e}")
        exit(1)

def seed_database(db, bucket):
    """Parses local productimgdir and pushes items to cloud storage & firestore."""
    if not os.path.exists(PRODUCT_IMG_DIR):
        print(f"Directory {PRODUCT_IMG_DIR} does not exist yet. Please populate it with images.")
        return

    print("Beginning heavy-data sync from productimgdir...")
    
    # Example logic for scanning and uploading files
    for root, dirs, files in os.walk(PRODUCT_IMG_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            blob_path = f"products/{file}"
            
            # 1. Upload to Firebase Storage
            blob = bucket.blob(blob_path)
            # blob.upload_from_filename(file_path)
            # blob.make_public()
            # print(f"Uploaded {file} to Storage.")
            
            # 2. Add Record to Firestore Database
            # doc_ref = db.collection('products').document()
            # doc_ref.set({
            #     'name': file.split('.')[0],
            #     'imageUrl': blob.public_url,
            #     'created_at': time.time()
            # })
            # print(f"Registered FireStore Database Document for {file}.")

if __name__ == '__main__':
    db, bucket = initialize_firebase()
    seed_database(db, bucket)
    print("Database seeding completed.")
