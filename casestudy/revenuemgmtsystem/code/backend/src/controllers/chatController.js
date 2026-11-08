const chatController = {
    handleChat: async (req, res) => {
        const { message, sessionId } = req.body;

        // Simulate AI delay
        await new Promise(resolve => setTimeout(resolve, 800));

        let responseText = "I'm the ZenithStays AI Agent. I can help you with rates, reservations, and strategy.";

        const lowerMsg = message.toLowerCase();

        if (lowerMsg.includes('rate') || lowerMsg.includes('price')) {
            responseText = "I've analyzed the comp set. **Grand Hotel** raised their weekday rates by 12%. I recommend we match with a **5% increase** to maintain occupancy targeting 85%.";
        } else if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
            responseText = "Hello! How can I assist you with your revenue management today?";
        } else if (lowerMsg.includes('occupancy')) {
            responseText = "Current occupancy is **78%** across all properties, which is **5.2%** higher than last week.";
        } else if (lowerMsg.includes('approve')) {
            responseText = "I've processed that approval. Rates have been updated in the PMS.";
        }

        res.json({
            response: responseText,
            timestamp: new Date().toISOString()
        });
    }
};

module.exports = chatController;
