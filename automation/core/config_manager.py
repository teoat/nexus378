#!/usr/bin/env python3
"""
⚙️ CONFIGURATION MANAGER - UNIFIED CONFIGURATION SYSTEM ⚙️

This module provides unified configuration management for the consolidated automation system.
It handles configuration loading, validation, hot reloading, and environment-specific settings.

Version: 1.0.0
Status: Production Ready
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

logger = logging.getLogger(__name__)

class ConfigSource(Enum):
    """Configuration source types"""
    JSON = "json"
    YAML = "yaml"
    ENV = "environment"
    DEFAULT = "default"

class ConfigValidationError(Exception):
    """Configuration validation error"""
    pass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    database: str = "nexus_automation"
    pool_size: int = 10
    max_overflow: int = 20
    timeout: int = 30
    ssl_mode: str = "prefer"

@dataclass
class WorkerConfig:
    """Worker configuration settings"""
    max_workers: int = 100
    min_workers: int = 5
    worker_timeout: int = 1800
    health_check_interval: int = 60
    auto_scaling: bool = True
    scaling_threshold: float = 0.8
    scaling_cooldown: int = 300

@dataclass
class TaskConfig:
    """Task configuration settings"""
    max_concurrent_tasks: int = 50
    task_timeout: int = 1800
    retry_attempts: int = 3
    retry_delay: int = 60
    priority_levels: int = 5
    enable_dependencies: bool = True
    max_dependency_depth: int = 10

@dataclass
class MonitoringConfig:
    """Monitoring configuration settings"""
    enable_health_monitoring: bool = True
    health_check_interval: int = 60
    enable_performance_monitoring: bool = True
    performance_check_interval: int = 300
    enable_metrics_collection: bool = True
    metrics_collection_interval: int = 30
    enable_alerting: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["log"])

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    enable_authentication: bool = True
    enable_authorization: bool = True
    jwt_secret: str = ""
    jwt_expiry: int = 3600
    enable_encryption: bool = True
    encryption_key: str = ""
    enable_audit_logging: bool = True

@dataclass
class SystemConfig:
    """System configuration settings"""
    environment: str = "development"
    log_level: str = "INFO"
    log_file: str = "automation.log"
    enable_debug: bool = False
    max_memory_usage: int = 1024  # MB
    enable_graceful_shutdown: bool = True
    shutdown_timeout: int = 30

class ConfigManager:
    """
    Unified configuration manager for the consolidated automation system.
    
    This class provides:
    - Configuration loading from multiple sources
    - Environment-specific configuration
    - Hot reloading of configuration changes
    - Configuration validation
    - Secure configuration storage
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager"""
        self.config_path = config_path or "automation/config/settings.json"
        self.config_dir = Path(self.config_path).parent
        self.config_file = Path(self.config_path)
        
        # Configuration storage
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._environment: str = "development"
        
        # Hot reloading
        self._observer = None
        self._watchdog_enabled = False
        self._last_modified = 0
        
        # Configuration validation
        self._validation_schema = {}
        
        logger.info(f"🔧 Configuration Manager initialized with path: {self.config_path}")
    
    async def initialize(self):
        """Initialize the configuration manager"""
        try:
            logger.info("🔄 Initializing Configuration Manager...")
            
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load default configurations
            self._load_defaults()
            
            # Load configuration from file
            await self._load_config()
            
            # Load environment variables
            self._load_environment_variables()
            
            # Validate configuration
            self._validate_config()
            
            # Setup hot reloading
            await self._setup_hot_reloading()
            
            logger.info("✅ Configuration Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration Manager initialization failed: {e}")
            raise
    
    def _load_defaults(self):
        """Load default configuration values"""
        logger.debug("Loading default configurations...")
        
        # System defaults
        self._defaults["system"] = asdict(SystemConfig())
        
        # Database defaults
        self._defaults["database"] = asdict(DatabaseConfig())
        
        # Worker defaults
        self._defaults["worker"] = asdict(WorkerConfig())
        
        # Task defaults
        self._defaults["task"] = asdict(TaskConfig())
        
        # Monitoring defaults
        self._defaults["monitoring"] = asdict(MonitoringConfig())
        
        # Security defaults
        self._defaults["security"] = asdict(SecurityConfig())
        
        # Merge defaults into main config
        self._config.update(self._defaults)
        
        logger.debug("Default configurations loaded")
    
    async def _load_config(self):
        """Load configuration from file"""
        try:
            if not self.config_file.exists():
                logger.warning(f"Configuration file not found: {self.config_file}")
                logger.info("Creating default configuration file...")
                await self._create_default_config()
                return
            
            # Check file modification time
            current_modified = self.config_file.stat().st_mtime
            if current_modified <= self._last_modified:
                logger.debug("Configuration file unchanged, skipping reload")
                return
            
            self._last_modified = current_modified
            
            # Load based on file extension
            if self.config_file.suffix.lower() == '.json':
                await self._load_json_config()
            elif self.config_file.suffix.lower() in ['.yml', '.yaml']:
                await self._load_yaml_config()
            else:
                logger.warning(f"Unsupported configuration file format: {self.config_file.suffix}")
                return
            
            logger.info(f"Configuration loaded from: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
    
    async def _load_json_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Merge file config with defaults
            self._merge_config(file_config)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise ConfigValidationError(f"Invalid JSON configuration: {e}")
        except Exception as e:
            logger.error(f"Error reading JSON configuration: {e}")
            raise
    
    async def _load_yaml_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
            
            # Merge file config with defaults
            self._merge_config(file_config)
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            raise ConfigValidationError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            logger.error(f"Error reading YAML configuration: {e}")
            raise
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing configuration"""
        def deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
            """Recursively merge configuration dictionaries"""
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base
        
        # Deep merge the new configuration
        self._config = deep_merge(self._config.copy(), new_config)
        
        logger.debug("Configuration merged successfully")
    
    def _load_environment_variables(self):
        """Load configuration from environment variables"""
        logger.debug("Loading environment variables...")
        
        # Environment-specific configuration
        env = os.getenv("NEXUS_ENV", "development")
        self._environment = env
        self._config["system"]["environment"] = env
        
        # Database configuration from environment
        if os.getenv("DB_HOST"):
            self._config["database"]["host"] = os.getenv("DB_HOST")
        if os.getenv("DB_PORT"):
            self._config["database"]["port"] = int(os.getenv("DB_PORT"))
        if os.getenv("DB_USERNAME"):
            self._config["database"]["username"] = os.getenv("DB_USERNAME")
        if os.getenv("DB_PASSWORD"):
            self._config["database"]["password"] = os.getenv("DB_PASSWORD")
        if os.getenv("DB_DATABASE"):
            self._config["database"]["database"] = os.getenv("DB_DATABASE")
        
        # Worker configuration from environment
        if os.getenv("MAX_WORKERS"):
            self._config["worker"]["max_workers"] = int(os.getenv("MAX_WORKERS"))
        if os.getenv("WORKER_TIMEOUT"):
            self._config["worker"]["worker_timeout"] = int(os.getenv("WORKER_TIMEOUT"))
        
        # Task configuration from environment
        if os.getenv("MAX_CONCURRENT_TASKS"):
            self._config["task"]["max_concurrent_tasks"] = int(os.getenv("MAX_CONCURRENT_TASKS"))
        if os.getenv("TASK_TIMEOUT"):
            self._config["task"]["task_timeout"] = int(os.getenv("TASK_TIMEOUT"))
        
        # Security configuration from environment
        if os.getenv("JWT_SECRET"):
            self._config["security"]["jwt_secret"] = os.getenv("JWT_SECRET")
        if os.getenv("ENCRYPTION_KEY"):
            self._config["security"]["encryption_key"] = os.getenv("ENCRYPTION_KEY")
        
        logger.debug(f"Environment variables loaded for environment: {env}")
    
    async def _create_default_config(self):
        """Create default configuration file"""
        try:
            # Create default configuration
            default_config = {
                "system": {
                    "environment": "development",
                    "log_level": "INFO",
                    "log_file": "automation.log",
                    "enable_debug": False,
                    "max_memory_usage": 1024,
                    "enable_graceful_shutdown": True,
                    "shutdown_timeout": 30
                },
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "username": "postgres",
                    "password": "",
                    "database": "nexus_automation",
                    "pool_size": 10,
                    "max_overflow": 20,
                    "timeout": 30,
                    "ssl_mode": "prefer"
                },
                "worker": {
                    "max_workers": 100,
                    "min_workers": 5,
                    "worker_timeout": 1800,
                    "health_check_interval": 60,
                    "auto_scaling": True,
                    "scaling_threshold": 0.8,
                    "scaling_cooldown": 300
                },
                "task": {
                    "max_concurrent_tasks": 50,
                    "task_timeout": 1800,
                    "retry_attempts": 3,
                    "retry_delay": 60,
                    "priority_levels": 5,
                    "enable_dependencies": True,
                    "max_dependency_depth": 10
                },
                "monitoring": {
                    "enable_health_monitoring": True,
                    "health_check_interval": 60,
                    "enable_performance_monitoring": True,
                    "performance_check_interval": 300,
                    "enable_metrics_collection": True,
                    "metrics_collection_interval": 30,
                    "enable_alerting": True,
                    "alert_channels": ["log"]
                },
                "security": {
                    "enable_authentication": True,
                    "enable_authorization": True,
                    "jwt_secret": "",
                    "jwt_expiry": 3600,
                    "enable_encryption": True,
                    "encryption_key": "",
                    "enable_audit_logging": True
                }
            }
            
            # Write configuration file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            # Update internal config
            self._config.update(default_config)
            
            logger.info(f"Default configuration file created: {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration values"""
        try:
            logger.debug("Validating configuration...")
            
            # Validate required fields
            required_fields = [
                "system.environment",
                "database.host",
                "database.port",
                "worker.max_workers",
                "task.max_concurrent_tasks"
            ]
            
            for field_path in required_fields:
                value = self._get_nested_value(field_path)
                if value is None:
                    raise ConfigValidationError(f"Required configuration field missing: {field_path}")
            
            # Validate numeric ranges
            if self._config["worker"]["max_workers"] <= 0:
                raise ConfigValidationError("max_workers must be greater than 0")
            
            if self._config["task"]["max_concurrent_tasks"] <= 0:
                raise ConfigValidationError("max_concurrent_tasks must be greater than 0")
            
            if self._config["database"]["port"] < 1 or self._config["database"]["port"] > 65535:
                raise ConfigValidationError("Database port must be between 1 and 65535")
            
            logger.debug("Configuration validation passed")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ConfigValidationError(f"Configuration validation failed: {e}")
    
    def _get_nested_value(self, field_path: str) -> Any:
        """Get nested configuration value by dot notation"""
        try:
            keys = field_path.split('.')
            value = self._config
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            return None
    
    async def _setup_hot_reloading(self):
        """Setup hot reloading for configuration changes"""
        try:
            if not self.config_file.exists():
                logger.warning("Configuration file not found, hot reloading disabled")
                return
            
            # Setup file watcher
            self._observer = Observer()
            event_handler = ConfigFileHandler(self)
            self._observer.schedule(event_handler, str(self.config_dir), recursive=False)
            self._observer.start()
            
            self._watchdog_enabled = True
            logger.info("✅ Hot reloading enabled for configuration changes")
            
        except Exception as e:
            logger.warning(f"Hot reloading setup failed: {e}")
            logger.info("Configuration changes will require manual reload")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            if '.' in key:
                value = self._get_nested_value(key)
            else:
                value = self._config.get(key, default)
            
            return value
        except Exception as e:
            logger.debug(f"Error getting configuration key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)"""
        try:
            if '.' in key:
                keys = key.split('.')
                config = self._config
                
                # Navigate to the parent of the target key
                for key_part in keys[:-1]:
                    if key_part not in config:
                        config[key_part] = {}
                    config = config[key_part]
                
                # Set the value
                config[keys[-1]] = value
            else:
                self._config[key] = value
            
            logger.debug(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            logger.error(f"Error setting configuration key '{key}': {e}")
            raise
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    def get_environment(self) -> str:
        """Get current environment"""
        return self._environment
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self._environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self._environment.lower() == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self._environment.lower() == "testing"
    
    async def reload(self):
        """Manually reload configuration"""
        try:
            logger.info("🔄 Reloading configuration...")
            
            # Reset to defaults
            self._config.clear()
            self._load_defaults()
            
            # Load from file
            await self._load_config()
            
            # Load environment variables
            self._load_environment_variables()
            
            # Validate configuration
            self._validate_config()
            
            logger.info("✅ Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Configuration reload failed: {e}")
            raise
    
    async def save(self):
        """Save current configuration to file"""
        try:
            logger.info("💾 Saving configuration to file...")
            
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Configuration saved to: {self.config_file}")
            
        except Exception as e:
            logger.error(f"❌ Configuration save failed: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the configuration manager"""
        try:
            logger.info("🔄 Shutting down Configuration Manager...")
            
            # Stop file watcher
            if self._observer and self._observer.is_alive():
                self._observer.stop()
                self._observer.join()
            
            logger.info("✅ Configuration Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Configuration Manager shutdown failed: {e}")


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.last_modified = 0
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        if event.src_path == str(self.config_manager.config_file):
            # Debounce rapid file changes
            current_time = time.time()
            if current_time - self.last_modified < 1.0:  # 1 second debounce
                return
            
            self.last_modified = current_time
            
            logger.info("📝 Configuration file changed, triggering reload...")
            
            # Schedule reload in event loop
            asyncio.create_task(self.config_manager.reload())


# Utility functions for external use
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (global access)"""
    # This would need to be implemented with a global config manager instance
    logger.warning("Global config access not implemented, use ConfigManager instance")
    return default


# Main entry point for testing
async def main():
    """Main entry point for testing the configuration manager"""
    config_manager = ConfigManager()
    
    try:
        await config_manager.initialize()
        
        # Test configuration access
        print(f"Environment: {config_manager.get('system.environment')}")
        print(f"Max Workers: {config_manager.get('worker.max_workers')}")
        print(f"Database Host: {config_manager.get('database.host')}")
        
        # Test configuration modification
        config_manager.set('worker.max_workers', 150)
        print(f"Updated Max Workers: {config_manager.get('worker.max_workers')}")
        
        # Save configuration
        await config_manager.save()
        
        # Wait for a bit to test hot reloading
        print("Configuration manager running. Press Ctrl+C to exit...")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    finally:
        await config_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
