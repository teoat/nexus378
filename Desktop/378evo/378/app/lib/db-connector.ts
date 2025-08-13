
import { Pool } from 'pg';

// This configuration would ideally come from a secure vault or environment variables.
const dbConfig = {
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 5432,
};

const pool = new Pool(dbConfig);

/**
 * Executes a query against the PostgreSQL database.
 * @param query The SQL query to execute.
 * @param params The parameters for the query.
 * @returns The query result.
 */
export async function queryDatabase(query: string, params: any[] = []) {
    let client;
    try {
        client = await pool.connect();
        const result = await client.query(query, params);
        return result.rows;
    } catch (error) {
        console.error("Database query failed:", error);
        throw new Error("Failed to execute database query.");
    } finally {
        if (client) {
            client.release();
        }
    }
}
