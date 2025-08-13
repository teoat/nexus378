
"use client";

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { 
    getAuth, 
    onAuthStateChanged, 
    User, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut,
    GoogleAuthProvider,
    SAMLAuthProvider,
    signInWithPopup
} from 'firebase/auth';
import { app } from '@/lib/firebase';
import { useAuditStore } from './use-audit-store';
import { createSession, deleteSession } from '@/app/actions/auth.actions';

const auth = getAuth(app);

interface AuthContextType {
    user: User | null;
    loading: boolean;
    signUp: (email: string, pass: string) => Promise<any>;
    signIn: (email: string, pass: string) => Promise<any>;
    signInWithGoogle: () => Promise<any>;
    signInWithSSO: () => Promise<any>;
    logout: () => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const setOwnerId = useAuditStore(state => state.setOwnerId);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (user) => {
            setUser(user);
            setOwnerId(user ? user.uid : null);
            if (user) {
                const token = await user.getIdToken();
                await createSession(token);
            } else {
                await deleteSession();
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, [setOwnerId]);

    const signUp = (email: string, pass: string) => {
        return createUserWithEmailAndPassword(auth, email, pass);
    }
    
    const signIn = (email: string, pass: string) => {
        return signInWithEmailAndPassword(auth, email, pass);
    }

    const signInWithGoogle = () => {
        const provider = new GoogleAuthProvider();
        return signInWithPopup(auth, provider);
    }
    
    const signInWithSSO = () => {
        // This provider ID must match the one configured in the Firebase console.
        const provider = new SAMLAuthProvider('saml.intelliaudit-sso');
        return signInWithPopup(auth, provider);
    }

    const logout = () => {
        return signOut(auth);
    }

    const value = {
        user,
        loading,
        signUp,
        signIn,
        signInWithGoogle,
        signInWithSSO,
        logout
    };

    return <AuthContext.Provider value={value}>{!loading && children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
