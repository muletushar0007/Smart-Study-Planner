import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv

load_dotenv()
service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "service-account-file.json")
cred = credentials.Certificate(service_account_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

try:
    uid = "test-uid-123"
    email = "test@example.com"
    username = "testuser"
    
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        print("User does not exist, creating...")
        user_data = {
            "username": username,
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        user_ref.set(user_data)
        print("User stored in Firestore successfully!")
    else:
        print("User already exists!")
except Exception as e:
    print(f"Error: {e}")
