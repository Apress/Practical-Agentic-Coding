"""
Multi-Agent Swarm Coordination System

This package provides a complete multi-agent coordination system
demonstrating Manager, Peer-to-Peer, and Blackboard patterns.
"""

__version__ = "1.0.0"

from starter.swarm_coordinator import SwarmCoordinator, CoordinationPattern, Task
from starter.base_agent import BaseAgent
from starter.dev_agent import DevAgent
from starter.qa_agent import QAAgent
from starter.scrum_agent import ScrumAgent
from starter.message_bus import MessageBus
from starter.blackboard import Blackboard

__all__ = [
    "SwarmCoordinator",
    "CoordinationPattern",
    "Task",
    "BaseAgent",
    "DevAgent",
    "QAAgent",
    "ScrumAgent",
    "MessageBus",
    "Blackboard",
]
