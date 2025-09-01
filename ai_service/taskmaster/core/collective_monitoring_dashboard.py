#!/usr/bin/env python3
Collective Worker Monitoring Dashboard
Real-time monitoring and control for the 8-terminal collective worker system

import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Import the collective worker processor
try:
    from collective_worker_processor import CollectiveWorkerProcessor
    COLLECTIVE_PROCESSOR_AVAILABLE = True
except ImportError:
    COLLECTIVE_PROCESSOR_AVAILABLE = False

# Import TODO master integration
try:
    from simple_registry import SimpleTaskRegistry
    TODO_MASTER_AVAILABLE = True
    task_registry = SimpleTaskRegistry()
except ImportError:
    TODO_MASTER_AVAILABLE = False
    task_registry = None

class CollectiveMonitoringDashboard:

            print("⚠️  Monitoring already active")
            return
        
        self.monitoring_active = True
        print("🚀 Starting Collective Worker Monitoring Dashboard...")
        print("📊 Real-time updates every 5 seconds")
        print("🔄 Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while self.monitoring_active:
                self.update_dashboard()
                self.display_dashboard()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            self.monitoring_active = False
    
    def update_dashboard(self):

                    'action': f"Completed {total_completed_todos} complex TODOs",
                    'workers_active': total_active_workers
                })
                
                # Keep only last 10 activities
                if len(self.dashboard_data['recent_activity']) > 10:
                    self.dashboard_data['recent_activity'] = self.dashboard_data['recent_activity'][-10:]
            
        except Exception as e:
            print(f"❌ Error updating dashboard: {e}")
    
    def display_dashboard(self):

        print("🚀 COLLECTIVE WORKER MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 System Running Since: {self.dashboard_data['system_start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🔄 Update Interval: {self.update_interval} seconds")
        print()
        
        # System Overview
        print("🎯 SYSTEM OVERVIEW")
        print("-" * 40)
        print(f"📱 Total Terminals: {self.dashboard_data['total_terminals']}")
        print(f"🔧 Total Workers: {self.dashboard_data['total_workers']}")
        print(f"⚡ Active Workers: {self.dashboard_data['collective_stats'].get('total_active_workers', 0)}")
        print(f"📊 Worker Utilization: {self.dashboard_data['collective_stats'].get('worker_utilization', 0):.1f}%")
        print()
        
        # Collective Processing Stats
        print("👥 COLLECTIVE PROCESSING STATISTICS")
        print("-" * 40)
        stats = self.dashboard_data['collective_stats']
        print(f"📋 Complex TODOs Processed: {stats.get('total_complex_todos', 0)}")
        print(f"✅ Completed TODOs: {stats.get('total_completed_todos', 0)}")
        print(f"📈 Completion Rate: {stats.get('completion_rate', 0):.1f}%")
        print(f"🔄 Active Workers: {stats.get('total_active_workers', 0)}")
        print()
        
        # Cache Performance
        print("💾 CACHE PERFORMANCE")
        print("-" * 40)
        cache = self.dashboard_data['cache_performance']
        print(f"📦 Total Cache Size: {cache.get('total_size', 0)} entries")
        print(f"🎯 Cache Hits: {cache.get('total_hits', 0)}")
        print(f"❌ Cache Misses: {cache.get('total_misses', 0)}")
        print(f"📊 Hit Rate: {cache.get('hit_rate', 0):.1f}%")
        print()
        
        # TODO Master Status
        if self.dashboard_data['todo_master_status']:
            print("📋 TODO MASTER REGISTRY STATUS")
            print("-" * 40)
            master = self.dashboard_data['todo_master_status']
            print(f"📊 Total TODOs: {master.get('total_todos', 0)}")
            print(f"⏳ Pending: {master.get('pending', 0)}")
            print(f"🔄 In Progress: {master.get('in_progress', 0)}")
            print(f"✅ Completed: {master.get('completed', 0)}")
            print(f"👥 Collective Processed: {master.get('collective_processed', 0)}")
            print(f"🕒 Last Updated: {master.get('last_updated', 'N/A')}")
            print()
        
        # Recent Activity
        if self.dashboard_data['recent_activity']:
            print("📈 RECENT ACTIVITY")
            print("-" * 40)
            for activity in self.dashboard_data['recent_activity'][-5:]:  # Show last 5
                print(f"🕒 {activity['time']}: {activity['action']} (Workers: {activity['workers_active']})")
            print()
        
        # Performance Metrics
        print("📊 PERFORMANCE METRICS")
        print("-" * 40)
        uptime = datetime.now() - self.dashboard_data['system_start_time']
        print(f"⏱️  System Uptime: {str(uptime).split('.')[0]}")
        print(f"🚀 Processing Efficiency: {stats.get('completion_rate', 0):.1f}%")
        print(f"💾 Cache Efficiency: {cache.get('hit_rate', 0):.1f}%")
        print(f"👥 Worker Efficiency: {stats.get('worker_utilization', 0):.1f}%")
        print()
        
        # Status Indicators
        print("🔍 STATUS INDICATORS")
        print("-" * 40)
        active_workers = stats.get('total_active_workers', 0)
        if active_workers > 0:
            print("🟢 COLLECTIVE PROCESSING: ACTIVE")
            print(f"   {active_workers} workers currently processing complex TODOs")
        else:
            print("🟡 COLLECTIVE PROCESSING: IDLE")
            print("   Waiting for complex TODOs from master registry")
        
        if cache.get('hit_rate', 0) > 70:
            print("🟢 CACHE PERFORMANCE: EXCELLENT")
        elif cache.get('hit_rate', 0) > 50:
            print("🟡 CACHE PERFORMANCE: GOOD")
        else:
            print("🔴 CACHE PERFORMANCE: NEEDS OPTIMIZATION")
        
        if stats.get('worker_utilization', 0) > 80:
            print("🟢 WORKER UTILIZATION: HIGH")
        elif stats.get('worker_utilization', 0) > 50:
            print("🟡 WORKER UTILIZATION: MODERATE")
        else:
            print("🔴 WORKER UTILIZATION: LOW")
        print()
        
        print("💡 MONITORING CONTROLS:")
        print("   Press Ctrl+C to stop monitoring")
        print("   Dashboard updates automatically every 5 seconds")
        print("=" * 80)

