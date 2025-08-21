from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Base class for all AI agents.
    """

    @abstractmethod
    def process(self, data):
        """
        Process the given data.

        This method must be implemented by subclasses.

        :param data: The data to be processed.
        :return: The processed data.
        """
        pass
