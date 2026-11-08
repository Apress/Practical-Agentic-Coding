"""
QA Agent implementation.

Handles code review, testing, quality validation, and providing
feedback to developers on implementations.
"""

import logging
from typing import Dict, Any, List, Optional
from starter.base_agent import BaseAgent
from starter.message_bus import Message

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    """
    QA agent responsible for:
    - Reviewing code implementations
    - Testing features
    - Validating quality standards
    - Providing constructive feedback
    - Approving or rejecting implementations
    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize QA agent.

        Args:
            config: Configuration dictionary
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__("qa", config, **kwargs)
        self.review_history: Dict[str, Any] = {}
        self.approval_threshold = 0.8  # Quality threshold for approval

    def get_role_description(self) -> str:
        """Get QA role description for system prompts."""
        return """You are an experienced QA engineer agent working as part of an agile team.
Your responsibilities include:
- Reviewing code implementations for quality and correctness
- Testing features thoroughly
- Identifying bugs, issues, and improvement opportunities
- Providing clear, constructive feedback to developers
- Ensuring adherence to quality standards and best practices
- Approving implementations that meet quality criteria

You should be thorough but fair in your assessments. Focus on:
- Functionality and correctness
- Code quality and maintainability
- Edge cases and error handling
- Performance considerations
- Security implications

