from __future__ import annotations
from abc import abstractmethod, ABC


class Transformer(ABC):
    """
    The Creator class declares the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """

    @abstractmethod
    def initialize_data(self, config):
        pass

    @abstractmethod
    def transform_data(self, adapted_data):
        pass
