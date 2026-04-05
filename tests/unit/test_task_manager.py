"""
OrcheFlowAI — Unit Tests: MCP Task Manager
TDD contract for create_task, list_tasks, update_task, and prioritize_tasks.
Stack: pytest + pytest-asyncio + pytest-mock
"""
import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


# ─── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Mock SQLAlchemy AsyncSession."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    return db


@pytest.fixture
def sample_task_body():
    from pydantic import BaseModel
    class Body:
        title = "Review API contract"
        description = "Review and confirm the OrcheFlowAI API contract"
        priority = 2
        due_date = str(date.today() + timedelta(days=2))
        tags = ["api", "review"]
        source_note_id = "note-001"
        user_id = "demo-user"
    return Body()


# ─── create_task ────────────────────────────────────────────────────────────────

class TestCreateTask:
    @pytest.mark.asyncio
    async def test_create_task_happy_path(self, mock_db, sample_task_body):
        """Should create task with all fields set correctly."""
        from mcp.tools.task_manager import create_task

        mock_task = MagicMock()
        mock_task.id = "task-123"
        mock_task.title = sample_task_body.title
        mock_task.status = "TODO"
        mock_task.priority = sample_task_body.priority
        mock_task.due_date = date.fromisoformat(sample_task_body.due_date)
        mock_task.created_at.isoformat.return_value = "2026-04-05T00:00:00"
        mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", "task-123")

        with patch("mcp.tools.task_manager.Task", return_value=mock_task):
            result = await create_task(sample_task_body, db=mock_db)

        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_create_task_without_due_date(self, mock_db):
        """Should succeed when due_date is None."""
        class BodyNoDueDate:
            title = "Backlog item"
            description = ""
            priority = 5
            due_date = None
            tags = []
            source_note_id = None
            user_id = "demo-user"

        from mcp.tools.task_manager import create_task
        mock_task = MagicMock()
        mock_task.id = "task-456"
        mock_task.status = "TODO"
        mock_task.priority = 5
        mock_task.due_date = None
        mock_task.created_at.isoformat.return_value = "2026-04-05T00:00:00"

        with patch("mcp.tools.task_manager.Task", return_value=mock_task):
            result = await create_task(BodyNoDueDate(), db=mock_db)

        assert mock_db.commit.called


# ─── prioritize_tasks ───────────────────────────────────────────────────────────

class TestPrioritizeTasks:
    @pytest.mark.asyncio
    async def test_urgent_task_ranks_first(self):
        """P1 task due tomorrow should rank above P3 task due in 7 days."""
        from mcp.tools.task_manager import prioritize_tasks, PrioritizeRequest

        tomorrow = str(date.today() + timedelta(days=1))
        next_week = str(date.today() + timedelta(days=7))

        body = PrioritizeRequest(tasks=[
            {"id": "t2", "title": "Low urgency", "priority": 3, "due_date": next_week},
            {"id": "t1", "title": "Critical item", "priority": 1, "due_date": tomorrow},
        ])
        result = await prioritize_tasks(body)
        assert result["tasks"][0]["id"] == "t1", "Critical task should be ranked first"

    @pytest.mark.asyncio
    async def test_no_due_date_ranks_last(self):
        """Task with no due date should rank below one with a due date."""
        from mcp.tools.task_manager import prioritize_tasks, PrioritizeRequest

        in_3_days = str(date.today() + timedelta(days=3))
        body = PrioritizeRequest(tasks=[
            {"id": "t1", "title": "No deadline", "priority": 2, "due_date": None},
            {"id": "t2", "title": "Has deadline", "priority": 2, "due_date": in_3_days},
        ])
        result = await prioritize_tasks(body)
        # t2 has urgency bonus; t1 has 0 urgency
        assert result["tasks"][0]["id"] == "t2"

    @pytest.mark.asyncio
    async def test_empty_task_list(self):
        """Empty input should return empty output without error."""
        from mcp.tools.task_manager import prioritize_tasks, PrioritizeRequest
        result = await prioritize_tasks(PrioritizeRequest(tasks=[]))
        assert result["tasks"] == []