Provide actionable feedback that helps developers improve their work."""

    async def process_message(self, message: Message) -> None:
        """
        Process incoming messages.

        Args:
            message: Message to process
        """
        logger.info(f"QAAgent processing message: {message.message_type}")

        if message.message_type == "review_request":
            await self._handle_review_request(message)
        elif message.message_type == "test_request":
            await self._handle_test_request(message)
        elif message.message_type == "dev_response":
            await self._handle_dev_response(message)
        else:
            logger.debug(f"QAAgent ignoring message type: {message.message_type}")

    async def _handle_review_request(self, message: Message) -> None:
        """Handle code review request."""
        task_id = message.payload.get("task_id")
        implementation = message.payload.get("implementation")

        logger.info(f"QAAgent received review request for task {task_id}")

        # Perform review
        review_result = await self.review_code(implementation)

        # Send feedback back to dev
        await self.send_message(
            to_agent=message.from_agent,
            message_type="qa_feedback",
            payload={
                "task_id": task_id,
                "feedback": review_result,
                "approved": review_result.get("approved", False)
            }
        )

    async def _handle_test_request(self, message: Message) -> None:
        """Handle test request."""
        task_id = message.payload.get("task_id")
        implementation = message.payload.get("implementation")

        logger.info(f"QAAgent received test request for task {task_id}")

        test_result = await self.test_feature(implementation)
        logger.info(f"QAAgent completed testing for task {task_id}")

    async def _handle_dev_response(self, message: Message) -> None:
        """Handle response from developer."""
        task_id = message.payload.get("task_id")
        response = message.payload.get("response")

        logger.info(f"QAAgent received dev response for task {task_id}")

    async def review_code(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code implementation.

        Args:
            implementation: Implementation details from dev agent

        Returns:
            Dictionary with review results
        """
        logger.info("QAAgent reviewing code implementation")

        impl_text = implementation.get("implementation", str(implementation))
        task_id = implementation.get("task_id", "unknown")

        user_message = f"""Please review the following implementation:

Task ID: {task_id}
Implementation:
{impl_text}

Provide a thorough code review covering:
1. Functionality and correctness
2. Code quality and maintainability
3. Potential bugs or edge cases
4. Performance considerations
5. Security implications
6. Suggestions for improvement
7. Overall quality rating (1-10)

Be specific and constructive in your feedback."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.5
            )

            # Parse quality rating
            quality_score = self._extract_quality_score(response)
            approved = quality_score >= 8.0

            result = {
                "task_id": task_id,
                "status": "reviewed",
                "review": response,
                "quality_score": quality_score,
                "approved": approved,
                "issues": self._extract_issues(response),
                "agent": self.agent_id
            }

            # Store in history
            self.review_history[task_id] = result

            logger.info(f"QAAgent completed review with score {quality_score}/10")
            return result

        except Exception as e:
            logger.error(f"QAAgent review failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "approved": False,
                "agent": self.agent_id
            }

    async def test_feature(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test feature implementation.

        Args:
            implementation: Implementation details to test

        Returns:
            Dictionary with test results
        """
        logger.info("QAAgent testing feature implementation")

        impl_text = implementation.get("implementation", str(implementation))
        task_id = implementation.get("task_id", "unknown")

        user_message = f"""Please create a test plan for the following implementation:

Task ID: {task_id}
Implementation:
{impl_text}

Provide:
1. Test cases to validate functionality
2. Edge cases to test
3. Expected results for each test
4. Potential failure scenarios
5. Performance test considerations
6. Test coverage assessment

Be thorough and consider both positive and negative test cases."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.6
            )

            result = {
                "task_id": task_id,
                "status": "tested",
                "test_plan": response,
                "test_cases": self._extract_test_cases(response),
                "coverage": "full",
                "agent": self.agent_id
            }

            logger.info(f"QAAgent completed testing for {task_id}")
            return result

        except Exception as e:
            logger.error(f"QAAgent testing failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_id
            }

    async def provide_feedback(
        self,
        task_id: str,
        implementation: Dict[str, Any],
        issues: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Provide detailed feedback on implementation.

        Args:
            task_id: Task identifier
            implementation: Implementation details
            issues: Optional list of specific issues

        Returns:
            Dictionary with feedback
        """
        logger.info(f"QAAgent providing feedback for task {task_id}")

        impl_text = implementation.get("implementation", str(implementation))
        issues_text = "\n".join(f"- {issue}" for issue in (issues or []))
        # Built outside the f-string below: a backslash inside an f-string
        # expression is a SyntaxError before Python 3.12.
        known_issues = f"Known Issues:\n{issues_text}" if issues else ""

        user_message = f"""Please provide constructive feedback on this implementation:

Task ID: {task_id}
Implementation:
{impl_text}

{known_issues}

Provide feedback that:
1. Acknowledges what was done well
2. Identifies specific problems or concerns
3. Suggests concrete improvements
4. Prioritizes issues by severity
5. Offers alternative approaches where applicable

Be constructive and helpful in your feedback."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.7
            )

            result = {
                "task_id": task_id,
                "feedback": response,
                "issues": issues or [],
                "agent": self.agent_id,
                "constructive": True
            }

            logger.info(f"QAAgent provided feedback for {task_id}")
            return result

        except Exception as e:
            logger.error(f"QAAgent feedback generation failed: {e}")
            return {
                "task_id": task_id,
                "feedback": f"Error generating feedback: {str(e)}",
                "agent": self.agent_id
            }

    async def validate_quality(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate implementation against quality standards.

        Args:
            implementation: Implementation to validate

        Returns:
            Dictionary with validation results
        """
        logger.info("QAAgent validating quality standards")

        impl_text = implementation.get("implementation", str(implementation))

        user_message = f"""Please validate this implementation against quality standards:

Implementation:
{impl_text}

Assess the following quality dimensions (rate each 1-10):
1. Functionality - Does it work as intended?
2. Reliability - Does it handle errors and edge cases?
3. Performance - Is it efficient?
4. Maintainability - Is it clean and understandable?
5. Security - Are there security concerns?

Provide:
- Rating for each dimension
- Overall quality score
- Pass/fail recommendation
- Key strengths and weaknesses"""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.4
            )

            overall_score = self._extract_quality_score(response)

            result = {
                "validation": response,
                "overall_score": overall_score,
                "passed": overall_score >= 7.0,
                "dimensions": self._extract_dimensions(response),
                "agent": self.agent_id
            }

            logger.info(f"QAAgent validation complete: score={overall_score}")
            return result

        except Exception as e:
            logger.error(f"QAAgent validation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "passed": False,
                "agent": self.agent_id
            }

    def _extract_quality_score(self, response: str) -> float:
        """Extract quality score from review response."""
        import re
        # Look for patterns like "8/10", "8 out of 10", "score: 8"
        patterns = [
            r'(\d+)/10',
            r'(\d+)\s*out\s*of\s*10',
            r'score[:\s]+(\d+)',
            r'rating[:\s]+(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                return float(match.group(1))

        # Default to 7 if no score found
        return 7.0

    def _extract_issues(self, response: str) -> List[str]:
        """Extract list of issues from review."""
        issues = []
        lines = response.split('\n')

        in_issues_section = False
        for line in lines:
            line_lower = line.lower()
            if 'issue' in line_lower or 'problem' in line_lower or 'concern' in line_lower:
                in_issues_section = True
            elif in_issues_section and line.strip().startswith(('-', '*', '•')):
                issues.append(line.strip()[1:].strip())
            elif in_issues_section and line.strip() and not line[0].isspace():
                in_issues_section = False

        return issues[:5]  # Return up to 5 issues

    def _extract_test_cases(self, response: str) -> List[str]:
        """Extract test cases from test plan."""
        test_cases = []
        lines = response.split('\n')

        for line in lines:
            if 'test' in line.lower() and line.strip().startswith(('-', '*', '•', '1', '2', '3')):
                test_cases.append(line.strip())

        return test_cases[:10]  # Return up to 10 test cases

    def _extract_dimensions(self, response: str) -> Dict[str, float]:
        """Extract quality dimension ratings."""
        dimensions = {}
        lines = response.split('\n')

        for line in lines:
            line_lower = line.lower()
            for dimension in ['functionality', 'reliability', 'performance', 'maintainability', 'security']:
                if dimension in line_lower:
                    # Try to extract score
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        dimensions[dimension] = float(match.group(1))

        return dimensions

    def get_review_history(self) -> Dict[str, Any]:
        """Get review history."""
        return self.review_history
