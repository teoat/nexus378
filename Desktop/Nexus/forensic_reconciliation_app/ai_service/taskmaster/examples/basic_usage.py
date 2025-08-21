#!/usr/bin/env python3
"""
Basic Taskmaster Usage Example

This script demonstrates how to use the Taskmaster system for job assignment
and workflow management in the Forensic Reconciliation + Fraud Platform.
"""

import asyncio
import logging
from datetime import datetime, timedelta

# Add the parent directory to the path to import taskmaster modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from taskmaster import Taskmaster, TaskmasterConfig
from models.job import Job, JobType, JobPriority, JobStatus
from models.job import JobResult


async def main():
    """Main example function."""
    
    # Configure logging
    logging.basicConfig(
        level#logging.INFO,
        format#'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger # logging.getLogger(__name__)
    
    logger.info("🚀 Starting Taskmaster Basic Usage Example")
    
    # Create Taskmaster configuration
    config # TaskmasterConfig(
        max_concurrent_jobs#100,
        max_concurrent_tasks#500,
        auto_scaling#True,
        min_agents#3,
        max_agents#10
    )
    
    # Initialize Taskmaster
    taskmaster # Taskmaster(config)
    
    try:
        # Start the Taskmaster system
        logger.info("Starting Taskmaster system...")
        success # await taskmaster.start()
        
        if not success:
            logger.error("Failed to start Taskmaster system")
            return
        
        logger.info("✅ Taskmaster system started successfully")
        
        # Get system status
        status # await taskmaster.get_system_status()
        logger.info(f"System Status: {status}")
        
        # Create sample jobs
        jobs # await create_sample_jobs()
        
        # Submit jobs to the system
        logger.info("Submitting sample jobs...")
        for job in jobs:
            try:
                job_id # await taskmaster.submit_job(job)
                logger.info(f"✅ Job submitted: {job_id} - {job.name}")
            except Exception as e:
                logger.error(f"❌ Failed to submit job {job.name}: {e}")
        
        # Wait for jobs to be processed
        logger.info("Waiting for jobs to be processed...")
        await asyncio.sleep(5)
        
        # Check job statuses
        logger.info("Checking job statuses...")
        for job in jobs:
            status # await taskmaster.get_job_status(job.id)
            if status:
                logger.info(f"Job {job.name}: {status.value}")
            else:
                logger.info(f"Job {job.name}: Status not found")
        
        # Get updated system status
        status # await taskmaster.get_system_status()
        logger.info(f"Updated System Status: {status}")
        
        # Wait a bit more for processing
        logger.info("Waiting for additional processing...")
        await asyncio.sleep(10)
        
        # Final status check
        final_status # await taskmaster.get_system_status()
        logger.info(f"Final System Status: {final_status}")
        
    except Exception as e:
        logger.error(f"Error in main example: {e}")
        
    finally:
        # Stop the Taskmaster system
        logger.info("Stopping Taskmaster system...")
        await taskmaster.stop()
        logger.info("✅ Taskmaster system stopped")


