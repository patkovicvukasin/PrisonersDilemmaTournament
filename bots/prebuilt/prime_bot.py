from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List
from math import sqrt

class PrimeBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Prime Bot"
    
    @property
    def description(self) -> str:
        return "A bot that cooperates on prime rounds and defects on non-prime rounds"
    
    def is_prime(self, n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], current_round: int, total_rounds: int) -> Move:
        return self.cooperate if self.is_prime(current_round) else self.defect
