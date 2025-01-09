from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class MilestoneBot(AbstractBot):
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        return "Milestone Bot"
    
    @property
    def description(self) -> str:
        return "A bot that defects on milestone rounds (1/5, 1/3, 1/2, and all of total rounds)"
    
    def is_milestone_round(self, current_round: int) -> bool:
        milestones = [
            round(self.total_rounds / 5),
            round(self.total_rounds / 3),
            round(self.total_rounds / 2),
            self.total_rounds
        ]
        return current_round in milestones
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        if self.is_milestone_round(current_round):
            return self.defect
        return self.cooperate
