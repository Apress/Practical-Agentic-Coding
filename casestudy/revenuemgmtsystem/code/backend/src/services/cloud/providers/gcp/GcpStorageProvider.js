const StorageInterface = require('../../StorageInterface');

class GcpStorageProvider extends StorageInterface {
    constructor() {
        super();
        // Lazily initialize client
        // const { Storage } = require('@google-cloud/storage');
        // this.client = new Storage();
        this.client = {};
        console.log(`[Cloud] Initialized GCP Storage Provider`);
    }

    async uploadFile(bucketName, key, body) {
        // Implementation using Google Cloud SDK
        console.log(`[GCP Storage] Uploading to ${bucketName}/${key}`);
        // await this.client.bucket(bucketName).file(key).save(body);
        return `https://storage.googleapis.com/${bucketName}/${key}`;
    }

    async getSignedUrl(bucketName, key) {
        console.log(`[GCP Storage] Generating Signed URL for ${key}`);
        return `https://storage.googleapis.com/${bucketName}/${key}?signature=abc`;
    }
}

module.exports = GcpStorageProvider;
