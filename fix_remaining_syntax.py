#!/usr/bin/env python3


    """Fix malformed docstrings in a file.
            if (line.strip().startswith('
                not line.strip().endswith('
                not lines[i + 1].strip().startswith('
            if line.strip().startswith('"""') and line.strip().endswith('
            elif line.strip().startswith('"""') and not line.strip().endswith('
                    if next_line.startswith('
                        line = line + '
                    line = line + '
        content = re.sub(r'class (\w+):\s*"""([^"]+)"""', r'class \1:\n    """\2
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix remaining syntax issues.
    print("🔧 Fixing remaining syntax issues...")
    
    # Files with known syntax issues
    problem_files = [
        "nexus/ai_service/agents/circular_transaction_detector.py",
        "nexus/ai_service/agents/ai_fuzzy_matcher.py",
        "nexus/ai_service/agents/compliance_rule_engine_fixed.py",
        "nexus/ai_service/agents/evidence_processor_fixed.py",
        "nexus/ai_service/agents/entity_network_analyzer.py",
        "nexus/ai_service/agents/explainable_ai.py",
        "nexus/ai_service/agents/fraud_agent_entity_network.py",
        "nexus/ai_service/agents/fraud_agent_pattern_detection.py",
        "nexus/ai_service/agents/ocr_processor.py",
        "nexus/ai_service/agents/outlier_detector.py",
        "nexus/ai_service/agents/pattern_detector.py",
        "nexus/ai_service/agents/reconciliation_agent.py",
        "nexus/ai_service/agents/risk_scorer.py",
        "nexus/ai_service/agents/reconciliation_agent_fuzzy_matching.py",
        "nexus/ai_service/agents/run_enhanced_todo.py",
        "nexus/ai_service/agents/run_todo_automation.py",
        "nexus/ai_service/agents/todo_automation_backup.py",
        "nexus/ai_service/agents/todo_automation_enhanced.py",
        "nexus/ai_service/agents/todo_cli.py",
        "nexus/ai_service/agents/todo_config.py",
        "nexus/ai_service/auth/encryption_service.py",
        "nexus/ai_service/auth/mfa/hardware_auth.py",
        "nexus/ai_service/auth/mfa/mfa_implementation.py",
        "nexus/ai_service/auth/mfa/mfa_manager.py",
        "nexus/ai_service/auth/mfa/sms_auth.py",
        "nexus/ai_service/auth/mfa/test_mfa_implementation.py",
        "nexus/ai_service/auth/mfa/test_mfa_system.py",
        "nexus/ai_service/auth/mfa/totp_auth.py",
        "nexus/ai_service/auth/mfa/mfa_mcp_server.py",
        "nexus/ai_service/core_agents/reconciliation_agent.py",
        "nexus/ai_service/core_agents/test_reconciliation_agent.py",
        "nexus/ai_service/orchestration/message_queue_system.py",
        "nexus/ai_service/main.py",
        "nexus/ai_service/plugins/example_plugin.py",
        "nexus/ai_service/plugins/plugin_manager.py",
        "nexus/ai_service/plugins/test_plugin_manager.py",
        "nexus/ai_service/security/encryption.py",
        "nexus/ai_service/security/key_management.py",
        "nexus/ai_service/security/encryption_core.py",
        "nexus/ai_service/taskmaster/core/9_tab_monitoring_dashboard.py",
        "nexus/ai_service/taskmaster/core/check_todo_master_integration.py",
        "nexus/ai_service/taskmaster/core/check_worker_status.py",
        "nexus/ai_service/taskmaster/core/cleanup_and_sync.py",
        "nexus/ai_service/taskmaster/core/collective_monitoring_dashboard.py",
        "nexus/ai_service/taskmaster/core/collective_worker_processor.py",
        "nexus/ai_service/taskmaster/core/dynamic_collaborative_system.py",
        "nexus/ai_service/taskmaster/core/final_working_system.py",
        "nexus/ai_service/taskmaster/core/fix_worker_processing.py",
        "nexus/ai_service/taskmaster/core/fixed_production_system.py",
        "nexus/ai_service/taskmaster/core/launch_11_tab_system.py",
        "nexus/ai_service/taskmaster/core/launch_macos_12_tabs_enhanced.py",
        "nexus/ai_service/taskmaster/core/launch_macos_9_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_manual_12_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_proper_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_active_workers.py",
        "nexus/ai_service/taskmaster/core/launch_reliable_12_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_reliable_36_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_simple_12_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_single_window_12_tabs.py",
        "nexus/ai_service/taskmaster/core/launch_simple_9_workers.py",
        "nexus/ai_service/taskmaster/core/load_balancing.py",
        "nexus/ai_service/taskmaster/core/mcp_server_orchestrator.py",
        "nexus/ai_service/taskmaster/core/monitor_collective_system.py",
        "nexus/ai_service/taskmaster/core/enhanced_collaborative_system.py",
        "nexus/ai_service/taskmaster/core/queue_manager.py",
        "nexus/ai_service/taskmaster/core/quick_test.py",
        "nexus/ai_service/taskmaster/core/reconfigured_system.py",
        "nexus/ai_service/taskmaster/core/production_task_system.py",
        "nexus/ai_service/taskmaster/core/resource_monitor.py",
        "nexus/ai_service/taskmaster/core/show_mcp_status.py",
        "nexus/ai_service/taskmaster/core/simple_9_terminal_launcher.py",
        "nexus/ai_service/taskmaster/core/simple_reconfigured_system.py",
        "nexus/ai_service/taskmaster/core/start_production.py",
        "nexus/ai_service/taskmaster/core/start_working_system.py",
        "nexus/ai_service/taskmaster/core/status_monitor.py",
        "nexus/ai_service/taskmaster/core/synchronized_production_system.py",
        "nexus/ai_service/taskmaster/core/system_optimizer.py",
        "nexus/ai_service/taskmaster/core/task_breakdown_engine.py",
        "nexus/ai_service/taskmaster/core/task_router.py",
        "nexus/ai_service/taskmaster/core/taskmaster.py",
        "nexus/ai_service/taskmaster/core/test_all_implementations.py",
        "nexus/ai_service/taskmaster/core/test_autoscaler.py",
        "nexus/ai_service/taskmaster/core/test_dynamic_system.py",
        "nexus/ai_service/taskmaster/core/test_integration.py",
        "nexus/ai_service/taskmaster/core/system_integration_api.py",
        "nexus/ai_service/taskmaster/core/test_todo_parsing.py",
        "nexus/ai_service/taskmaster/core/test_system.py",
        "nexus/ai_service/taskmaster/core/test_worker_status.py",
        "nexus/ai_service/taskmaster/core/todo_master_reader.py",
        "nexus/ai_service/taskmaster/core/todo_status.py",
        "nexus/ai_service/taskmaster/core/todo_processing_engine.py",
        "nexus/ai_service/taskmaster/core/working_production_system.py",
        "nexus/ai_service/taskmaster/core/test_duckdb_setup.py",
        "nexus/ai_service/taskmaster/examples/basic_usage.py",
        "nexus/ai_service/taskmaster/examples/check_todo_status.py",
        "nexus/ai_service/taskmaster/examples/mcp_demo.py",
        "nexus/ai_service/taskmaster/examples/status_monitor.py",
        "nexus/ai_service/taskmaster/examples/task_breakdown_analysis.py",
        "nexus/ai_service/taskmaster/examples/update_unimplemented_todos.py",
        "nexus/ai_service/taskmaster/examples/verify_mcp_status.py",
        "nexus/ai_service/taskmaster/examples/workspace_sync.py",
        "nexus/ai_service/taskmaster/models/job.py",
        "nexus/gateway/auth/mfa_auth.py",
        "nexus/gateway/auth/sms_service.py",
        "nexus/gateway/auth/totp_service.py",
        "nexus/gateway/auth/jwt_auth.py",
        "nexus/frontend/dashboard_framework.py",
        "nexus/infrastructure/load_balancer/round_robin_lb.py",
        "nexus/infrastructure/queue_monitoring/alert_system.py",
        "nexus/infrastructure/queue_monitoring/performance_dashboard.py",
        "nexus/infrastructure/queue_monitoring/queue_metrics.py",
        "nexus/api_gateway/core/gateway.py",
        "nexus/test_all_components.py",
        "nexus/smart_todo_automation.py",
        "nexus/gateway/api_gateway.py",
        "nexus/api_gateway/middleware/rate_limiter.py",
        "nexus/api_gateway/node_modules/flatted/python/flatted.py",
        "nexus/auto_todo_detector.py",
        "nexus/consolidate_markdown.py",
        "nexus/enhanced_todo_automation.py"
    ]
    
    fixed_count = 0
    for file_path in problem_files:
        path = Path(file_path)
        if path.exists():
            print(f"   Fixing: {file_path}")
            if fix_docstring_syntax(path):
                fixed_count += 1
                print(f"     ✅ Fixed: {file_path}")
            else:
                print(f"     ⚠️  No changes needed: {file_path}")
        else:
            print(f"     ❌ File not found: {file_path}")
    
    print(f"\n📊 Fixed {fixed_count} files")
    print("✅ Syntax fixes completed. Now run Black formatting again.")

if __name__ == "__main__":
    main()
