"""Loopuman API client."""

import os
import time
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

try:
    import requests
except ImportError:
    raise ImportError("Install requests: pip install requests")


BASE_URL = "https://api.loopuman.com/api/v1"


class TaskStatus(str, Enum):
    ACTIVE = "active"
    CLAIMED = "claimed"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    APPROVED = "approved"
    EXPIRED = "expired"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class TaskCategory(str, Enum):
    WRITING = "writing"
    RESEARCH = "research"
    DATA = "data"
    SURVEY = "survey"
    IMAGE = "image"
    LOCAL = "local"
    TRANSLATION = "translation"
    AUDIO = "audio"
    OTHER = "other"


@dataclass
class Task:
    """Represents a Loopuman task."""
    id: str
    status: str
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[int] = None
    result: Optional[str] = None
    submissions: Optional[List[Dict]] = None
    worker_id: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        # API returns task_id at top level, not nested under .task
        task_id = data.get("task_id", data.get("id", ""))
        submissions = data.get("submissions", [])
        # Extract result from first approved/pending submission
        result = None
        if submissions:
            result = submissions[0].get("content", submissions[0].get("text"))
        return cls(
            id=task_id,
            status=data.get("status", ""),
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            budget=data.get("budget_vae", data.get("budget")),
            result=result,
            submissions=submissions,
            worker_id=data.get("worker_id"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            raw=data,
        )

    @property
    def is_done(self) -> bool:
        return self.status in ("completed", "approved")

    @property
    def is_pending(self) -> bool:
        return self.status in ("active", "claimed", "submitted")

    @property
    def budget_usd(self) -> Optional[float]:
        """Budget converted to USD (100 VAE = $1.00)."""
        return self.budget / 100.0 if self.budget else None


class LoopumanError(Exception):
    """Base exception for Loopuman API errors."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}


class InsufficientBalanceError(LoopumanError):
    """Raised when account balance is too low."""
    pass


class TaskExpiredError(LoopumanError):
    """Raised when a task expires without being completed."""
    pass


class Loopuman:
    """
    Loopuman API client — route tasks to real humans.
    
    Usage:
        client = Loopuman()  # reads LOOPUMAN_API_KEY from env
        result = client.ask("Is this address real? 123 Main St, Nairobi")
        
        # Or with more control:
        task = client.create_task(
            title="Verify business",
            description="Call +254... and ask if they deliver",
            category="local",
            budget_vae=100,  # 100 VAE = $1.00
            estimated_seconds=300,  # ~5 min task
        )
        task = client.wait(task.id)
        print(task.result)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: int = 30,
    ):
        self.api_key = api_key or os.environ.get("LOOPUMAN_API_KEY")
        if not self.api_key:
            raise LoopumanError(
                "No API key. Set LOOPUMAN_API_KEY env var or pass api_key=. "
                "Register free at https://loopuman.com (promo code CLAW500 for $5 credit)."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        })

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an API request."""
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)
        resp = self._session.request(method, url, **kwargs)
        
        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError):
            data = {"raw": resp.text}

        if resp.status_code >= 400:
            error_msg = data.get("error", data.get("message", resp.text))
            if "insufficient_balance" in str(error_msg).lower() or "balance" in str(error_msg).lower():
                raise InsufficientBalanceError(
                    f"Balance too low. Top up at loopuman.com or deposit crypto. Error: {error_msg}",
                    status_code=resp.status_code,
                    response=data,
                )
            raise LoopumanError(
                f"API error {resp.status_code}: {error_msg}",
                status_code=resp.status_code,
                response=data,
            )
        return data

    # ── Core Methods ───────────────────────────────────────────

    def create_task(
        self,
        description: str,
        title: Optional[str] = None,
        category: str = "other",
        budget_vae: int = 50,
        estimated_seconds: int = 120,
        priority: str = "normal",
        max_workers: int = 1,
        **extra_fields,
    ) -> Task:
        """
        Create a task for a human worker.
        
        Args:
            description: What the human should do (be specific!)
            title: Short title (auto-generated from description if omitted)
            category: Task category — writing, research, data, survey, image, local, translation, audio, other
            budget_vae: Amount in VAE (100 VAE = $1.00 USD). Minimum 10.
            estimated_seconds: Expected time for worker to complete (required — enforces $6/hr min rate)
            priority: "normal" or "high" (high = workers see it first)
            max_workers: Number of workers 1-5 (use 2+ for competition mode)
            **extra_fields: Any additional fields your API supports
            
        Returns:
            Task object with id and status
        """
        payload = {
            "description": description,
            "category": category,
            "budget_vae": max(budget_vae, 10),
            "estimated_seconds": estimated_seconds,
            "priority": priority,
            "max_workers": max_workers,
            **extra_fields,
        }
        if title:
            payload["title"] = title

        data = self._request("POST", "/tasks", json=payload)
        return Task.from_dict(data.get("task", data))

    def create_task_sync(
        self,
        description: str,
        title: Optional[str] = None,
        category: str = "other",
        budget_vae: int = 50,
        estimated_seconds: int = 120,
        priority: str = "high",
        timeout: int = 300,
        **extra_fields,
    ) -> Task:
        """
        Create a task and block until a human responds.
        
        Timeout is 5 minutes. For longer tasks, use create_task() + wait().
        """
        payload = {
            "description": description,
            "category": category,
            "budget_vae": max(budget_vae, 10),
            "estimated_seconds": estimated_seconds,
            "priority": priority,
            **extra_fields,
        }
        if title:
            payload["title"] = title

        data = self._request("POST", "/tasks/sync", json=payload, timeout=timeout)
        return Task.from_dict(data.get("task", data))

    def get_task(self, task_id: str) -> Task:
        """Get current status and result of a task."""
        data = self._request("GET", f"/tasks/{task_id}")
        return Task.from_dict(data.get("task", data))

    def wait(
        self,
        task_id: str,
        poll_interval: int = 15,
        max_wait: int = 900,
    ) -> Task:
        """
        Poll a task until it's completed or times out.
        
        Args:
            task_id: The task ID to wait for
            poll_interval: Seconds between checks (default 15)
            max_wait: Maximum seconds to wait (default 900 = 15 min)
            
        Returns:
            Completed Task with result
        """
        elapsed = 0
        while elapsed < max_wait:
            task = self.get_task(task_id)
            if task.is_done:
                return task
            if task.status in ("expired", "cancelled", "disputed"):
                raise TaskExpiredError(
                    f"Task {task_id} ended with status: {task.status}",
                    response=task.raw,
                )
            time.sleep(poll_interval)
            elapsed += poll_interval

        task = self.get_task(task_id)
        return task  # return whatever state it's in

    def ask(
        self,
        question: str,
        category: str = "other",
        budget_vae: int = 50,
        estimated_seconds: int = 120,
        max_wait: int = 900,
    ) -> str:
        """
        Simplest interface: ask a human a question, get the answer.
        
        Args:
            question: What to ask (be specific)
            category: Task category
            budget_vae: VAE amount (100 = $1.00). Minimum 10.
            estimated_seconds: Expected time for worker (default 2 min)
            max_wait: Max seconds to wait (default 15 min)
            
        Returns:
            The human's response as a string
        """
        task = self.create_task(
            description=question,
            category=category,
            budget_vae=budget_vae,
            estimated_seconds=estimated_seconds,
            priority="high",
        )
        completed = self.wait(task.id, max_wait=max_wait)
        return completed.result or f"Task {completed.status} — no result yet."

    # ── Bulk Operations ────────────────────────────────────────

    def create_bulk_tasks(
        self,
        tasks: List[Dict[str, Any]],
        webhook_url: Optional[str] = None,
    ) -> dict:
        """
        Create up to 10,000 tasks at once.
        
        Args:
            tasks: List of task dicts with description, category, budget
            webhook_url: URL to receive results as they complete
            
        Returns:
            API response with batch_id and task_ids
        """
        payload = {"tasks": tasks}
        if webhook_url:
            payload["webhook_url"] = webhook_url
        return self._request("POST", "/tasks/bulk", json=payload)

    # ── Account ────────────────────────────────────────────────

    def balance(self) -> dict:
        """
        Check account balance.
        
        Returns:
            dict with balance in VAE and USD equivalent
        """
        data = self._request("GET", "/balance")
        # Add USD conversion for convenience
        if "balance" in data and "balance_usd" not in data:
            data["balance_usd"] = data["balance"] / 100.0
        return data

    # ── Class Methods ──────────────────────────────────────────

    @classmethod
    def register(
        cls,
        email: str,
        company_name: str = "Agent",
        promo_code: str = "CLAW500",
        base_url: str = BASE_URL,
    ) -> dict:
        """
        Register a new account (free, includes $5 credit with CLAW500).
        
        Returns:
            dict with api_key and balance
        """
        resp = requests.post(
            f"{base_url}/register",
            json={
                "email": email,
                "company_name": company_name,
                "promo_code": promo_code,
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code >= 400:
            raise LoopumanError(
                f"Registration failed: {data}",
                status_code=resp.status_code,
                response=data,
            )
        return data

    def __repr__(self):
        return f"Loopuman(base_url='{self.base_url}')"
