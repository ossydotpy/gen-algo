from abc import ABC, abstractmethod
from typing import Dict, List

from lib.src.models.individual import Individual


class BasePenalty(ABC):
    def __init__(self, weight: float):
        self.weight = weight

    @abstractmethod
    def calculate(
        self,
        individual: Individual,
        preferences: Dict,
        subjects: List[str],
        time_slots: List[str],
    ) -> float:
        """Calculates the penalty for the given individual. Child classes must override this method."""
        pass


class Penalties:
    def __init__(self, penalties: List[BasePenalty]=None):
        if penalties is None:
            penalties = []
        self.penalties: List[BasePenalty] = penalties

    def register_penalty(self, penalty: BasePenalty):
        self.penalties.append(penalty)

    def calculate_total_penalty(
        self,*args, **kwargs
    ) -> float:
        return sum(penalty.calculate(*args, **kwargs)*penalty.weight for penalty in self.penalties)
