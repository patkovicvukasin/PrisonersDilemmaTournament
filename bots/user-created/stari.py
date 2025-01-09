from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List

class KuwaitBot(AbstractBot):
    def __init__(self):
        super().__init__()
        
        # Pamtimo da li treba da odradimo 'prisilnih' 3 runde defekta
        self.force_defect_for_3 = 0
        
        # Definišemo raspon rundi u kojima nasumično izdajemo:
        # Od 6. do 190. (inclusive)
        total_rounds = 200
        valid_rounds = list(range(6, total_rounds - 10 + 1))  # 6..190
        
        # Nasumično biramo 30 rundi iz tog skupa
        self.forced_defect_rounds = set(random.sample(valid_rounds, 30))

    @property
    def name(self) -> str:
        return "Moj bot"

    @property
    def description(self) -> str:
        return (
            "• Prvih 5 rundi nominalno sarađuje, ali ako protivnik prva 2 poteza izda, "
            "onda mi naredna 3 poteza uzastopno izdajemo. "
            "• Posle 5. runde, gleda prethodna 3 poteza protivnika: ako je poslednji potez COOP i "
            "bar 2 od 3 su COOP, i mi sarađujemo, inače izdajemo. "
            "• U 30 slučajno izabranih rundi (između 6. i 190.) uvek izdajemo. "
            "• U poslednjih 10 rundi (191–200) uvek izdajemo."
        )

    def strategy(self,
                 my_history: List[Move],
                 opponent_history: List[Move],
                 current_round: int,
                 total_rounds: int) -> Move:

        # 1) Ako smo još u "3 prisilna defekta" zbog prve dve izdaje od protivnika
        if self.force_defect_for_3 > 0:
            self.force_defect_for_3 -= 1
            return Move.DEFECT
        
        # 2) Prvih 5 rundi nominalno sarađujemo...
        if current_round <= 5:
            # ...ali na početku 3. runde proveravamo da li je protivnik
            # prva 2 poteza (runda 1 i 2) izdao
            # (možemo čekati dok *imamo* bar 2 poteza u opponent_history)
            if current_round == 3 and len(opponent_history) >= 2:
                if (opponent_history[0] == Move.DEFECT and 
                    opponent_history[1] == Move.DEFECT):
                    # Ako jeste, naredna 3 poteza (uključujući *ovu* rundu 3) izdajemo
                    # ali pazite, "ovu rundu 3" upravo sad igramo, pa:
                    self.force_defect_for_3 = 3  # stavi 3
                    self.force_defect_for_3 -= 1  # odmah trošimo 1 za ovu rundu
                    return Move.DEFECT
            
            # Ako nismo u prisilnoj 3-defekta fazi, sarađujemo
            return Move.COOPERATE
        
        # 3) Poslednjih 10 rundi => Uvek DEFECT
        if current_round > total_rounds - 10:
            return Move.DEFECT
        
        # 4) Provera da li je ova runda jedna od nasumično izabranih za defekt
        if current_round in self.forced_defect_rounds:
            # Bez obzira na sve, izdajemo
            return Move.DEFECT
        
        # 5) "Glavna" logika za ostale runde (6..190, osim prisilnih i nasumičnih defekta):
        #    Gledamo prethodna 3 poteza protivnika
        if len(opponent_history) < 3:
            # Iz predostrožnosti (mada realno bi trebalo da imamo >=3)
            return Move.COOPERATE
        
        last_3_moves = opponent_history[-3:]
        
        # Provera uslova:
        # a) Da li je poslednji potez COOPERATE?
        # b) Da li su bar 2 od ta 3 poteza COOPERATE?
        if (last_3_moves[-1] == Move.COOPERATE 
            and last_3_moves.count(Move.COOPERATE) >= 2):
            return Move.COOPERATE
        else:
            return Move.DEFECT