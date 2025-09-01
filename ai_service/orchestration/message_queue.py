Message Queue System - Priority-based Messaging and Routing

This module implements the MessageQueue class that provides
comprehensive message queuing capabilities for the forensic platform.

import asyncio
import json
import logging
import pickle
import time
import uuid
from datetime import datetime, timedelta

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType

class MessagePriority(Enum):
    """Message priority levels."""

    CRITICAL = 0  # Highest priority - immediate processing
    HIGH = 1  # High priority - process soon
    NORMAL = 2  # Normal priority - standard processing
    LOW = 3  # Low priority - process when resources available
    BULK = 4  # Bulk processing - lowest priority

class MessageType(Enum):
    """Types of messages."""

    TASK = "task"  # Task execution message
    NOTIFICATION = "notification"  # System notification
    EVENT = "event"  # System event
    COMMAND = "command"  # Control command
    DATA = "data"  # Data transfer
    STATUS = "status"  # Status update
    ERROR = "error"  # Error message
    HEARTBEAT = "heartbeat"  # Health check

class MessageStatus(Enum):
    """Message processing status."""

    PENDING = "pending"  # Waiting to be processed
    PROCESSING = "processing"  # Currently being processed
    COMPLETED = "completed"  # Successfully processed
    FAILED = "failed"  # Processing failed
    RETRY = "retry"  # Scheduled for retry
    CANCELLED = "cancelled"  # Cancelled
    EXPIRED = "expired"  # Expired

class QueueType(Enum):
    """Types of message queues."""

    PRIORITY = "priority"  # Priority-based queue
    FIFO = "fifo"  # First-in-first-out
    LIFO = "lifo"  # Last-in-first-out
    ROUND_ROBIN = "round_robin"  # Round-robin distribution
    WEIGHTED = "weighted"  # Weighted distribution

@dataclass
class Message:
    """A message in the queue."""

    message_id: str
    message_type: MessageType
    priority: MessagePriority
    sender_id: str
    recipient_id: str
    payload: Any
    timestamp: datetime
    expiration: Optional[datetime]
    retry_count: int = 0
    max_retries: int = 3
    status: MessageStatus = MessageStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueConfig:
    """Configuration for a message queue."""

    queue_id: str
    queue_name: str
    queue_type: QueueType
    max_size: int
    max_message_size: int
    retention_period: int  # seconds
    enable_priority: bool
    enable_persistence: bool
    enable_monitoring: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueMetrics:
    """Metrics for a message queue."""

    total_messages: int
    pending_messages: int
    processing_messages: int
    completed_messages: int
    failed_messages: int
    average_processing_time: float
    queue_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MessageHandler:
    """Handler for processing messages."""

    handler_id: str
    handler_name: str
    message_types: List[MessageType]
    priority_levels: List[MessagePriority]
    handler_function: Callable
    is_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

