/**
 * End-to-End Encryption Service for API Gateway
 * Implements AES-256 encryption with secure key management
 */

const crypto = require('crypto');
const fs = require('fs');

class EncryptionService {
    constructor(masterKey = null) {
        this.masterKey = masterKey || process.env.ENCRYPTION_MASTER_KEY || 'default-key-change-in-production';
        this.keySize = 32;  // 256 bits
        this.ivSize = 16;   // 128 bits
        this.saltSize = 32; // 256 bits
    }
    
    generateKey(password, salt = null) {
        // Generate encryption key from password using PBKDF2
        if (!salt) {
            salt = crypto.randomBytes(this.saltSize);
        }
        
        const key = crypto.pbkdf2Sync(password, salt, 100000, this.keySize, 'sha256');
        return [key, salt];
    }
    
    encryptData(data, key = null) {
        // Generate key if not provided
        let encryptionKey, salt;
        
        if (!key) {
            [encryptionKey, salt] = this.generateKey(this.masterKey);
        } else {
            encryptionKey = key;
            salt = crypto.randomBytes(this.saltSize);
        }
        
        // Generate random IV
        const iv = crypto.randomBytes(this.ivSize);
        
        // Create cipher
        const cipher = crypto.createCipher('aes-256-cbc', encryptionKey);
        cipher.setAutoPadding(true);
        
        // Encrypt
        let encryptedData = cipher.update(data);
        encryptedData = Buffer.concat([encryptedData, cipher.final()]);
        
        // Return encrypted data as base64 strings
        return {
            encrypted_data: encryptedData.toString('base64'),
            iv: iv.toString('base64'),
            salt: salt.toString('base64')
        };
    }
    
    decryptData(encryptedData, iv, salt, key = null) {
        try {
            // Decode base64 strings
            const encryptedBytes = Buffer.from(encryptedData, 'base64');
            const ivBytes = Buffer.from(iv, 'base64');
            const saltBytes = Buffer.from(salt, 'base64');
            
            // Generate key
            let decryptionKey;
            if (!key) {
                [decryptionKey, _] = this.generateKey(this.masterKey, saltBytes);
            } else {
                decryptionKey = key;
            }
            
            // Create decipher
            const decipher = crypto.createDecipher('aes-256-cbc', decryptionKey);
            decipher.setAutoPadding(true);
            
            // Decrypt
            let decryptedData = decipher.update(encryptedBytes);
            decryptedData = Buffer.concat([decryptedData, decipher.final()]);
            
            return decryptedData;
            
        } catch (error) {
            console.error(`Decryption failed: ${error}`);
            throw new Error('Failed to decrypt data');
        }
    }
    
    encryptFile(filePath, outputPath, key = null) {
        try {
            const data = fs.readFileSync(filePath);
            const encryptedInfo = this.encryptData(data, key);
            
            // Save encrypted data
            fs.writeFileSync(outputPath, encryptedInfo.encrypted_data);
            
            return encryptedInfo;
            
        } catch (error) {
            console.error(`File encryption failed: ${error}`);
            throw error;
        }
    }
    
    decryptFile(encryptedFilePath, outputPath, iv, salt, key = null) {
        try {
            const encryptedData = fs.readFileSync(encryptedFilePath, 'utf8');
            const decryptedData = this.decryptData(encryptedData, iv, salt, key);
            
            fs.writeFileSync(outputPath, decryptedData);
            
            return true;
            
        } catch (error) {
            console.error(`File decryption failed: ${error}`);
            return false;
        }
    }
    
    hashData(data, algorithm = 'sha256') {
        // Generate hash of data for integrity verification
        if (algorithm === 'sha256') {
            return crypto.createHash('sha256').update(data).digest('hex');
        } else if (algorithm === 'sha512') {
            return crypto.createHash('sha512').update(data).digest('hex');
        } else {
            throw new Error('Unsupported hash algorithm');
        }
    }
    
    verifyHash(data, expectedHash, algorithm = 'sha256') {
        // Verify data integrity using hash
        const actualHash = this.hashData(data, algorithm);
        return actualHash === expectedHash;
    }
    
    generateSecureRandom(length) {
        // Generate cryptographically secure random bytes
        return crypto.randomBytes(length);
    }
    
    encryptMetadata(metadata, key = null) {
        // Encrypt metadata dictionary
        const metadataJson = JSON.stringify(metadata);
        const metadataBuffer = Buffer.from(metadataJson, 'utf8');
        
        return this.encryptData(metadataBuffer, key);
    }
    
    decryptMetadata(encryptedInfo, key = null) {
        // Decrypt metadata dictionary
        const decryptedBuffer = this.decryptData(
            encryptedInfo.encrypted_data,
            encryptedInfo.iv,
            encryptedInfo.salt,
            key
        );
        
        const metadataJson = decryptedBuffer.toString('utf8');
        return JSON.parse(metadataJson);
    }
}

// Global encryption service instance
const encryptionService = new EncryptionService();

module.exports = encryptionService;
