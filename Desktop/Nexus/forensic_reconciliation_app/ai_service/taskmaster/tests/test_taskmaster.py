import pytest
import asyncio
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, 'Desktop/Nexus/forensic_reconciliation_app/ai_service')
from taskmaster.core.taskmaster import Taskmaster, TaskmasterStatus
from taskmaster.models.job import JobType

@pytest.fixture
def temp_dir_with_todo():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        (tmpdir_path / "dummy_file.py").write_text("# TODO: Fix this")
        yield tmpdir

@pytest.mark.asyncio
async def test_taskmaster_initialization():
    taskmaster = Taskmaster()
    assert taskmaster is not None
    assert taskmaster.status == TaskmasterStatus.STOPPED

@pytest.mark.asyncio
async def test_taskmaster_start_stop():
    taskmaster = Taskmaster()
    await taskmaster.start()
    assert taskmaster.status == TaskmasterStatus.RUNNING
    await asyncio.sleep(0.1)
    await taskmaster.stop()
    assert taskmaster.status == TaskmasterStatus.STOPPED

@pytest.mark.asyncio
async def test_submit_todo_scanning_job(temp_dir_with_todo):
    taskmaster = Taskmaster()
    await taskmaster.start()
    job_id = await taskmaster.submit_todo_scanning_job(temp_dir_with_todo)
    assert job_id is not None
    await asyncio.sleep(0.2)
    assert len(taskmaster.active_jobs) == 2
    # Find the created job
    found_todo_job = False
    for job in taskmaster.active_jobs.values():
        if job.job_type == JobType.GENERAL_TODO:
            assert "Fix this" in job.data["content"]
            found_todo_job = True
    assert found_todo_job
    await taskmaster.stop()
