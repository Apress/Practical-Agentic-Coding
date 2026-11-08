/**
 * Factory to return the correct cloud provider implementation based on configuration.
 * Uses Lazy Loading (require inside the method) to avoid loading unused SDKs.
 */
class CloudProviderFactory {
    static getStorageProvider() {
        const provider = process.env.CLOUD_PROVIDER || 'AWS'; // Default to AWS

        console.log(`[CloudFactory] Loading Storage Provider for: ${provider}`);

        switch (provider.toUpperCase()) {
            case 'AWS':
                // Lazy load AWS provider to avoid importing GCP dependencies
                const AwsStorageProvider = require('./providers/aws/AwsStorageProvider');
                return new AwsStorageProvider(process.env.AWS_REGION);
            case 'GCP':
                // Lazy load GCP provider to avoid importing AWS dependencies
                const GcpStorageProvider = require('./providers/gcp/GcpStorageProvider');
                return new GcpStorageProvider();
            default:
                throw new Error(`Unsupported Cloud Provider: ${provider}`);
        }
    }
}

module.exports = CloudProviderFactory;
