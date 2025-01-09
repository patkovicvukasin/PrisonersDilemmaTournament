from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class KuwaitBot(AbstractBot):
    @property
    def name(self) -> str:
        return "New Tactic Bot"

    @property
    def description(self) -> str:
        return (
            "• Izdajemo u prvoj i poslednjoj (200.) rundi. "
            "• Ako protivnik izda prve dve runde, izdajemo treću. "
            "• U ostalim rundama (2–199, osim 3. ako se triguje iznad) sarađujemo, "
            "osim ako je protivnik u prethodna 3 poteza izdao >=2 puta, tada mi defektujemo jednu rundu."
        )

    def strategy(self,
                 my_history: List[Move],
                 opponent_history: List[Move],
                 current_round: int,
                 total_rounds: int) -> Move:
        
        # 1) Ako je prva runda => DEFECT
        if current_round == 1:
            return Move.DEFECT
        
        # 2) Ako je poslednja runda (pretpostavljamo 200) => DEFECT
        if current_round == total_rounds:
            return Move.DEFECT
        
        # 3) Ako je TREĆA runda i protivnik je prva dva poteza izdao, i mi izdajemo
        if current_round == 3:
            # Treba da imamo 2 poteza u opponent_history
            if len(opponent_history) >= 2:
                if (opponent_history[0] == Move.DEFECT 
                    and opponent_history[1] == Move.DEFECT):
                    return Move.DEFECT
            # Ako nije oba izdao, nastavljamo normalnom logikom (ispod)
        
        # 4) Ako nemamo bar 3 protivnička poteza, a već smo prošli prvu i drugu rundu
        #    (ovde to može biti samo runda 2 ili 3, ali 3 smo već pokrili iznad) => sarađuj
        if len(opponent_history) < 3:
            return Move.COOPERATE
        
        # 5) Inače (runda 4 – 199), gledamo poslednja 3 poteza protivnika
        last_3 = opponent_history[-3:]
        if last_3.count(Move.DEFECT) >= 2:
            return Move.DEFECT
        
        # 6) U svim ostalim slučajevima sarađujemo
        return Move.COOPERATE
