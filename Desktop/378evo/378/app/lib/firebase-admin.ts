
import { initializeApp, getApps, App, ServiceAccount, cert } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import { getFirestore } from 'firebase-admin/firestore';
import { getStorage } from 'firebase-admin/storage';

let adminApp: App;

const serviceAccount: ServiceAccount = {
  projectId: process.env.FIREBASE_ADMIN_PROJECT_ID,
  privateKey: process.env.FIREBASE_ADMIN_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  clientEmail: process.env.FIREBASE_ADMIN_CLIENT_EMAIL,
};

const databaseURL = "https://intelliaudit-ai-default-rtdb.asia-southeast1.firebasedatabase.app";

if (getApps().length === 0) {
  // For local development, use the service account from environment variables.
  // In a deployed App Hosting environment, these variables won't be set, and it will fall back to Application Default Credentials.
  if (process.env.FIREBASE_ADMIN_PRIVATE_KEY) {
    adminApp = initializeApp({
        credential: cert(serviceAccount),
        databaseURL
    });
  } else {
    // Use Application Default Credentials in production
    adminApp = initializeApp({ databaseURL });
  }
} else {
  adminApp = getApps()[0];
}

const adminAuth = getAuth(adminApp);
const adminDb = getFirestore(adminApp);
const adminStorage = getStorage(adminApp);

export { adminApp, adminAuth, adminDb, adminStorage };
