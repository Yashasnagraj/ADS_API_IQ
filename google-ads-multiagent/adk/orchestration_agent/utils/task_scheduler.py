from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from queue import PriorityQueue
import uuid

logger = logging.getLogger(__name__)


class TaskPriority:
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class ScheduledTask:
    def __init__(self, task_id: str, func: Callable, args: tuple = None, kwargs: dict = None,
                 priority: int = TaskPriority.NORMAL, scheduled_time: datetime = None):
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.priority = priority
        self.scheduled_time = scheduled_time or datetime.now()
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = "pending"
        self.result = None
        self.error = None

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.scheduled_time < other.scheduled_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "function": self.func.__name__ if hasattr(self.func, '__name__') else str(self.func),
            "priority": self.priority,
            "scheduled_time": self.scheduled_time.isoformat(),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "error": str(self.error) if self.error else None
        }


class TaskScheduler:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = PriorityQueue()
        self.active_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.failed_tasks: Dict[str, ScheduledTask] = {}
        self.futures: Dict[str, Future] = {}
        self.is_running = False
        self.scheduler_task = None

    def schedule_task(self, func: Callable, args: tuple = None, kwargs: dict = None,
                     priority: int = TaskPriority.NORMAL, delay_seconds: int = 0) -> str:
        task_id = str(uuid.uuid4())
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)

        task = ScheduledTask(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_time=scheduled_time
        )

        self.task_queue.put(task)
        logger.info(f"Scheduled task {task_id} with priority {priority}")

        return task_id

    def schedule_recurring_task(self, func: Callable, interval_seconds: int,
                              args: tuple = None, kwargs: dict = None,
                              priority: int = TaskPriority.NORMAL) -> str:
        task_id = str(uuid.uuid4())

        async def recurring_wrapper():
            while self.is_running:
                self.schedule_task(func, args, kwargs, priority)
                await asyncio.sleep(interval_seconds)

        asyncio.create_task(recurring_wrapper())
        logger.info(f"Scheduled recurring task {task_id} with interval {interval_seconds}s")

        return task_id

    async def start(self):
        if self.is_running:
            logger.warning("TaskScheduler is already running")
            return

        self.is_running = True
        self.scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("TaskScheduler started")

    async def stop(self):
        self.is_running = False

        if self.scheduler_task:
            await self.scheduler_task

        self.executor.shutdown(wait=True)
        logger.info("TaskScheduler stopped")

    async def _run_scheduler(self):
        while self.is_running:
            if not self.task_queue.empty():
                task = self.task_queue.get()

                if task.scheduled_time <= datetime.now():
                    if len(self.active_tasks) < self.max_workers:
                        await self._execute_task(task)
                    else:
                        self.task_queue.put(task)
                        await asyncio.sleep(0.1)
                else:
                    self.task_queue.put(task)
                    wait_time = (task.scheduled_time - datetime.now()).total_seconds()
                    await asyncio.sleep(min(wait_time, 1))
            else:
                await asyncio.sleep(0.5)

    async def _execute_task(self, task: ScheduledTask):
        task.status = "running"
        task.started_at = datetime.now()
        self.active_tasks[task.task_id] = task

        logger.info(f"Executing task {task.task_id}")

        try:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                self.executor,
                task.func,
                *task.args,
                **task.kwargs
            )
            self.futures[task.task_id] = future

            task.result = await future
            task.status = "completed"
            task.completed_at = datetime.now()

            self.completed_tasks[task.task_id] = task
            logger.info(f"Task {task.task_id} completed successfully")

        except Exception as e:
            task.status = "failed"
            task.error = e
            task.completed_at = datetime.now()

            self.failed_tasks[task.task_id] = task
            logger.error(f"Task {task.task_id} failed: {str(e)}")

        finally:
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            if task.task_id in self.futures:
                del self.futures[task.task_id]

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        elif task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        elif task_id in self.failed_tasks:
            return self.failed_tasks[task_id].to_dict()
        else:
            return None

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.futures:
            future = self.futures[task_id]
            cancelled = future.cancel()

            if cancelled:
                if task_id in self.active_tasks:
                    task = self.active_tasks[task_id]
                    task.status = "cancelled"
                    task.completed_at = datetime.now()
                    del self.active_tasks[task_id]

                logger.info(f"Task {task_id} cancelled")
                return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "max_workers": self.max_workers,
            "is_running": self.is_running
        }

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.active_tasks.values()]

    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        all_tasks = list(self.completed_tasks.values()) + list(self.failed_tasks.values())
        all_tasks.sort(key=lambda t: t.completed_at or t.created_at, reverse=True)
        return [task.to_dict() for task in all_tasks[:limit]]

    def clear_history(self):
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        logger.info("Task history cleared")