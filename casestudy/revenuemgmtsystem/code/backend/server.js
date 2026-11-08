const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

// Import Routes
const propertyRoutes = require('./src/routes/propertyRoutes');
const dashboardRoutes = require('./src/routes/dashboardRoutes');
const settingsRoutes = require('./src/routes/settingsRoutes');
const chatRoutes = require('./src/routes/chatRoutes');
const integrationRoutes = require('./src/routes/integrationRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Traceability Middleware
app.use((req, res, next) => {
    const traceId = req.headers['x-trace-id'] || 'no-trace-id';
    console.log(`[${new Date().toISOString()}] [${traceId}] ${req.method} ${req.url}`);
    next();
});

// Health Check
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', service: 'ZenithStays API', mode: 'modular' });
});

// Mount Routes
// Mount Routes
const userRoutes = require('./src/routes/userRoutes');

app.use('/api/properties', propertyRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/settings', settingsRoutes);
app.use('/api/chat', chatRoutes);
app.use('/api/integrations', integrationRoutes);
app.use('/api/users', userRoutes);

// Global Error Handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: 'Internal Server Error', error: err.message });
});

// Start Server
app.listen(PORT, (err) => {
    // Express 5 passes a failed listen (for example EADDRINUSE) to this callback.
    if (err) {
        console.error(`Could not start the server on port ${PORT}: ${err.message}`);
        process.exit(1);
    }
    console.log(`Server running on port ${PORT}`);
    console.log(`   - Properties API: /api/properties`);
    console.log(`   - Dashboard API:  /api/dashboard`);
    console.log(`   - Settings API:   /api/settings`);
    console.log(`   - Chat API:       /api/chat`);
    console.log(`   - Integrations:   /api/integrations`);
    console.log(`   - Users API:      /api/users`);
});
