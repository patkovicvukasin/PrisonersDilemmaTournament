from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class AlwaysDefectBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Always Defect Bot"
    
    @property
    def description(self) -> str:
        return "A bot that always defects"
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        return self.defect