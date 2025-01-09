from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class TitForTatBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Tit for Tat Bot"
    
    @property
    def description(self) -> str:
        return "A bot that copies opponent's last move"
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        if not opponent_history:
            return self.cooperate
        return opponent_history[-1]