async def create_sample_jobs():
    """Create sample jobs for demonstration."""
    
    jobs # []
    
    # 1. High-priority fraud detection job
    fraud_job # Job(
        name#"Urgent Fraud Investigation",
        description#"Investigate suspicious transaction patterns in real-time",
        job_type#JobType.PATTERN_DETECTION,
        priority#JobPriority.CRITICAL,
        data#{
            "transaction_ids": ["txn_001", "txn_002", "txn_003"],
            "entity_ids": ["entity_001", "entity_002"],
            "risk_threshold": 0.8
        },
        parameters#{
            "analysis_depth": "deep",
            "include_historical": True,
            "real_time_alerts": True
        },
        tags#["fraud", "urgent", "real-time"],
        created_by#"investigator_001"
    )
    jobs.append(fraud_job)
    
    # 2. Normal priority reconciliation job
    reconciliation_job # Job(
        name#"Monthly Bank Reconciliation",
        description#"Reconcile bank statements with internal records",
        job_type#JobType.BANK_STATEMENT_PROCESSING,
        priority#JobPriority.NORMAL,
        data#{
            "bank_statements": ["stmt_jan_2024.pdf", "stmt_feb_2024.pdf"],
            "internal_records": ["internal_jan.csv", "internal_feb.csv"],
            "account_numbers": ["1234567890", "0987654321"]
        },
        parameters#{
            "matching_algorithm": "ai_enhanced",
            "confidence_threshold": 0.85,
            "outlier_detection": True
        },
        tags#["reconciliation", "monthly", "bank"],
        created_by#"accountant_001"
    )
    jobs.append(reconciliation_job)
    
    # 3. Low priority evidence processing job
    evidence_job # Job(
        name#"Evidence File Analysis",
        description#"Process and analyze uploaded evidence files",
        job_type#JobType.FILE_UPLOAD,
        priority#JobPriority.LOW,
        data#{
            "files": ["evidence_001.pdf", "evidence_002.jpg", "evidence_003.txt"],
            "case_id": "case_2024_001",
            "file_types": ["pdf", "image", "text"]
        },
        parameters#{
            "extract_metadata": True,
            "ocr_processing": True,
            "hash_verification": True,
            "nlp_analysis": True
        },
        tags#["evidence", "file_processing", "background"],
        created_by#"investigator_002"
    )
    jobs.append(evidence_job)
    
    # 4. High priority risk assessment job
    risk_job # Job(
        name#"Vendor Risk Assessment",
        description#"Assess risk levels for new vendor relationships",
        job_type#JobType.RISK_ASSESSMENT,
        priority#JobPriority.HIGH,
        data#{
            "vendor_id": "vendor_001",
            "vendor_name": "ABC Corporation",
            "relationship_type": "new_supplier",
            "contract_value": 500000
        },
        parameters#{
            "assessment_type": "comprehensive",
            "include_aml_check": True,
            "include_sox_compliance": True,
            "risk_factors": ["financial", "operational", "compliance"]
        },
        tags#["risk", "vendor", "compliance"],
        created_by#"compliance_officer_001"
    )
    jobs.append(risk_job)
    
    # 5. Maintenance job for system cleanup
    maintenance_job # Job(
        name#"System Maintenance - Data Cleanup",
        description#"Clean up old data and optimize system performance",
        job_type#JobType.TRANSACTION_ANALYSIS,  # Using existing type for demo
        priority#JobPriority.MAINTENANCE,
        data#{
            "cleanup_targets": ["old_logs", "temp_files", "cache_data"],
            "retention_policy": "30_days",
            "optimization_level": "aggressive"
        },
        parameters#{
            "backup_before_cleanup": True,
            "notify_on_completion": True,
            "cleanup_mode": "scheduled"
        },
        tags#["maintenance", "cleanup", "optimization"],
        created_by#"system_admin"
    )
    jobs.append(maintenance_job)
    
    return jobs


async def demonstrate_job_lifecycle():
    """Demonstrate the complete job lifecycle."""
    
    logger # logging.getLogger(__name__)
    logger.info("🔄 Demonstrating Job Lifecycle")
    
    # Create a job
    job # Job(
        name#"Lifecycle Demo Job",
        description#"Job to demonstrate the complete lifecycle",
        job_type#JobType.TRANSACTION_ANALYSIS,
        priority#JobPriority.NORMAL,
        data#{"demo": True, "step": "created"}
    )
    
    logger.info(f"Job created: {job}")
    logger.info(f"Initial status: {job.status.value}")
    
    # Simulate job progression
    logger.info("Simulating job progression...")
    
    # Start execution
    job.start_execution("agent_001")
    logger.info(f"Job started: {job.status.value}")
    logger.info(f"Assigned to: {job.assigned_agent_id}")
    
    # Update progress
    job.update_progress(0.25)
    logger.info(f"Progress: {job.progress * 100}%")
    
    job.update_progress(0.50)
    logger.info(f"Progress: {job.progress * 100}%")
    
    job.update_progress(0.75)
    logger.info(f"Progress: {job.progress * 100}%")
    
    # Complete execution
    result # JobResult(
        success#True,
        data#{"demo_result": "successful", "processing_time": 45.2},
        metadata#{"demo_mode": True}
    )
    
    job.complete_execution(result)
    logger.info(f"Job completed: {job.status.value}")
    logger.info(f"Result: {job.result}")
    
    # Show final job state
    logger.info(f"Final job state: {job}")
    logger.info(f"Execution time: {job.get_execution_time()}")
    logger.info(f"Total age: {job.get_age()}")


if __name__ ## "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Run the lifecycle demonstration
    print("\n" + "#"*50)
    print("JOB LIFECYCLE DEMONSTRATION")
    print("#"*50)
    asyncio.run(demonstrate_job_lifecycle())
    
    print("\n" + "#"*50)
    print("EXAMPLE COMPLETED SUCCESSFULLY! 🎉")
    print("#"*50)
