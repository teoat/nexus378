
'use server';

import { PlaidApi, Configuration, PlaidEnvironments } from 'plaid';
import { adminDb } from './firebase-admin';
// In the future, we would import the QuickBooks SDK here as well.
// import QuickBooks from 'node-quickbooks';

const plaidConfig = new Configuration({
    basePath: PlaidEnvironments[process.env.PLAID_ENV || 'sandbox'],
    baseOptions: {
        headers: {
            'PLAID-CLIENT-ID': process.env.PLAID_CLIENT_ID,
            'PLAID-SECRET': process.env.PLAID_SECRET,
        },
    },
});

const plaidClient = new PlaidApi(plaidConfig);

/**
 * Creates a Plaid Link token for the frontend to initialize the Plaid Link flow.
 * @param userId The ID of the user to associate the token with.
 * @returns The Link token.
 */
export async function createPlaidLinkToken(userId: string) {
    try {
        const response = await plaidClient.linkTokenCreate({
            user: { client_user_id: userId },
            client_name: 'IntelliAudit AI',
            products: ['transactions'],
            country_codes: ['US'],
            language: 'en',
        });
        return response.data.link_token;
    } catch (error) {
        console.error("Failed to create Plaid Link token:", error);
        throw new Error("Could not initialize secure bank connection.");
    }
}

/**
 * Exchanges a public token from the Plaid Link flow for an access token.
 * @param publicToken The public token to exchange.
 * @returns The access token and item ID.
 */
export async function exchangePublicToken(publicToken: string) {
    try {
        const response = await plaidClient.itemPublicTokenExchange({
            public_token: publicToken,
        });
        // These tokens should be securely stored, e.g., in a secure backend database.
        return {
            accessToken: response.data.access_token,
            itemId: response.data.item_id,
        };
    } catch (error) {
        console.error("Failed to exchange public token:", error);
        throw new Error("Failed to finalize secure bank connection.");
    }
}


/**
 * Placeholder function to initiate OAuth2 flow with QuickBooks.
 * @param userId The user initiating the connection.
 * @returns The authorization URL.
 */
export async function getQuickBooksAuthUrl(userId: string): Promise<string> {
    // This is a placeholder. A real implementation would use the node-quickbooks library
    // to generate an authorization URI and store the request token.
    console.log(`Generating QuickBooks auth URL for user ${userId}`);
    
    // In a real app, the client ID would be from env vars and the redirect URI would be the deployed app's URL.
    const client_id = process.env.QUICKBOOKS_CLIENT_ID || 'ABc123';
    const redirect_uri = process.env.NODE_ENV === 'production' 
        ? `https://${process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN}/api/auth/quickbooks/callback`
        : `http://localhost:3000/api/auth/quickbooks/callback`;
    const state = userId; // Use user ID as state to identify the user on callback.

    return `https://appcenter.intuit.com/connect/oauth2?client_id=${client_id}&scope=com.intuit.quickbooks.accounting&redirect_uri=${redirect_uri}&response_type=code&state=${state}`;
}

/**
 * Placeholder function to handle the OAuth2 callback from QuickBooks.
 * @param code The authorization code from the redirect.
 * @param userId The state parameter, which we set as the user's ID.
 * @returns The access and refresh tokens.
 */
export async function handleQuickBooksCallback(code: string, userId: string): Promise<{ success: boolean }> {
    // This is a placeholder. A real implementation would exchange the authorization code
    // for an access token and refresh token using the node-quickbooks library.
    console.log(`Handling QuickBooks callback for user ${userId} with code ${code}`);
    
    // Here you would exchange the code for tokens and securely store them.
    // For this example, we'll just mark the user as connected in Firestore.
    try {
        await adminDb.collection('users').doc(userId).set({ quickbooksConnected: true }, { merge: true });
        return { success: true };
    } catch (error) {
        console.error("Failed to update user's QuickBooks status:", error);
        return { success: false };
    }
}
