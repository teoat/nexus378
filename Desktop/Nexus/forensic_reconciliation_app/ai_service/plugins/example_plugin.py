"""
Example Plugin for the Forensic Reconciliation Platform
"""

import logging
from .plugin_interface import PluginInterface

logger = logging.getLogger(__name__)

class ExamplePlugin(PluginInterface):
    """
    An example plugin that demonstrates the basic structure of a plugin.
    """

    @property
    def name(self) -> str:
        return "Example Plugin"

    @property
    def description(self) -> str:
        return "A simple plugin that logs messages during its lifecycle."

    def initialize(self, **kwargs) -> None:
        """
        Called when the plugin is initialized.
        """
        logger.info("ExamplePlugin: Initialized!")
        # In a real plugin, you might connect to a database or load resources here.

    def unload(self) -> None:
        """
        Called when the plugin is unloaded.
        """
        logger.info("ExamplePlugin: Unloaded!")
        # In a real plugin, you would clean up resources here.

# Note: The PluginManager will automatically discover and instantiate classes
# that inherit from PluginInterface in this file. You can have multiple
# plugin classes in a single file if needed.
