"""
Scrum Master Agent implementation.

Handles task coordination, prioritization, assignment, progress monitoring,
and blocker resolution in the manager pattern.
"""

import logging
from typing import Dict, Any, List, Optional
from starter.base_agent import BaseAgent
from starter.message_bus import Message

logger = logging.getLogger(__name__)


class ScrumAgent(BaseAgent):
    """
    Scrum Master agent responsible for:
    - Task prioritization and assignment
    - Progress monitoring
    - Blocker resolution
    - Team coordination
    - Sprint management
    - Facilitating communication
    """

    def __init__(self, config: Dict[str, Any], **kwargs):
        """
        Initialize Scrum Master agent.

        Args:
            config: Configuration dictionary
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__("scrum", config, **kwargs)
        self.assigned_tasks: Dict[str, str] = {}  # task_id -> agent_id
        self.task_status: Dict[str, str] = {}  # task_id -> status
        self.blockers: List[Dict[str, Any]] = []

    def get_role_description(self) -> str:
        """Get Scrum Master role description for system prompts."""
        return """You are an experienced Scrum Master agent coordinating an agile development team.
Your responsibilities include:
- Prioritizing tasks based on value and dependencies
- Assigning tasks to appropriate team members
- Monitoring progress and identifying blockers
- Facilitating communication between team members
- Resolving conflicts and impediments
- Ensuring smooth workflow and collaboration
- Making decisions about sprint goals and timelines

You should be:
- Fair and objective in task assignments
- Proactive in identifying and resolving issues
- Clear and concise in communication
- Focused on team productivity and collaboration
- Aware of team capacity and workload

Make data-driven decisions and prioritize team success over individual tasks."""

    async def process_message(self, message: Message) -> None:
        """
        Process incoming messages.

        Args:
            message: Message to process
        """
        logger.info(f"ScrumAgent processing message: {message.message_type}")

        if message.message_type == "task_complete":
            await self._handle_task_complete(message)
        elif message.message_type == "blocker_reported":
            await self._handle_blocker(message)
        elif message.message_type == "progress_update":
            await self._handle_progress_update(message)
        elif message.message_type == "help_request":
            await self._handle_help_request(message)
        else:
            logger.debug(f"ScrumAgent ignoring message type: {message.message_type}")

    async def _handle_task_complete(self, message: Message) -> None:
        """Handle task completion notification."""
        task_id = message.payload.get("task_id")
        logger.info(f"ScrumAgent received task completion: {task_id}")
        self.task_status[task_id] = "complete"

    async def _handle_blocker(self, message: Message) -> None:
        """Handle blocker report."""
        blocker = message.payload.get("blocker")
        task_id = message.payload.get("task_id")
        logger.info(f"ScrumAgent received blocker for task {task_id}")

        self.blockers.append({
            "task_id": task_id,
            "blocker": blocker,
            "from_agent": message.from_agent
        })

        # Attempt to resolve
        await self.resolve_blockers(blocker)

    async def _handle_progress_update(self, message: Message) -> None:
        """Handle progress update from agent."""
        task_id = message.payload.get("task_id")
        progress = message.payload.get("progress")
        logger.info(f"ScrumAgent received progress update: {task_id} at {progress}%")

    async def _handle_help_request(self, message: Message) -> None:
        """Handle help request from team member."""
        task_id = message.payload.get("task_id")
        issue = message.payload.get("issue")
        logger.info(f"ScrumAgent received help request for task {task_id}")

    async def prioritize_tasks(self, tasks: List[Any]) -> List[Any]:
        """
        Prioritize list of tasks.

        Args:
            tasks: List of task objects

        Returns:
            Prioritized list of tasks
        """
        logger.info(f"ScrumAgent prioritizing {len(tasks)} tasks")

        # Build task descriptions
        task_descriptions = []
        for i, task in enumerate(tasks):
            task_id = task.id if hasattr(task, 'id') else f"task_{i}"
            description = task.description if hasattr(task, 'description') else str(task)
            task_descriptions.append(f"- {task_id}: {description}")

        tasks_text = "\n".join(task_descriptions)

        user_message = f"""Please prioritize the following tasks:

{tasks_text}

Consider:
1. Business value and impact
2. Dependencies between tasks
3. Risk and complexity
4. Team capacity and skills
5. Urgency and deadlines

Provide:
- Prioritized order (task IDs)
- Rationale for prioritization
- Any dependencies to note
- Recommended sprint grouping

