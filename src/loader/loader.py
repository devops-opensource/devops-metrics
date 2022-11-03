from __future__ import annotations
from src.loader import loader
from abc import abstractmethod, ABC
import pandas as pd


class Loader(ABC):
    """
    The Creator class declare the factory method that is supposed to return an
    object of a Product class. The Creator's subclasses usually provide the
    implementation of this method.
    """
    @abstractmethod
    def initialize_data(self):
        pass

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def adapt_data(self):
        pass
