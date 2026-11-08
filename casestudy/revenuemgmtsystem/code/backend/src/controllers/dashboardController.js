const mockDataService = require('../services/mockDataService');
const aiAgentService = require('../services/aiAgentService');
const { v4: uuidv4 } = require('uuid');

const getStats = (req, res) => {
    const { propertyId } = req.query;
    console.log(`[DashboardController] Fetching stats for Property ID: ${propertyId}`);
    res.json(mockDataService.getDashboardStats(propertyId));
};

const getChart = (req, res) => {
    const { propertyId } = req.query;
    console.log(`[DashboardController] Fetching chart data for Property ID: ${propertyId}`);
    res.json(mockDataService.getDashboardChart(propertyId));
};

const getInsight = async (req, res) => {
    const { propertyId } = req.query;
    console.log(`[DashboardController] Fetching insights for Property ID: ${propertyId}`);

    try {
        const sessionId = req.headers['x-session-id'] || uuidv4();

        // 1. Attempt to get Real AI Insight from AWS Bedrock
        // We prompt the agent with the current context
        const prompt = `Analyze current demand for property ${propertyId || 'Miami'} and suggest pricing actions.`;

        // This will return null if STRATEGY_AGENT_ID is not set in env
        const agentResponse = await aiAgentService.generateStrategy(sessionId, prompt);

        if (agentResponse) {
            console.log(`[DashboardController] Serving AI generated insight`);
            const parsed = aiAgentService.parseInsight(agentResponse);

            // Format to match our UI expected schema
            return res.json({
                id: uuidv4(),
                description: parsed.description || parsed.raw || agentResponse,
                source: 'Bedrock Agent'
            });
        }

        // 2. Fallback to Mock Data (if Agent ID not set or fails)
        console.log('[DashboardController] Using Mock Insight (Agent not configured)');
        res.json(mockDataService.getDashboardInsight(propertyId));

    } catch (error) {
        console.error('[DashboardController] Agent Error, falling back to mock:', error.message);
        res.json(mockDataService.getDashboardInsight(propertyId));
    }
};

const approveInsight = (req, res) => {
    // In a real app, this would update the DB or trigger the Execution Agent
    res.json({ success: true, message: 'Action approved' });
};

module.exports = {
    getStats,
    getChart,
    getInsight,
    approveInsight
};