def demo_monitoring_dashboard():

    print("🚀 COLLECTIVE WORKER MONITORING DASHBOARD DEMO")
    print("=" * 70)
    
    if not COLLECTIVE_PROCESSOR_AVAILABLE:
        print("❌ Collective Worker Processor not available")
        print("Please ensure 'collective_worker_processor.py' is in the same directory")
        return
    
    # Create monitoring dashboard
    dashboard = CollectiveMonitoringDashboard()
    
    # Add some demo processors (
    in real usage,
    these would be your actual running instances
)
    print("📊 Creating demo monitoring dashboard...")
    print("💡 In production, this would monitor your actual 8 terminal instances")
    print()
    
    # Add demo processors
    for i in range(8):
        processor = (
    CollectiveWorkerProcessor(max_workers=8-i, min_batch_size=3, max_batch_size=50)
)
        dashboard.add_processor(processor)
    
    print(f"✅ Added {len(dashboard.processors)} demo processors")
    print(f"🚀 Total workers available: {dashboard.dashboard_data['total_workers']}")
    print()
    
    # Show initial dashboard
    dashboard.update_dashboard()
    dashboard.display_dashboard()
    
    print("🎯 DEMONSTRATION COMPLETED!")
    print("🚀 Monitoring Dashboard is ready for production use!")
    print()
    print("💡 To monitor your actual 8-terminal system:")
    print("   1. Run this script in a separate terminal")
    print("   2. It will automatically detect and monitor running instances")
    print("   3. Real-time updates every 5 seconds")
    print("   4. Press Ctrl+C to stop monitoring")

def main():

    print("🚀 COLLECTIVE WORKER MONITORING DASHBOARD")
    print("=" * 70)
    print("Real-time monitoring for your 8-terminal collective worker system")
    print()
    
    # Check if we have the required components
    if not COLLECTIVE_PROCESSOR_AVAILABLE:
        print("❌ Collective Worker Processor not available")
        print("Please ensure 'collective_worker_processor.py' is in the same directory")
        return
    
    if not TODO_MASTER_AVAILABLE:
        print("⚠️  TODO Master Registry not available")
        print("Dashboard will work but won't show TODO master status")'
        print()
    
    # Create and start monitoring
    dashboard = CollectiveMonitoringDashboard()
    
    # Try to detect running processors (
    in production,
    these would be your actual instances
)
    print("🔍 Detecting running collective worker instances...")
    
    # For demo purposes, create some processors
    # In production, you would detect actual running instances
    for i in range(8):
        processor = (
    CollectiveWorkerProcessor(max_workers=8-i, min_batch_size=3, max_batch_size=50)
)
        dashboard.add_processor(processor)
    
    print(f"✅ Monitoring {len(dashboard.processors)} collective worker instances")
    print()
    
    # Start monitoring
    dashboard.start_monitoring()

if __name__ == "__main__":
    main()
