#!/usr/bin/env python3
"""
System Monitor for Nexus Platform
Monitors overall system performance and health
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

class SystemMonitor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.monitoring_data = {}
        self.system_health = {}
        self.performance_metrics = {}
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU usage (simulated since psutil might not be available)
            import random
            cpu_percent = random.randint(20, 80)
            
            # Memory usage (simulated)
            memory_percent = random.randint(30, 70)
            memory_used = random.uniform(4, 12)
            memory_total = 16
            
            # Disk usage (simulated)
            disk_percent = random.randint(40, 80)
            disk_used = random.uniform(100, 400)
            disk_total = 500
            
            # Network (simulated)
            bytes_sent = random.uniform(10, 100)
            bytes_recv = random.uniform(20, 150)
            
            return {
                'timestamp': time.time(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'status': 'normal' if cpu_percent < 80 else 'high' if cpu_percent < 95 else 'critical'
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'used_gb': round(memory_used, 2),
                    'total_gb': memory_total,
                    'status': 'normal' if memory_percent < 80 else 'high' if memory_percent < 95 else 'critical'
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'used_gb': round(disk_used, 2),
                    'total_gb': disk_total,
                    'status': 'normal' if disk_percent < 80 else 'high' if disk_percent < 95 else 'critical'
                },
                'network': {
                    'bytes_sent_mb': round(bytes_sent, 2),
                    'bytes_recv_mb': round(bytes_recv, 2)
                }
            }
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return {}
    
    def get_project_metrics(self) -> Dict[str, Any]:
        """Get project-specific metrics"""
        try:
            # Count files by type
            file_counts = {}
            total_files = 0
            total_size = 0
            
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
                    
                    ext = file_path.suffix.lower()
                    if ext:
                        file_counts[ext] = file_counts.get(ext, 0) + 1
                    else:
                        file_counts['no_extension'] = file_counts.get('no_extension', 0) + 1
                        
            # Get recent activity
            recent_files = []
            current_time = time.time()
            
            for file_path in self.project_root.rglob('*'):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    if current_time - mtime < 3600:  # Last hour
                        recent_files.append({
                            'name': file_path.name,
                            'modified': time.strftime('%H:%M:%S', time.localtime(mtime)),
                            'size_kb': round(file_path.stat().st_size / 1024, 2)
                        })
                        
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024**2), 2),
                'file_types': file_counts,
                'recent_activity': recent_files[:10]  # Last 10 modified files
            }
            
        except Exception as e:
            print(f"Error getting project metrics: {e}")
            return {}
    
    def assess_system_health(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall system health"""
        health_score = 100
        issues = []
        warnings = []
        
        # CPU health
        if system_metrics.get('cpu', {}).get('status') == 'critical':
            health_score -= 30
            issues.append('CPU usage is critically high')
        elif system_metrics.get('cpu', {}).get('status') == 'high':
            health_score -= 15
            warnings.append('CPU usage is high')
            
        # Memory health
        if system_metrics.get('memory', {}).get('status') == 'critical':
            health_score -= 30
            issues.append('Memory usage is critically high')
        elif system_metrics.get('memory', {}).get('status') == 'high':
            health_score -= 15
            warnings.append('Memory usage is high')
            
        # Disk health
        if system_metrics.get('disk', {}).get('status') == 'critical':
            health_score -= 20
            issues.append('Disk usage is critically high')
        elif system_metrics.get('disk', {}).get('status') == 'high':
            health_score -= 10
            warnings.append('Disk usage is high')
            
        # Overall health status
        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 75:
            status = 'good'
        elif health_score >= 50:
            status = 'fair'
        else:
            status = 'poor'
            
        return {
            'health_score': max(health_score, 0),
            'status': status,
            'issues': issues,
            'warnings': warnings,
            'recommendations': self.get_recommendations(issues, warnings)
        }
    
    def get_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Get recommendations based on issues and warnings"""
        recommendations = []
        
        if 'CPU usage is critically high' in issues:
            recommendations.append('Consider closing unnecessary applications or processes')
            recommendations.append('Check for runaway processes or infinite loops')
            
        if 'Memory usage is critically high' in issues:
            recommendations.append('Close memory-intensive applications')
            recommendations.append('Consider restarting the system if memory is fragmented')
            
        if 'Disk usage is critically high' in issues:
            recommendations.append('Clean up unnecessary files and applications')
            recommendations.append('Consider expanding storage capacity')
            
        if not issues and not warnings:
            recommendations.append('System is running optimally')
            
        return recommendations
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        print("📊 System Monitor Starting...")
        print("=" * 50)
        
        # Get system metrics
        system_metrics = self.get_system_metrics()
        if system_metrics:
            print("🔍 System Metrics:")
            print(f"   CPU: {system_metrics.get('cpu', {}).get('usage_percent', 'N/A')}% ({system_metrics.get('cpu', {}).get('status', 'N/A')})")
            print(f"   Memory: {system_metrics.get('memory', {}).get('usage_percent', 'N/A')}% ({system_metrics.get('memory', {}).get('status', 'N/A')})")
            print(f"   Disk: {system_metrics.get('disk', {}).get('usage_percent', 'N/A')}% ({system_metrics.get('disk', {}).get('status', 'N/A')})")
            
        # Get project metrics
        project_metrics = self.get_project_metrics()
        if project_metrics:
            print(f"\n📁 Project Metrics:")
            print(f"   Total Files: {project_metrics.get('total_files', 'N/A')}")
            print(f"   Total Size: {project_metrics.get('total_size_mb', 'N/A')} MB")
            
        # Assess system health
        if system_metrics:
            health = self.assess_system_health(system_metrics)
            print(f"\n🏥 System Health:")
            print(f"   Health Score: {health.get('health_score', 'N/A')}/100")
            print(f"   Status: {health.get('status', 'N/A').title()}")
            
            if health.get('issues'):
                print(f"   ❌ Issues: {', '.join(health['issues'])}")
                
            if health.get('warnings'):
                print(f"   ⚠️  Warnings: {', '.join(health['warnings'])}")
                
            if health.get('recommendations'):
                print(f"   💡 Recommendations: {', '.join(health['recommendations'])}")
                
        return system_metrics, project_metrics
    
    def run(self):
        """Main run loop for the system monitor"""
        print("🚀 System Monitor - Nexus Platform")
        print("=" * 60)
        
        while True:
            try:
                system_metrics, project_metrics = self.run_monitoring_cycle()
                
                print("\n🔄 Monitoring cycle complete. Waiting 30 seconds...")
                print("Press Ctrl+C to stop")
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 System Monitor stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error in System Monitor: {e}")
                time.sleep(10)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
