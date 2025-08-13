
import { initializeApp, getApps, getApp, FirebaseApp } from 'firebase/app';
import { getAuth, Auth } from 'firebase/auth';
import { getFirestore, Firestore } from "firebase/firestore";
import { getFunctions, Functions } from 'firebase/functions';
import { getAnalytics, Analytics, isSupported as isAnalyticsSupported } from "firebase/analytics";
import { getPerformance, Performance } from "firebase/performance";
import { getRemoteConfig, RemoteConfig } from "firebase/remote-config";
import { firebaseConfig } from '@/app/firebase-config';
import { initializeAppCheck, ReCaptchaV3Provider, AppCheck } from 'firebase/app-check';

let app: FirebaseApp;
let auth: Auth;
let db: Firestore;
let functions: Functions;
let analytics: Analytics | null = null;
let performance: Performance | null = null;
let remoteConfig: RemoteConfig | null = null;
let appCheck: AppCheck | null = null;

if (getApps().length === 0) {
  app = initializeApp(firebaseConfig);
} else {
  app = getApp();
}

// Initialize services
auth = getAuth(app);
db = getFirestore(app);
functions = getFunctions(app);

// Initialize App Check with a reCAPTCHA v3 provider
// Make sure to set the NEXT_PUBLIC_RECAPTCHA_SITE_KEY environment variable.
if (typeof window !== 'undefined') {
    if (process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY) {
        appCheck = initializeAppCheck(app, {
            provider: new ReCaptchaV3Provider(process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY),
            isTokenAutoRefreshEnabled: true
        });
    } else {
        console.warn("NEXT_PUBLIC_RECAPTCHA_SITE_KEY is not set. App Check is disabled.");
    }
}


// Initialize Analytics, Performance, and Remote Config only in the browser
if (typeof window !== 'undefined') {
    isAnalyticsSupported().then(supported => {
        if (supported) {
            analytics = getAnalytics(app);
        }
    });
    performance = getPerformance(app);
    
    // Initialize and configure Remote Config
    remoteConfig = getRemoteConfig(app);
    remoteConfig.settings.minimumFetchIntervalMillis = 10000; // 10 seconds for development
    remoteConfig.defaultConfig = {
      "welcome_message": "Welcome to IntelliAudit AI",
      "enable_frenly_agent": false,
    };
}


export { app, auth, db, functions, analytics, performance, remoteConfig, appCheck };
