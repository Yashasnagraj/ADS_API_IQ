"""
Root agent definition for Google ADK
This is the main entry point that ADK looks for
"""

from google.adk import Agent
from core.orchestrator import orchestrator_agent

# ADK requires this exact variable name
root_agent: Agent = orchestrator_agent