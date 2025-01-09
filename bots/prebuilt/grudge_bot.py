from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class GrudgeBot(AbstractBot):
    def __init__(self):
        super().__init__()  # Add this line to initialize parent class
        self.been_betrayed = False
    
    @property
    def name(self) -> str:
        return "Grudge Bot"
    
    @property
    def description(self) -> str:
        return "A bot that never forgives betrayal"
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        if not opponent_history:
            return self.cooperate
            
        if not self.been_betrayed and opponent_history[-1] == Move.DEFECT:
            self.been_betrayed = True
            
        return self.defect if self.been_betrayed else self.cooperate