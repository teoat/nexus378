"""
Plugin Interface for the Forensic Reconciliation Platform

This module defines the abstract base class that all plugins must inherit from.
It ensures that all plugins adhere to a common interface for discovery, loading,
and execution.
"""

from abc import ABC, abstractmethod

class PluginInterface(ABC):
    """
    Abstract Base Class for all plugins.

    Plugins should subclass this and implement the required properties and methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """A user-friendly name for the plugin."""
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the plugin does."""
        raise NotImplementedError

    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """
        Initializes the plugin with any required context or resources.
        This method is called by the PluginManager after the plugin is loaded.

        Args:
            **kwargs: Arbitrary keyword arguments that the application may pass.
                      This allows for future flexibility.
        """
        raise NotImplementedError

    @abstractmethod
    def unload(self) -> None:
        """
        Cleans up any resources used by the plugin.
        This method is called by the PluginManager when the application is shutting down.
        """
        raise NotImplementedError
