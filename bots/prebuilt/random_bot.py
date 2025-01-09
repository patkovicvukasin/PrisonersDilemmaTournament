from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List
import random

class RandomBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Random Bot"
    
    @property
    def description(self) -> str:
        return "A bot that makes random decisions"
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        return random.choice([self.cooperate, self.defect])