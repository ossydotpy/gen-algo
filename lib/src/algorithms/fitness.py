from typing import Dict, List

from lib.src.models.individual import Individual
from lib.src.models.penalties.penalty import Penalties
from lib.src.models.rewards.reward import Rewards
from lib.src.utils.validators import TimetableValidator
from lib.src.models.rewards.rewards import reward_objects
from lib.src.models.penalties.penalties import penalty_objects


class FitnessEvaluator:
    """Calculate the fitness of an individual.
    Args: subjects (List[str]): The list of subjects.
          time_slots (List[str]): The list of time slots.
          preferences (Dict): The preferences of the students.
    """

    def __init__(self, subjects: List[str], time_slots: List[str], preferences: Dict):
        self.subjects = subjects
        self.time_slots = time_slots
        self.preferences = preferences
        self.penalties = Penalties()
        self.rewards = Rewards()

        for penalty in penalty_objects:
            self.penalties.register_penalty(penalty)
        for reward in reward_objects:
            self.rewards.register_reward(reward)

    def calculate_fitness(self, individual: Individual) -> float:
        if not TimetableValidator.is_valid(individual, self.subjects, self.time_slots):
            return float("-inf")
        penalty = self.penalties.calculate_total_penalty(
            individual, self.preferences, self.subjects, self.time_slots
        )
        reward = self.rewards.calculate_total_reward(
            individual, self.preferences, self.subjects, self.time_slots
        )
        return 1000 - penalty + reward
