const integrations = [
    { id: 'cloudbeds', name: 'Cloudbeds', type: 'PMS', status: 'connected', lastSync: '2023-10-25T14:30:00Z', icon: 'Cloud' },
    { id: 'mews', name: 'Mews', type: 'PMS', status: 'disconnected', lastSync: null, icon: 'Database' },
    { id: 'hostaway', name: 'Hostaway', type: 'PMS', status: 'disconnected', lastSync: null, icon: 'Cloud' },
    { id: 'synxis', name: 'SynXis', type: 'Channel Manager', status: 'connected', lastSync: '2023-10-25T15:00:00Z', icon: 'Globe' },
    { id: 'booking', name: 'Booking.com', type: 'OTA', status: 'connected', lastSync: '2023-10-25T12:00:00Z', icon: 'Globe' },
    { id: 'stripe', name: 'Stripe', type: 'Payment', status: 'connected', lastSync: '2023-10-25T15:15:00Z', icon: 'CreditCard' }
];

exports.getIntegrations = (req, res) => {
    res.json(integrations);
};

exports.connectIntegration = (req, res) => {
    const { id } = req.params;
    const { apiKey, secret } = req.body;

    // Simulate backend connection/validation
    const integration = integrations.find(i => i.id === id);
    if (!integration) return res.status(404).json({ error: 'Integration not found' });

    // Mock processing
    setTimeout(() => {
        integration.status = 'connected';
        integration.lastSync = new Date().toISOString();
        res.json({ message: 'Connected successfully', integration });
    }, 1000);
};

exports.disconnectIntegration = (req, res) => {
    const { id } = req.params;
    const integration = integrations.find(i => i.id === id);
    if (!integration) return res.status(404).json({ error: 'Integration not found' });

    integration.status = 'disconnected';
    integration.lastSync = null;
    res.json({ message: 'Disconnected successfully', integration });
};

exports.syncIntegration = (req, res) => {
    const { id } = req.params;
    const integration = integrations.find(i => i.id === id);
    if (!integration) return res.status(404).json({ error: 'Integration not found' });

    if (integration.status !== 'connected') {
        return res.status(400).json({ error: 'Cannot sync disconnected integration' });
    }

    // Mock Sync
    setTimeout(() => {
        integration.lastSync = new Date().toISOString();
        res.json({ message: 'Sync complete', lastSync: integration.lastSync });
    }, 1500);
};
