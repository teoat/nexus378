#!/usr/bin/env python3
Test Worker Status - Check if workers are actually processing

import sys
import time

import psutil

def test_worker_status():
    print("🔍 TESTING WORKER STATUS")
    print("=" * 50)

    # Find all collective worker processes
    worker_processes = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cwd"]):
        try:
            if proc.info["cmdline"] and "collective_worker_processor.py" in " ".join(
                proc.info["cmdline"]
            ):
                worker_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    print(f"📊 Found {len(worker_processes)} worker processes")

    if not worker_processes:
        print("❌ No worker processes found")
        return

    # Check each worker
    for i, proc in enumerate(worker_processes, 1):
        print(f"\n🔧 Worker {i}:")
        print(f"   PID: {proc.pid}")
        print(f"   Status: {proc.status()}")
        print(f"   CPU: {proc.cpu_percent()}%")
        print(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")

        try:
            print(f"   Working Directory: {proc.cwd()}")
        except:
            print(f"   Working Directory: Unable to determine")

        # Check if process is actually doing work
        try:
            cpu_times = proc.cpu_times()
            print(
                f"   CPU Time: {cpu_times.user:.2f}s user, {cpu_times.system:.2f}s system"
            )
        except:
            print(f"   CPU Time: Unable to determine")

    # Check TODO_MASTER.md
    print(f"\n📋 TODO_MASTER.md Status:")
    todo_path = Path(
        "/Users/Arief/Desktop/Nexus/nexus/TODO_MASTER.md"
    )
    if todo_path.exists():
        stat = todo_path.stat()
        print(f"   Path: {todo_path}")
        print(f"   Size: {stat.st_size} bytes")
        print(f"   Modified: {time.ctime(stat.st_mtime)}")
        print(f"   Last Modified: {time.time() - stat.st_mtime:.0f} seconds ago")
    else:
        print(f"   ❌ TODO_MASTER.md not found")

    # Test TODO reading
    print(f"\n🧪 Testing TODO Reading:")
    try:
        sys.path.insert(0, str(Path(__file__).parent))

        reader = TodoMasterReader()
        todos = reader.get_all_todos()
        pending = reader.get_pending_todos()

        print(f"   ✅ Total TODOs: {len(todos)}")
        print(f"   ✅ Pending TODOs: {len(pending)}")

        if pending:
            print(f"   📝 Sample pending TODO: {pending[0]['title'][:50]}...")

    except Exception as e:
        print(f"   ❌ Error reading TODOs: {e}")

if __name__ == "__main__":
    test_worker_status()
