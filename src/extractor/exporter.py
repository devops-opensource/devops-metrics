from __future__ import annotations
from abc import abstractmethod, ABC


class Exporter(ABC):
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    @abstractmethod
    def initialize_data(self):
        pass

    @abstractmethod
    def extract_data(self):
        pass

    @abstractmethod
    def adapt_data(self):
        pass
