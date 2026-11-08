/**
 * Generic Storage Interface
 * This acts as the contract that all cloud providers must implement.
 * Business logic should ONLY rely on these methods, never on provider specifics.
 */
class StorageInterface {
    /**
     * Upload a file to object storage
     * @param {string} bucketName 
     * @param {string} key 
     * @param {Buffer|string} body 
     * @returns {Promise<string>} url
     */
    async uploadFile(bucketName, key, body) {
        throw new Error('Method not implemented');
    }

    /**
     * Get a signed URL for a file
     * @param {string} bucketName 
     * @param {string} key 
     * @returns {Promise<string>} signedUrl
     */
    async getSignedUrl(bucketName, key) {
        throw new Error('Method not implemented');
    }
}

module.exports = StorageInterface;