Be objective and consider team efficiency."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.6
            )

            # Extract prioritized order
            prioritized_ids = self._extract_task_order(response, tasks)

            # Reorder tasks based on prioritization
            task_map = {
                (task.id if hasattr(task, 'id') else f"task_{i}"): task
                for i, task in enumerate(tasks)
            }

            prioritized_tasks = [
                task_map[task_id]
                for task_id in prioritized_ids
                if task_id in task_map
            ]

            logger.info(f"ScrumAgent prioritized tasks: {prioritized_ids}")
            return prioritized_tasks

        except Exception as e:
            logger.error(f"ScrumAgent prioritization failed: {e}")
            return tasks  # Return original order on failure

    async def assign_task(self, task: Any, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Assign task to an agent.

        Args:
            task: Task object to assign
            agent_name: Specific agent to assign to (or None to decide)

        Returns:
            Assignment result dictionary
        """
        task_id = task.id if hasattr(task, 'id') else str(task)
        description = task.description if hasattr(task, 'description') else str(task)

        logger.info(f"ScrumAgent assigning task {task_id}")

        if not agent_name:
            # Decide which agent to assign to
            agent_name = await self._decide_assignment(task)

        # Record assignment
        self.assigned_tasks[task_id] = agent_name
        self.task_status[task_id] = "assigned"

        # Send assignment message
        await self.send_message(
            to_agent=agent_name,
            message_type="task_assignment",
            payload={
                "task_id": task_id,
                "description": description,
                "assigned_by": self.agent_id
            }
        )

        logger.info(f"ScrumAgent assigned task {task_id} to {agent_name}")

        return {
            "task_id": task_id,
            "assigned_to": agent_name,
            "status": "assigned",
            "agent": self.agent_id
        }

    async def _decide_assignment(self, task: Any) -> str:
        """
        Decide which agent should handle the task.

        Args:
            task: Task to assign

        Returns:
            Agent identifier
        """
        description = task.description if hasattr(task, 'description') else str(task)

        user_message = f"""Given the following task, which team member should handle it?

Task: {description}

Available team members:
- dev: Developer agent (implements features, fixes bugs)
- qa: QA agent (tests, reviews, validates quality)

Consider:
- Task type and requirements
- Agent expertise and current workload
- Task complexity

Respond with just the agent name (dev or qa) and brief rationale."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.5
            )

            # Extract agent name from response
            if 'dev' in response.lower()[:20]:
                return 'dev'
            elif 'qa' in response.lower()[:20]:
                return 'qa'
            else:
                # Default to dev for implementation tasks
                return 'dev'

        except Exception as e:
            logger.error(f"ScrumAgent assignment decision failed: {e}")
            return 'dev'  # Default assignment

    async def monitor_progress(self, task_id: str) -> Dict[str, Any]:
        """
        Monitor progress of a task.

        Args:
            task_id: Task identifier

        Returns:
            Progress information dictionary
        """
        logger.info(f"ScrumAgent monitoring progress for task {task_id}")

        current_status = self.task_status.get(task_id, "unknown")
        assigned_to = self.assigned_tasks.get(task_id, "unassigned")

        # Check blackboard for latest state
        if self.blackboard:
            task_state = await self.read_blackboard(task_id)
            if task_state:
                current_status = task_state.status
                assigned_to = task_state.assigned_to or assigned_to

        progress = {
            "task_id": task_id,
            "status": current_status,
            "assigned_to": assigned_to,
            "blockers": [b for b in self.blockers if b.get("task_id") == task_id],
            "agent": self.agent_id
        }

        logger.info(f"ScrumAgent progress report: {task_id} is {current_status}")
        return progress

    async def resolve_blockers(self, blocker: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to resolve a blocker.

        Args:
            blocker: Blocker information

        Returns:
            Resolution result
        """
        logger.info("ScrumAgent resolving blocker")

        blocker_desc = blocker.get("description", str(blocker))
        task_id = blocker.get("task_id", "unknown")

        user_message = f"""A team member reported the following blocker:

Task ID: {task_id}
Blocker: {blocker_desc}

As Scrum Master, how would you resolve this blocker?

Provide:
1. Root cause analysis
2. Proposed resolution steps
3. Who should be involved
4. Timeline for resolution
5. Prevention measures

Be specific and actionable."""

        try:
            response = await self.query_claude(
                system_prompt=self.get_role_description(),
                user_message=user_message,
                temperature=0.7
            )

            result = {
                "task_id": task_id,
                "blocker": blocker_desc,
                "resolution": response,
                "status": "resolved",
                "agent": self.agent_id
            }

            # Remove from blockers list
            self.blockers = [b for b in self.blockers if b.get("task_id") != task_id]

            logger.info(f"ScrumAgent resolved blocker for task {task_id}")
            return result

        except Exception as e:
            logger.error(f"ScrumAgent blocker resolution failed: {e}")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_id
            }

    async def coordinate_handoff(
        self,
        task_id: str,
        from_agent: str,
        to_agent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate task handoff between agents.

        Args:
            task_id: Task identifier
            from_agent: Source agent
            to_agent: Destination agent
            context: Handoff context and data

        Returns:
            Handoff result
        """
        logger.info(f"ScrumAgent coordinating handoff: {from_agent} -> {to_agent} for task {task_id}")

        # Notify destination agent
        await self.send_message(
            to_agent=to_agent,
            message_type="task_handoff",
            payload={
                "task_id": task_id,
                "from_agent": from_agent,
                "context": context,
                "coordinated_by": self.agent_id
            }
        )

        # Update assignment
        self.assigned_tasks[task_id] = to_agent

        logger.info(f"ScrumAgent completed handoff for task {task_id}")

        return {
            "task_id": task_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "status": "handed_off",
            "agent": self.agent_id
        }

    def _extract_task_order(self, response: str, original_tasks: List[Any]) -> List[str]:
        """Extract prioritized task order from response."""
        # Extract task IDs from response
        task_ids = []
        lines = response.split('\n')

        # Get original task IDs
        original_ids = [
            task.id if hasattr(task, 'id') else f"task_{i}"
            for i, task in enumerate(original_tasks)
        ]

        # Look for task IDs in response
        for line in lines:
            for task_id in original_ids:
                if task_id in line and task_id not in task_ids:
                    task_ids.append(task_id)

        # Add any missing tasks at the end
        for task_id in original_ids:
            if task_id not in task_ids:
                task_ids.append(task_id)

        return task_ids

    def get_assigned_tasks(self) -> Dict[str, str]:
        """Get currently assigned tasks."""
        return self.assigned_tasks.copy()

    def get_task_status(self, task_id: str) -> str:
        """Get status of specific task."""
        return self.task_status.get(task_id, "unknown")

    def get_active_blockers(self) -> List[Dict[str, Any]]:
        """Get list of active blockers."""
        return self.blockers.copy()
