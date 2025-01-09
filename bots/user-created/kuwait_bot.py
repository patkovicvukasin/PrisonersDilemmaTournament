from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class KuwaitBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Kuwait Bot"

    @property
    def description(self) -> str:
        return()

    def strategy(self,
                 my_history: List[Move],
                 opponent_history: List[Move],
                 current_round: int,
                 total_rounds: int) -> Move:
        
        if current_round == 1:
            return Move.DEFECT
        
        if current_round == total_rounds:
            return Move.DEFECT
        
        if current_round == 3:
            if len(opponent_history) >= 2:
                if (opponent_history[0] == Move.DEFECT 
                    and opponent_history[1] == Move.DEFECT):
                    return Move.DEFECT
        
        if len(opponent_history) < 3:
            return Move.COOPERATE
        
        last_3 = opponent_history[-3:]
        if last_3.count(Move.DEFECT) >= 2:
            return Move.DEFECT
        
        return Move.COOPERATE
