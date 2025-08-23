"""
Plugin Manager for the Forensic Reconciliation Platform

This module provides the PluginManager, which is responsible for discovering,
loading, and managing the lifecycle of all plugins.
"""

import importlib.util
import inspect
import logging
import os
from typing import Dict

from .plugin_interface import PluginInterface

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages the discovery, loading, and lifecycle of plugins.
    """

    def __init__(self, plugin_folder: str = "plugins"):
        """
        Initializes the PluginManager.

        Args:
            plugin_folder (str): The path to the directory to search for plugins.
                                 Can be absolute or relative to this file's location.
        """
        if os.path.isabs(plugin_folder):
            self.plugin_folder = plugin_folder
        else:
            self.plugin_folder = os.path.join(os.path.dirname(__file__), plugin_folder)

        self.loaded_plugins: Dict[str, PluginInterface] = {}
        logger.info(
            f"PluginManager initialized. Plugin folder set to: {self.plugin_folder}"
        )

    def discover_and_load_plugins(self):
        """
        Discovers all available plugins from the plugin folder, loads them,
        and initializes them.
        """
        logger.info("Starting plugin discovery...")
        if not os.path.isdir(self.plugin_folder):
            logger.warning(
                f"Plugin folder '{self.plugin_folder}' not found. No plugins will be loaded."
            )
            return

        for filename in os.listdir(self.plugin_folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module_path = os.path.join(self.plugin_folder, filename)

                try:
                    self._load_module_and_register_plugins(module_name, module_path)
                except Exception as e:
                    logger.error(
                        f"Failed to load or register plugins from {module_name}: {e}",
                        exc_info=True,
                    )

        logger.info(
            f"Plugin discovery complete. Loaded {len(self.loaded_plugins)} plugins."
        )

    def _load_module_and_register_plugins(self, module_name: str, module_path: str):
        """
        Loads a module from a given path and registers any valid plugins found within it.
        """
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            logger.error(f"Could not create module spec for {module_path}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, PluginInterface)
                and obj is not PluginInterface
            ):
                try:
                    plugin_instance = obj()
                    if plugin_instance.name in self.loaded_plugins:
                        logger.warning(
                            f"Plugin with name '{plugin_instance.name}' already loaded. Skipping duplicate."
                        )
                        continue

                    # Initialize the plugin
                    plugin_instance.initialize()

                    # Store the loaded plugin
                    self.loaded_plugins[plugin_instance.name] = plugin_instance
                    logger.info(
                        f"Successfully loaded and registered plugin: '{plugin_instance.name}' from {module_name}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to instantiate or register plugin class '{obj.__name__}' from {module_name}: {e}",
                        exc_info=True,
                    )

    def shutdown(self):
        """
        Properly shuts down all loaded plugins.
        """
        logger.info("Shutting down all loaded plugins...")
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                plugin.unload()
                logger.info(f"Plugin '{plugin_name}' unloaded successfully.")
            except Exception as e:
                logger.error(
                    f"Error unloading plugin '{plugin_name}': {e}", exc_info=True
                )
        self.loaded_plugins.clear()
        logger.info("All plugins shut down.")

    def get_plugin(self, name: str) -> PluginInterface:
        """
        Retrieves a loaded plugin by its name.
        """
        return self.loaded_plugins.get(name)

    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """
        Returns a dictionary of all loaded plugins.
        """
        return self.loaded_plugins
