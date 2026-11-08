const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require("@aws-sdk/client-bedrock-agent-runtime");
const dotenv = require('dotenv');

dotenv.config();

/**
 * AI Agent Service
 * Interacts with AWS Bedrock Agents to generate real-time pricing strategies and insights.
 */
class AiAgentService {
    constructor() {
        // Initialize Bedrock Client
        // Region and Credentials are automatically loaded from process.env or ~/.aws/credentials
        this.client = new BedrockAgentRuntimeClient({ region: process.env.AWS_REGION || "us-east-1" });

        this.agentId = process.env.STRATEGY_AGENT_ID; // The ID of the Agent created in AWS Console
        this.agentAliasId = process.env.STRATEGY_AGENT_ALIAS_ID || "TSTALIASID"; // 'TSTALIASID' is default for testing
    }

    /**
     * Invokes the Strategy Agent to analyze market data and generate insights.
     * @param {string} sessionId - Unique session ID for conversation context
     * @param {string} inputText - The user's prompt or system trigger (e.g., "Analyze demand for next week")
     * @returns {Promise<string>} - The agent's text response
     */
    async generateStrategy(sessionId, inputText) {
        if (!this.agentId) {
            console.warn("Bedrock Agent ID not configured. Falling back to Mock data.");
            return null;
        }

        const command = new InvokeAgentCommand({
            agentId: this.agentId,
            agentAliasId: this.agentAliasId,
            sessionId: sessionId,
            inputText: inputText,
            enableTrace: true // Useful for debugging agent reasoning steps
        });

        try {
            console.log(`Invoking Bedrock Agent (ID: ${this.agentId}) with input: "${inputText}"...`);
            const response = await this.client.send(command);

            // Bedrock returns a stream of events
            let completion = "";

            if (response.completion) {
                for await (const event of response.completion) {
                    if (event.chunk) {
                        const chunk = new TextDecoder("utf-8").decode(event.chunk.bytes);
                        completion += chunk;
                    }
                }
            }

            return completion;

        } catch (error) {
            console.error("Error invoking Strategy Agent:", error);
            throw error;
        }
    }

    /**
     * Parses the Agent's response if it returns structured JSON.
     * Use this if the Agent is prompted to output specific JSON schemas.
     */
    parseInsight(agentResponseText) {
        try {
            // Find JSON block in markdown if present
            const jsonMatch = agentResponseText.match(/```json\n([\s\S]*?)\n```/) ||
                agentResponseText.match(/\{[\s\S]*\}/);

            if (jsonMatch) {
                return JSON.parse(jsonMatch[1] || jsonMatch[0]);
            }
            return { raw: agentResponseText };
        } catch (e) {
            return { raw: agentResponseText };
        }
    }
}

module.exports = new AiAgentService();
