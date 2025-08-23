import logging
import os
import shutil
import sys
import unittest
from unittest.mock import MagicMock, patch

# Use absolute import based on the project structure
from Desktop.Nexus.forensic_reconciliation_app.ai_service.plugins.plugin_manager import (
    PluginManager,
)

from .plugin_interface import PluginInterface
from .plugin_manager import PluginManager

# Suppress logging for cleaner test output
logging.disable(logging.CRITICAL)


class TestPluginManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for test plugins and add it to sys.path."""
        self.test_plugin_dir = os.path.abspath("test_plugins_temp")
        os.makedirs(self.test_plugin_dir, exist_ok=True)
        sys.path.insert(0, self.test_plugin_dir)

        # Create a valid plugin file that uses an absolute import
        # This ensures it references the same PluginInterface class as the manager
        with open(os.path.join(self.test_plugin_dir, "valid_plugin.py"), "w") as f:
            f.write(
                """
import logging
from ..plugin_interface import PluginInterface

class ValidPlugin(PluginInterface):
    @property
    def name(self): return "Valid Test Plugin"
    @property
    def description(self): return "A valid plugin for testing."
    def initialize(self, **kwargs): logging.info("ValidPlugin Initialized")
    def unload(self): logging.info("ValidPlugin Unloaded")
"""
            )

        # Create a file that is not a plugin
        with open(os.path.join(self.test_plugin_dir, "not_a_plugin.py"), "w") as f:
            f.write("class NotAPlugin: pass")

        # Create a file with a class that doesn't inherit from the interface
        with open(
            os.path.join(self.test_plugin_dir, "invalid_inheritance.py"), "w"
        ) as f:
            f.write(
                """
class InvalidPlugin:
    @property
    def name(self): return "Invalid Plugin"
    def initialize(self, **kwargs): pass
    def unload(self): pass
"""
            )

        # Create a file with a syntax error
        with open(os.path.join(self.test_plugin_dir, "broken_plugin.py"), "w") as f:
            f.write("this is a syntax error:")

        # Create an __init__.py file in the test directory
        with open(os.path.join(self.test_plugin_dir, "__init__.py"), "w") as f:
            f.write("# Test plugins package")

    def tearDown(self):
        """Remove the temporary directory and clean up sys.path."""
        sys.path.pop(0)
        shutil.rmtree(self.test_plugin_dir)

    def test_discover_and_load_valid_plugin(self):
        """Test that a valid plugin is discovered and loaded correctly."""
        manager = PluginManager(plugin_folder=self.test_plugin_dir)
        manager.discover_and_load_plugins()

        self.assertEqual(len(manager.loaded_plugins), 1)
        self.assertIn("Valid Test Plugin", manager.loaded_plugins)
        plugin = manager.get_plugin("Valid Test Plugin")
        self.assertIsInstance(plugin, PluginInterface)

    def test_ignore_invalid_and_broken_plugins(self):
        """Test that invalid or broken files do not crash the manager."""
        manager = PluginManager(plugin_folder=self.test_plugin_dir)

        try:
            manager.discover_and_load_plugins()
        except Exception as e:
            self.fail(f"Plugin discovery crashed with an unexpected exception: {e}")

        self.assertEqual(len(manager.loaded_plugins), 1)
        self.assertIn("Valid Test Plugin", manager.loaded_plugins)

    def test_shutdown_calls_unload(self):
        """Test that the shutdown method calls unload on loaded plugins."""
        manager = PluginManager(plugin_folder=self.test_plugin_dir)
        manager.discover_and_load_plugins()

        plugin = manager.get_plugin("Valid Test Plugin")
        plugin.unload = MagicMock()

        manager.shutdown()

        plugin.unload.assert_called_once()
        self.assertEqual(len(manager.loaded_plugins), 0)


if __name__ == "__main__":
    unittest.main()
