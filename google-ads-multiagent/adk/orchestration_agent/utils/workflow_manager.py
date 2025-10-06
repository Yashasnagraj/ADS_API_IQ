from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep:
    def __init__(self, agent: str, action: str, params: Dict[str, Any] = None):
        self.agent = agent
        self.action = action
        self.params = params or {}
        self.status = WorkflowStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "action": self.action,
            "params": self.params,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None
        }


class Workflow:
    def __init__(self, workflow_id: str, workflow_type: str = "sequential"):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.steps: List[WorkflowStep] = []
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.now()
        self.start_time = None
        self.end_time = None
        self.context = {}
        self.results = []

    def add_step(self, step: WorkflowStep):
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else None,
            "steps": [step.to_dict() for step in self.steps],
            "context": self.context,
            "results": self.results
        }


class WorkflowManager:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: List[str] = []
        self.max_concurrent_workflows = 5

    def create_workflow(self, workflow_id: str, workflow_type: str = "sequential") -> Workflow:
        if workflow_id in self.workflows:
            raise ValueError(f"Workflow {workflow_id} already exists")

        workflow = Workflow(workflow_id, workflow_type)
        self.workflows[workflow_id] = workflow
        logger.info(f"Created workflow {workflow_id} of type {workflow_type}")
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)

    def start_workflow(self, workflow_id: str):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        if len(self.active_workflows) >= self.max_concurrent_workflows:
            raise RuntimeError(f"Maximum concurrent workflows ({self.max_concurrent_workflows}) reached")

        workflow.status = WorkflowStatus.RUNNING
        workflow.start_time = datetime.now()
        self.active_workflows.append(workflow_id)
        logger.info(f"Started workflow {workflow_id}")

    def complete_workflow(self, workflow_id: str, results: List[Any] = None):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = WorkflowStatus.COMPLETED
        workflow.end_time = datetime.now()
        workflow.results = results or []

        if workflow_id in self.active_workflows:
            self.active_workflows.remove(workflow_id)

        logger.info(f"Completed workflow {workflow_id}")

    def fail_workflow(self, workflow_id: str, error: str):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = WorkflowStatus.FAILED
        workflow.end_time = datetime.now()

        if workflow_id in self.active_workflows:
            self.active_workflows.remove(workflow_id)

        logger.error(f"Failed workflow {workflow_id}: {error}")

    def cancel_workflow(self, workflow_id: str):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = WorkflowStatus.CANCELLED
        workflow.end_time = datetime.now()

        if workflow_id in self.active_workflows:
            self.active_workflows.remove(workflow_id)

        logger.info(f"Cancelled workflow {workflow_id}")

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        return [
            self.workflows[workflow_id].to_dict()
            for workflow_id in self.active_workflows
            if workflow_id in self.workflows
        ]

    def get_workflow_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        sorted_workflows = sorted(
            self.workflows.values(),
            key=lambda w: w.created_at,
            reverse=True
        )
        return [w.to_dict() for w in sorted_workflows[:limit]]

    def cleanup_old_workflows(self, days: int = 7):
        cutoff_date = datetime.now() - timedelta(days=days)
        workflows_to_remove = []

        for workflow_id, workflow in self.workflows.items():
            if workflow.created_at < cutoff_date and workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                workflows_to_remove.append(workflow_id)

        for workflow_id in workflows_to_remove:
            del self.workflows[workflow_id]
            logger.info(f"Removed old workflow {workflow_id}")

        return len(workflows_to_remove)

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.workflows)
        active = len(self.active_workflows)
        completed = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.COMPLETED)
        failed = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.FAILED)
        cancelled = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.CANCELLED)
        pending = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.PENDING)

        avg_duration = None
        completed_workflows = [w for w in self.workflows.values() if w.status == WorkflowStatus.COMPLETED and w.end_time and w.start_time]
        if completed_workflows:
            total_duration = sum((w.end_time - w.start_time).total_seconds() for w in completed_workflows)
            avg_duration = total_duration / len(completed_workflows)

        return {
            "total_workflows": total,
            "active_workflows": active,
            "completed_workflows": completed,
            "failed_workflows": failed,
            "cancelled_workflows": cancelled,
            "pending_workflows": pending,
            "average_duration_seconds": avg_duration,
            "max_concurrent_workflows": self.max_concurrent_workflows
        }


from datetime import timedelta