class MessageQueue:

    Comprehensive message queue system.

    The MessageQueue is responsible for:
    - Managing priority-based message queues
    - Routing messages to appropriate handlers
    - Implementing various queue types and algorithms
    - Providing message persistence and recovery
    - Monitoring queue performance and health

    def __init__(self, config: Dict[str, Any]):
        """Initialize the MessageQueue."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_queue_size = config.get("default_queue_size", 10000)
        self.default_message_size = config.get(
            "default_message_size", 1024 * 1024
        )  # 1MB
        self.default_retention_period = config.get(
            "default_retention_period", 3600
        )  # 1 hour
        self.enable_persistence = config.get("enable_persistence", True)
        self.persistence_path = config.get("persistence_path", "./message_queue_data")

        # Message queues
        self.queues: Dict[str, deque] = {}
        self.queue_configs: Dict[str, QueueConfig] = {}
        self.queue_metrics: Dict[str, QueueMetrics] = {}

        # Message handlers
        self.message_handlers: Dict[str, MessageHandler] = {}
        self.handler_index: Dict[MessageType, List[str]] = defaultdict(list)

        # Message tracking
        self.messages: Dict[str, Message] = {}
        self.message_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Performance tracking
        self.total_messages_processed = 0
        self.total_messages_failed = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Background tasks
        self.cleanup_task = None
        self.monitoring_task = None
        self.persistence_task = None

        # Initialize message queue components
        self._initialize_message_queue_components()

        self.logger.info("MessageQueue initialized successfully")

    async def start(self):
        """Start the MessageQueue."""
        self.logger.info("Starting MessageQueue...")

        # Initialize message queue components
        await self._initialize_message_queue_components()

        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
        self.monitoring_task = asyncio.create_task(self._monitor_queue_health())
        if self.enable_persistence:
            self.persistence_task = asyncio.create_task(self._persist_queue_data())

        self.logger.info("MessageQueue started successfully")

    async def stop(self):
        """Stop the MessageQueue."""
        self.logger.info("Stopping MessageQueue...")

        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.persistence_task:
            self.persistence_task.cancel()

        # Persist final state
        if self.enable_persistence:
            await self._persist_queue_data()

        self.logger.info("MessageQueue stopped")

    def _initialize_message_queue_components(self):
        """Initialize message queue components."""
        try:
            # Initialize default queues
            self._initialize_default_queues()

            # Initialize default handlers
            self._initialize_default_handlers()

            self.logger.info("Message queue components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing message queue components: {e}")

    def _initialize_default_queues(self):
        """Initialize default message queues."""
        try:
            # Priority queue for high-priority messages
            priority_queue_config = QueueConfig(
                queue_id="priority_queue",
                queue_name="Priority Message Queue",
                queue_type=QueueType.PRIORITY,
                max_size=5000,
                max_message_size=self.default_message_size,
                retention_period=self.default_retention_period,
                enable_priority=True,
                enable_persistence=True,
                enable_monitoring=True,
            )

            # FIFO queue for standard messages
            fifo_queue_config = QueueConfig(
                queue_id="fifo_queue",
                queue_name="FIFO Message Queue",
                queue_type=QueueType.FIFO,
                max_size=10000,
                max_message_size=self.default_message_size,
                retention_period=self.default_retention_period,
                enable_priority=False,
                enable_persistence=True,
                enable_monitoring=True,
            )

            # Bulk processing queue
            bulk_queue_config = QueueConfig(
                queue_id="bulk_queue",
                queue_name="Bulk Processing Queue",
                queue_type=QueueType.WEIGHTED,
                max_size=20000,
                max_message_size=self.default_message_size * 10,  # 10MB
                retention_period=self.default_retention_period * 24,  # 24 hours
                enable_priority=False,
                enable_persistence=True,
                enable_monitoring=True,
            )

            # Store queue configs
            self.queue_configs[priority_queue_config.queue_id] = priority_queue_config
            self.queue_configs[fifo_queue_config.queue_id] = fifo_queue_config
            self.queue_configs[bulk_queue_config.queue_id] = bulk_queue_config

            # Initialize queues
            self.queues[priority_queue_config.queue_id] = deque(
                maxlen=priority_queue_config.max_size
            )
            self.queues[fifo_queue_config.queue_id] = deque(
                maxlen=fifo_queue_config.max_size
            )
            self.queues[bulk_queue_config.queue_id] = deque(
                maxlen=bulk_queue_config.max_size
            )

            # Initialize metrics
            for queue_id in self.queues:
                self.queue_metrics[queue_id] = QueueMetrics(
                    total_messages=0,
                    pending_messages=0,
                    processing_messages=0,
                    completed_messages=0,
                    failed_messages=0,
                    average_processing_time=0.0,
                    queue_size=0,
                )

            self.logger.info(f"Initialized {len(self.queues)} default message queues")

        except Exception as e:
            self.logger.error(f"Error initializing default queues: {e}")

    def _initialize_default_handlers(self):
        """Initialize default message handlers."""
        try:
            # Task handler
            task_handler = MessageHandler(
                handler_id="task_handler",
                handler_name="Task Message Handler",
                message_types=[MessageType.TASK],
                priority_levels=[
                    MessagePriority.CRITICAL,
                    MessagePriority.HIGH,
                    MessagePriority.NORMAL,
                ],
                handler_function=self._handle_task_message,
                is_active=True,
            )

            # Notification handler
            notification_handler = MessageHandler(
                handler_id="notification_handler",
                handler_name="Notification Message Handler",
                message_types=[MessageType.NOTIFICATION],
                priority_levels=[MessagePriority.HIGH, MessagePriority.NORMAL],
                handler_function=self._handle_notification_message,
                is_active=True,
            )

            # Event handler
            event_handler = MessageHandler(
                handler_id="event_handler",
                handler_name="Event Message Handler",
                message_types=[MessageType.EVENT],
                priority_levels=[MessagePriority.NORMAL, MessagePriority.LOW],
                handler_function=self._handle_event_message,
                is_active=True,
            )

            # Store handlers
            self.message_handlers[task_handler.handler_id] = task_handler
            self.message_handlers[notification_handler.handler_id] = (
                notification_handler
            )
            self.message_handlers[event_handler.handler_id] = event_handler

            # Index handlers by message type
            for handler in [task_handler, notification_handler, event_handler]:
                for message_type in handler.message_types:
                    self.handler_index[message_type].append(handler.handler_id)

            self.logger.info(
                f"Initialized {len(self.message_handlers)} default message handlers"
            )

        except Exception as e:
            self.logger.error(f"Error initializing default handlers: {e}")

    async def create_queue(
        self,
        queue_name: str,
        queue_type: QueueType,
        max_size: int = None,
        enable_priority: bool = True,
    ) -> str:
        """Create a new message queue."""
        try:
            queue_id = str(uuid.uuid4())

            if max_size is None:
                max_size = self.default_queue_size

            config = QueueConfig(
                queue_id=queue_id,
                queue_name=queue_name,
                queue_type=queue_type,
                max_size=max_size,
                max_message_size=self.default_message_size,
                retention_period=self.default_retention_period,
                enable_priority=enable_priority,
                enable_persistence=self.enable_persistence,
                enable_monitoring=True,
            )

            # Store config
            self.queue_configs[queue_id] = config

            # Initialize queue
            self.queues[queue_id] = deque(maxlen=max_size)

            # Initialize metrics
            self.queue_metrics[queue_id] = QueueMetrics(
                total_messages=0,
                pending_messages=0,
                processing_messages=0,
                completed_messages=0,
                failed_messages=0,
                average_processing_time=0.0,
                queue_size=0,
            )

            self.logger.info(f"Created message queue: {queue_id} - {queue_name}")

            return queue_id

        except Exception as e:
            self.logger.error(f"Error creating message queue: {e}")
            raise

    async def send_message(
        self,
        queue_id: str,
        message_type: MessageType,
        priority: MessagePriority,
        sender_id: str,
        recipient_id: str,
        payload: Any,
        expiration: Optional[datetime] = None,
    ) -> str:
        """Send a message to a queue."""
        try:
            # Validate queue exists
            if queue_id not in self.queues:
                raise ValueError(f"Queue {queue_id} does not exist")

            # Create message
            message = Message(
                message_id=str(uuid.uuid4()),
                message_type=message_type,
                priority=priority,
                sender_id=sender_id,
                recipient_id=recipient_id,
                payload=payload,
                timestamp=datetime.utcnow(),
                expiration=expiration,
            )

            # Store message
            self.messages[message.message_id] = message

            # Add to queue based on queue type
            queue = self.queues[queue_id]
            config = self.queue_configs[queue_id]

            if config.queue_type == QueueType.PRIORITY and config.enable_priority:
                # Priority queue - insert based on priority
                self._insert_priority_message(queue, message)
            elif config.queue_type == QueueType.LIFO:
                # LIFO queue - append to left
                queue.appendleft(message)
            else:
                # FIFO queue - append to right
                queue.append(message)

            # Update metrics
            self.queue_metrics[queue_id].total_messages += 1
            self.queue_metrics[queue_id].pending_messages += 1
            self.queue_metrics[queue_id].queue_size = len(queue)

            # Record message
            self.message_history[message.message_id].append(
                {
                    "timestamp": datetime.utcnow(),
                    "action": "sent",
                    "queue_id": queue_id,
                    "status": message.status.value,
                }
            )

            self.logger.info(f"Sent message {message.message_id} to queue {queue_id}")

            return message.message_id

        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    def _insert_priority_message(self, queue: deque, message: Message):
        """Insert a message into a priority queue."""
        try:
            # Find insertion position based on priority
            insert_index = 0
            for i, existing_message in enumerate(queue):
                if message.priority.value < existing_message.priority.value:
                    insert_index = i
                    break
                insert_index = i + 1

            # Insert at the appropriate position
            queue.insert(insert_index, message)

        except Exception as e:
            self.logger.error(f"Error inserting priority message: {e}")
            # Fallback to append
            queue.append(message)

    async def receive_message(
        self, queue_id: str, timeout: float = None
    ) -> Optional[Message]:
        """Receive a message from a queue."""
        try:
            # Validate queue exists
            if queue_id not in self.queues:
                raise ValueError(f"Queue {queue_id} does not exist")

            queue = self.queues[queue_id]

            # Wait for message if queue is empty
            if not queue and timeout:
                start_time = time.time()
                while not queue and (time.time() - start_time) < timeout:
                    await asyncio.sleep(0.1)

            # Get message from queue
            if queue:
                message = queue.popleft()

                # Update message status
                message.status = MessageStatus.PROCESSING

                # Update metrics
                self.queue_metrics[queue_id].pending_messages -= 1
                self.queue_metrics[queue_id].processing_messages += 1
                self.queue_metrics[queue_id].queue_size = len(queue)

                # Record message
                self.message_history[message.message_id].append(
                    {
                        "timestamp": datetime.utcnow(),
                        "action": "received",
                        "queue_id": queue_id,
                        "status": message.status.value,
                    }
                )

                self.logger.info(
                    f"Received message {message.message_id} from queue {queue_id}"
                )

                return message

            return None

        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            return None

    async def process_message(self, message: Message) -> bool:
        """Process a message using appropriate handlers."""
        try:
            start_time = time.time()

            # Find handlers for this message type
            handlers = []
            for handler_id in self.handler_index.get(message.message_type, []):
                handler = self.message_handlers.get(handler_id)
                if handler and handler.is_active:
                    handlers.append(handler)

            if not handlers:
                self.logger.warning(
                    f"No handlers found for message type: {message.message_type}"
                )
                return False

            # Process message with handlers
            success = False
            for handler in handlers:
                try:
                    # Check if handler supports this priority
                    if message.priority not in handler.priority_levels:
                        continue

                    # Process message
                    result = await handler.handler_function(message)
                    if result:
                        success = True
                        break

                except Exception as e:
                    self.logger.error(f"Error in handler {handler.handler_id}: {e}")
                    continue

            # Update message status
            if success:
                message.status = MessageStatus.COMPLETED
                self.total_messages_processed += 1
            else:
                message.status = MessageStatus.FAILED
                self.total_messages_failed += 1

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update metrics
            queue_id = self._get_message_queue_id(message)
            if queue_id:
                metrics = self.queue_metrics[queue_id]
                metrics.processing_messages -= 1
                if success:
                    metrics.completed_messages += 1
                else:
                    metrics.failed_messages += 1

                # Update average processing time
                if metrics.completed_messages > 0:
                    metrics.average_processing_time = (
                        metrics.average_processing_time
                        * (metrics.completed_messages - 1)
                        + processing_time
                    ) / metrics.completed_messages

            # Record message
            self.message_history[message.message_id].append(
                {
                    "timestamp": datetime.utcnow(),
                    "action": "processed",
                    "status": message.status.value,
                    "processing_time": processing_time,
                    "success": success,
                }
            )

            self.logger.info(
                f"Processed message {message.message_id}: {message.status.value}"
            )

            return success

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return False

    def _get_message_queue_id(self, message: Message) -> Optional[str]:
        """Get the queue ID for a message."""
        for queue_id, queue in self.queues.items():
            if message in queue:
                return queue_id
        return None

    async def _handle_task_message(self, message: Message) -> bool:
        """Handle task messages."""
        try:
            self.logger.info(f"Processing task message: {message.message_id}")

            # Extract task information from payload
            if isinstance(message.payload, dict):
                task_data = message.payload
            else:
                # Try to parse payload
                try:
                    task_data = json.loads(str(message.payload))
                except Exception:
                    logger.error(f"Error: {e}")
                    task_data = {"raw_payload": str(message.payload)}

            # Process task based on type
            task_type = task_data.get("task_type", "unknown")

            if task_type == "reconciliation":
                # Handle reconciliation task
                await self._process_reconciliation_task(task_data)
            elif task_type == "fraud_detection":
                # Handle fraud detection task
                await self._process_fraud_detection_task(task_data)
            elif task_type == "risk_assessment":
                # Handle risk assessment task
                await self._process_risk_assessment_task(task_data)
            else:
                # Handle unknown task type
                await self._process_unknown_task(task_data)

            return True

        except Exception as e:
            self.logger.error(f"Error handling task message: {e}")
            return False

    async def _handle_notification_message(self, message: Message) -> bool:
        """Handle notification messages."""
        try:
            self.logger.info(f"Processing notification message: {message.message_id}")

            # Extract notification data
            if isinstance(message.payload, dict):
                notification_data = message.payload
            else:
                notification_data = {"message": str(message.payload)}

            # Process notification
            notification_type = notification_data.get("type", "info")
            notification_message = notification_data.get("message", "No message")

            # Log notification
            if notification_type == "error":
                self.logger.error(f"Notification: {notification_message}")
            elif notification_type == "warning":
                self.logger.warning(f"Notification: {notification_message}")
            else:
                self.logger.info(f"Notification: {notification_message}")

            return True

        except Exception as e:
            self.logger.error(f"Error handling notification message: {e}")
            return False

    async def _handle_event_message(self, message: Message) -> bool:
        """Handle event messages."""
        try:
            self.logger.info(f"Processing event message: {message.message_id}")

            # Extract event data
            if isinstance(message.payload, dict):
                event_data = message.payload
            else:
                event_data = {"event": str(message.payload)}

            # Process event
            event_type = event_data.get("event_type", "unknown")
            event_data_value = event_data.get("data", {})

            # Handle different event types
            if event_type == "system_startup":
                self.logger.info("System startup event received")
            elif event_type == "system_shutdown":
                self.logger.info("System shutdown event received")
            elif event_type == "agent_status_change":
                self.logger.info(f"Agent status change: {event_data_value}")
            else:
                self.logger.info(f"Unknown event type: {event_type}")

            return True

        except Exception as e:
            self.logger.error(f"Error handling event message: {e}")
            return False

    async def _process_reconciliation_task(self, task_data: Dict[str, Any]):
        """Process reconciliation task."""
        try:
            self.logger.info("Processing reconciliation task")
            # Implementation would integrate with reconciliation agent
            await asyncio.sleep(0.1)  # Simulate processing

        except Exception as e:
            self.logger.error(f"Error processing reconciliation task: {e}")

    async def _process_fraud_detection_task(self, task_data: Dict[str, Any]):
        """Process fraud detection task."""
        try:
            self.logger.info("Processing fraud detection task")
            # Implementation would integrate with fraud agent
            await asyncio.sleep(0.1)  # Simulate processing

        except Exception as e:
            self.logger.error(f"Error processing fraud detection task: {e}")

    async def _process_risk_assessment_task(self, task_data: Dict[str, Any]):
        """Process risk assessment task."""
        try:
            self.logger.info("Processing risk assessment task")
            # Implementation would integrate with risk agent
            await asyncio.sleep(0.1)  # Simulate processing

        except Exception as e:
            self.logger.error(f"Error processing risk assessment task: {e}")

    async def _process_unknown_task(self, task_data: Dict[str, Any]):
        """Process unknown task type."""
        try:
            self.logger.warning(f"Processing unknown task type: {task_data}")
            # Implementation would handle unknown task types
            await asyncio.sleep(0.1)  # Simulate processing

        except Exception as e:
            self.logger.error(f"Error processing unknown task: {e}")

    async def _cleanup_expired_messages(self):
        """Clean up expired messages."""
        while True:
            try:
                current_time = datetime.utcnow()
                expired_messages = []

                for message_id, message in self.messages.items():
                    if message.expiration and current_time > message.expiration:
                        expired_messages.append(message_id)

                for message_id in expired_messages:
                    message = self.messages[message_id]
                    message.status = MessageStatus.EXPIRED

                    # Remove from queues
                    for queue in self.queues.values():
                        if message in queue:
                            queue.remove(message)

                    # Update metrics
                    queue_id = self._get_message_queue_id(message)
                    if queue_id:
                        self.queue_metrics[queue_id].pending_messages -= 1
                        self.queue_metrics[queue_id].queue_size = len(
                            self.queues[queue_id]
                        )

                if expired_messages:
                    self.logger.info(
                        f"Cleaned up {len(expired_messages)} expired messages"
                    )

                await asyncio.sleep(60)  # Clean up every minute

            except Exception as e:
                self.logger.error(f"Error cleaning up expired messages: {e}")
                await asyncio.sleep(60)

    async def _monitor_queue_health(self):
        """Monitor queue health and performance."""
        while True:
            try:
                # Check queue health
                for queue_id, queue in self.queues.items():
                    config = self.queue_configs[queue_id]
                    metrics = self.queue_metrics[queue_id]

                    # Check if queue is getting full
                    if len(queue) > config.max_size * 0.8:
                        self.logger.warning(f"Queue {queue_id} is 80% full")

                    # Check processing performance
                    if (
                        metrics.processing_messages > 0
                        and metrics.average_processing_time > 5.0
                    ):
                        self.logger.warning(
                            f"Queue {queue_id} has slow processing: {metrics.average_processing_time:.2f}s"
                        )

                    # Check failure rate
                    if metrics.total_messages > 0:
                        failure_rate = metrics.failed_messages / metrics.total_messages
                        if failure_rate > 0.1:  # 10% failure rate
                            self.logger.warning(
                                f"Queue {queue_id} has high failure rate: {failure_rate:.2%}"
                            )

                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                self.logger.error(f"Error monitoring queue health: {e}")
                await asyncio.sleep(30)

    async def _persist_queue_data(self):
        """Persist queue data to disk."""
        while True:
            try:
                if not self.enable_persistence:
                    await asyncio.sleep(300)
                    continue

                # Create persistence directory
                persistence_dir = Path(self.persistence_path)
                persistence_dir.mkdir(parents=True, exist_ok=True)

                # Persist queue data
                for queue_id, queue in self.queues.items():
                    queue_file = persistence_dir / f"{queue_id}_queue.pkl"
                    with open(queue_file, "wb") as f:
                        pickle.dump(list(queue), f)

                # Persist message data
                messages_file = persistence_dir / "messages.pkl"
                with open(messages_file, "wb") as f:
                    pickle.dump(self.messages, f)

                # Persist metrics
                metrics_file = persistence_dir / "metrics.pkl"
                with open(metrics_file, "wb") as f:
                    pickle.dump(self.queue_metrics, f)

                await asyncio.sleep(300)  # Persist every 5 minutes

            except Exception as e:
                self.logger.error(f"Error persisting queue data: {e}")
                await asyncio.sleep(300)

    def get_queue_metrics(
        self, queue_id: str = None
    ) -> Union[QueueMetrics, Dict[str, QueueMetrics]]:
        """Get metrics for a specific queue or all queues."""
        if queue_id:
            return self.queue_metrics.get(queue_id)
        else:
            return self.queue_metrics

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics."""
        return {
            "total_messages_processed": self.total_messages_processed,
            "total_messages_failed": self.total_messages_failed,
            "average_processing_time": self.average_processing_time,
            "total_queues": len(self.queues),
            "total_handlers": len(self.message_handlers),
            "total_messages": len(self.messages),
            "queue_metrics": self.queue_metrics,
        }

# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_queue_size": 10000,
        "default_message_size": 1024 * 1024,
        "default_retention_period": 3600,
        "enable_persistence": True,
        "persistence_path": "./message_queue_data",
    }

    # Initialize message queue
    message_queue = MessageQueue(config)

    print("MessageQueue system initialized successfully!")
