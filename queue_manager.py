#!/usr/bin/env python3


    """Enhanced queue manager for multi-source TODO processing
        logger.info(f"Enhanced Queue Manager initialized - Min: {self.min_todos}, Max: {self.max_todos}")

    def add_work_items(self, work_items: List[Dict[str, Any]]):
        """Add work items to the pending queue with enhanced categorization
                    logger.debug(f"Added work item: {enhanced_item.get('title', 'Unknown')} from {source}")
            
            # Sort queue by priority and source
            self._sort_pending_queue()
            
            logger.info(f"Added {len(work_items)} work items to queue. Total pending: {len(self.pending_queue)}")
            
        except Exception as e:
            logger.error(f"Error adding work items: {e}")

    def _enhance_work_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance work item with additional metadata
        enhanced['queue_id'] = f"Q_{len(self.pending_queue) + 1:04d}"
        enhanced['assigned_worker'] = None
        enhanced['processing_started'] = None
        enhanced['processing_completed'] = None
        enhanced['status'] = 'pending'
        
        # Calculate priority score for sorting
        priority_scores = {'high': 3, 'medium': 2, 'low': 1}
        enhanced['priority_score'] = priority_scores.get(enhanced.get('priority', 'medium'), 2)
        
        # Add source priority (TODO_MASTER.md gets higher priority)
        source_priority = {'TODO_MASTER': 2, 'MASTER_TODO': 1}
        enhanced['source_priority'] = source_priority.get(enhanced.get('source', ''), 0)
        
        return enhanced

    def _is_item_already_queued(self, item: Dict[str, Any]) -> bool:
        """Check if item is already in any queue
        """Sort pending queue by priority, source, and other factors
        """Determine if we should start processing more items
        """Get a batch of items to process
        logger.info(f"Prepared processing batch of {len(batch)} items")
        return batch

    def distribute_work_evenly(self, work_items: List[Dict[str, Any]], available_workers: List[str]):
        """Distribute work items evenly across available workers
                    logger.debug(f"Assigned {best_work.get('title', 'Unknown')} to {worker_id}")
            
            # Distribute remaining work to any available workers
            remaining_workers = [w for w in available_workers if w not in self.worker_assignments]
            for i, work_item in enumerate(work_items):
                if i < len(remaining_workers):
                    worker_id = remaining_workers[i]
                    self._assign_work_to_worker(worker_id, work_item)
                    logger.debug(f"Assigned remaining work {work_item.get('title', 'Unknown')} to {worker_id}")
            
            logger.info(f"Distributed {len(work_items)} work items across {len(available_workers)} workers")
            
        except Exception as e:
            logger.error(f"Error distributing work: {e}")

    def _group_work_by_specialization(self, work_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group work items by their extension/specialization
        """Find the best work item for a specific worker based on specialization
        """Assign a work item to a specific worker
            logger.error(f"Error assigning work to worker {worker_id}: {e}")

    def get_work_for_worker(self, worker_id: str, specializations: List[str]) -> Optional[Dict[str, Any]]:
        """Get work for a specific worker based on their specializations
            logger.error(f"Error getting work for worker {worker_id}: {e}")
            return None

    def _work_matches_specializations(self, work_item: Dict[str, Any], specializations: List[str]) -> bool:
        """Check if work item matches worker specializations
    def mark_work_completed(self, queue_id: str, success: bool = True, notes: str = ""):
        """Mark work item as completed
                logger.info(f"Marked work {queue_id} as {'completed' if success else 'failed'}")
                
        except Exception as e:
            logger.error(f"Error marking work completed: {e}")

    def _update_performance_metrics(self):
        """Update performance metrics
            logger.error(f"Error updating performance metrics: {e}")

    def get_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive queue status
            logger.error(f"Error getting queue status: {e}")
            return {}

    def clear_completed(self):
        """Clear completed and failed items to free memory
            logger.info(f"Cleared {cleared_count} completed/failed items")
            
        except Exception as e:
            logger.error(f"Error clearing completed items: {e}")

    def reset_queue(self):
        """Reset all queues (use with caution)
            logger.warning("All queues have been reset")
            
        except Exception as e:
            logger.error(f"Error resetting queues: {e}")

    def get_worker_performance(self) -> Dict[str, Any]:
        """Get worker performance statistics
        """Get intelligent queue management recommendations
                recommendations.append("📋 Pending queue is full - consider increasing worker capacity")
            elif status['pending_count'] < self.min_todos:
                recommendations.append("⏸️  Pending queue is low - consider adding more work items")
            
            # Processing efficiency recommendations
            if status['processing_count'] < self.max_processing * 0.5:
                recommendations.append("🔧 Low processing utilization - check worker availability")
            elif status['processing_count'] >= self.max_processing:
                recommendations.append("🚨 Processing queue at capacity - wait for completion")
            
            # Performance recommendations
            if status['failed_count'] > status['completed_count'] * 0.2:
                recommendations.append("⚠️  High failure rate - investigate worker issues")
            
            # Source balance recommendations
            source_dist = status.get('source_distribution', {})
            if len(source_dist) > 1:
                max_source = max(source_dist.values())
                min_source = min(source_dist.values())
                if max_source > min_source * 3:
                    recommendations.append("⚖️  Unbalanced source distribution - consider load balancing")
            
        except Exception as e:
            logger.error(f"Error generating queue recommendations: {e}")
            recommendations.append("⚠️  Error generating recommendations")
        
        return recommendations[:5]  # Return top 5 recommendations
