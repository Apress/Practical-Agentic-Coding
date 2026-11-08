"""
Developer Agent implementation.

Handles feature implementation, bug fixes, and code modifications.
Responds to feedback from QA and collaborates on improvements.
"""

import logging
from typing import Dict, Any, Optional
from starter.base_agent import BaseAgent
from starter.message_bus import Message

logger = logging.getLogger(__name__)


class DevAgent(BaseAgent):
    """
    Developer agent responsible for:
    - Implementing features
    - Fixing bugs
    - Responding to QA feedback
    - Code modifications and improvements
    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize developer agent.

        Args:
            config: Configuration dictionary
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__("dev", config, **kwargs)
        self.current_task: Optional[str] = None
        self.implementation_history: Dict[str, Any] = {}

    def get_role_description(self) -> str:
        """Get developer role description for system prompts."""
        return """You are a skilled software developer agent working as part of an agile team.
Your responsibilities include:
- Implementing features based on requirements
- Writing clean, maintainable code
- Fixing bugs and addressing issues
- Responding constructively to QA feedback
- Collaborating with team members
- Following best practices and coding standards

You should provide clear, concise responses about your work and be open to feedback.
When implementing features, explain your approach and any trade-offs considered."""

    async def process_message(self, message: Message) -> None:
        """
        Process incoming messages.

        Args:
            message: Message to process
        """
        logger.info(f"DevAgent processing message: {message.message_type}")

        if message.message_type == "task_assignment":
            await self._handle_task_assignment(message)
        elif message.message_type == "qa_feedback":
            await self._handle_qa_feedback(message)
        elif message.message_type == "review_complete":
            await self._handle_review_complete(message)
        else:
            logger.debug(f"DevAgent ignoring message type: {message.message_type}")

    async def _handle_task_assignment(self, message: Message) -> None:
        """Handle task assignment from Scrum Master."""
        task_id = message.payload.get("task_id")
        self.current_task = task_id
        logger.info(f"DevAgent assigned task: {task_id}")

    async def _handle_qa_feedback(self, message: Message) -> None:
        """Handle feedback from QA agent."""
        feedback = message.payload.get("feedback")
        task_id = message.payload.get("task_id")
        logger.info(f"DevAgent received QA feedback for task {task_id}")

        # Process feedback and potentially respond
        response = await self.respond_to_feedback(feedback)
        logger.info(f"DevAgent response to feedback: {response[:100]}...")

    async def _handle_review_complete(self, message: Message) -> None:
        """Handle review completion notification."""
        task_id = message.payload.get("task_id")
        approved = message.payload.get("approved", False)
        logger.info(f"DevAgent notified: task {task_id} review complete (approved={approved})")

    async def implement_feature(self, task: Any) -> Dict[str, Any]:
        """
        Implement a feature based on task description.

        Args:
            task: Task object with description and requirements

        Returns:
            Dictionary with implementation details
        """
        task_id = task.id if hasattr(task, 'id') else str(task)
        description = task.description if hasattr(task, 'description') else str(task)

        logger.info(f"DevAgent implementing feature: {task_id}")

        # Build prompt for Claude
        user_message = f"""Please implement the following feature:

Task ID: {task_id}
Description: {description}

Provide:
1. High-level implementation approach
2. Key components or modules needed
3. Potential challenges or considerations
4. Estimated complexity (low/medium/high)
5. Any dependencies or prerequisites

Be concise but thorough in your response."""

        try:
            # Query Claude for implementation approach
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.7
            )

            # Structure the result
            result = {
                "task_id": task_id,
                "status": "implemented",
                "implementation": response,
                "agent": self.agent_id,
                "approach": self._extract_approach(response),
                "complexity": self._extract_complexity(response)
            }

            # Store in history
            self.implementation_history[task_id] = result

            logger.info(f"DevAgent completed implementation for {task_id}")
            return result

        except Exception as e:
            logger.error(f"DevAgent implementation failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_id
            }

    async def fix_bug(self, bug_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fix a reported bug.

        Args:
            bug_description: Description of the bug
            context: Optional context about the bug

        Returns:
            Dictionary with fix details
        """
        logger.info(f"DevAgent fixing bug: {bug_description[:50]}...")

        user_message = f"""Please analyze and fix the following bug:

Bug Description: {bug_description}

{f"Additional Context: {context}" if context else ""}

Provide:
1. Root cause analysis
2. Proposed fix approach
3. Steps to verify the fix
4. Potential side effects or risks

Be specific and actionable."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.6
            )

            result = {
                "bug_description": bug_description,
                "status": "fixed",
                "fix_details": response,
                "agent": self.agent_id,
                "root_cause": self._extract_root_cause(response)
            }

            logger.info("DevAgent completed bug fix")
            return result

        except Exception as e:
            logger.error(f"DevAgent bug fix failed: {e}")
            return {
                "bug_description": bug_description,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_id
            }

    async def respond_to_feedback(self, feedback: Dict[str, Any]) -> str:
        """
        Respond to QA feedback.

        Args:
            feedback: Feedback from QA agent

        Returns:
            Response string
        """
        logger.info("DevAgent responding to QA feedback")

        feedback_text = feedback.get("feedback", str(feedback))
        issues = feedback.get("issues", [])

        user_message = f"""You received the following feedback from QA:

{feedback_text}

{f"Specific Issues: {', '.join(issues)}" if issues else ""}

Please provide:
1. Your response to the feedback
2. How you will address each issue
3. Any clarifications needed
4. Timeline for fixes (if applicable)

Be professional and constructive."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.7
            )

            logger.info("DevAgent generated feedback response")
            return response

        except Exception as e:
            logger.error(f"DevAgent feedback response failed: {e}")
            return f"Error generating response: {str(e)}"

    async def collaborate_with_qa(self, task_id: str, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Directly collaborate with QA agent (for peer-to-peer pattern).

        Args:
            task_id: Task identifier
            implementation: Implementation details to share

        Returns:
            Collaboration result
        """
        logger.info(f"DevAgent collaborating with QA on task {task_id}")

        # Send implementation to QA for review
        await self.send_message(
            to_agent="qa",
            message_type="review_request",
            payload={
                "task_id": task_id,
                "implementation": implementation,
                "from_agent": self.agent_id
            }
        )

        return {
            "status": "collaboration_initiated",
            "task_id": task_id,
            "message_sent": "review_request"
        }

    def _extract_approach(self, response: str) -> str:
        """Extract implementation approach from response."""
        # Simple extraction - look for approach section
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if 'approach' in line.lower():
                # Return next few lines
                return '\n'.join(lines[i:i+3])
        return response[:200]  # Fallback to first 200 chars

    def _extract_complexity(self, response: str) -> str:
        """Extract complexity estimation from response."""
        response_lower = response.lower()
        if 'low' in response_lower and 'complexity' in response_lower:
            return "low"
        elif 'high' in response_lower and 'complexity' in response_lower:
            return "high"
        elif 'medium' in response_lower and 'complexity' in response_lower:
            return "medium"
        return "unknown"

    def _extract_root_cause(self, response: str) -> str:
        """Extract root cause from bug fix response."""
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if 'root cause' in line.lower():
                return '\n'.join(lines[i:i+2])
        return response[:150]

    def get_implementation_history(self) -> Dict[str, Any]:
        """Get implementation history."""
        return self.implementation_history

    def get_current_task(self) -> Optional[str]:
        """Get currently assigned task."""
        return self.current_task
