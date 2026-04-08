"""
OrcheFlowAI — Unit Tests: Calendar Manager (free slot algorithm)
Tests gap detection logic without DB dependency.
"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, patch, MagicMock


class TestFindFreeSlots:
    @pytest.mark.asyncio
    async def test_gaps_detected_between_meetings(self):
        """Should find gap between 10:00-11:00 when meetings are 09:00-10:00 and 11:00-12:00."""
        from mcp_server.tools.calendar_manager import find_free_slots

        mock_db = AsyncMock()
        today = date.today().isoformat()

        mock_events = {
            "date": today,
            "events": [
                {"start": f"{today}T09:00:00", "end": f"{today}T10:00:00", "title": "Standup"},
                {"start": f"{today}T11:00:00", "end": f"{today}T12:00:00", "title": "Client Call"},
            ]
        }

        with patch("mcp_server.tools.calendar_manager.list_events", new=AsyncMock(return_value=mock_events)):
            result = await find_free_slots(date=today, min_duration_minutes=30, db=mock_db)

        gaps = result["gaps"]
        assert len(gaps) >= 1
        # Gap between 10:00 and 11:00 = 60 minutes
        morning_gap = next((g for g in gaps if "T10:00:00" in g["start"]), None)
        assert morning_gap is not None
        assert morning_gap["duration_minutes"] == 60

    @pytest.mark.asyncio
    async def test_no_gaps_when_fully_booked(self):
        """Should return 0 gaps when calendar is fully booked 09:00-18:00."""
        from mcp_server.tools.calendar_manager import find_free_slots

        mock_db = AsyncMock()
        today = date.today().isoformat()
        mock_events = {
            "date": today,
            "events": [{"start": f"{today}T09:00:00", "end": f"{today}T18:00:00", "title": "All day"}]
        }

        with patch("mcp_server.tools.calendar_manager.list_events", new=AsyncMock(return_value=mock_events)):
            result = await find_free_slots(date=today, min_duration_minutes=90, db=mock_db)

        assert result["gaps"] == []

    @pytest.mark.asyncio
    async def test_full_day_free_when_no_events(self):
        """Should return entire workday as gap when no events."""
        from mcp_server.tools.calendar_manager import find_free_slots

        mock_db = AsyncMock()
        today = date.today().isoformat()
        mock_events = {"date": today, "events": []}

        with patch("mcp_server.tools.calendar_manager.list_events", new=AsyncMock(return_value=mock_events)):
            result = await find_free_slots(
                date=today, min_duration_minutes=90,
                work_start_hour=9, work_end_hour=18, db=mock_db
            )

        gaps = result["gaps"]
        assert len(gaps) == 1
        assert gaps[0]["duration_minutes"] == 540  # 9 hours = 540 mins
