# Blokadni Turnir Strategija - Zatvorenikova dilema - Uputstvo za učesnike

Dobrodošli na blokadni turnir strategija! Ovaj dokument će vam pomoći da razumete pravila takmičenja i objasniti kako da kreirate svog bota koji će se takmičiti na turniru.

## O turniru

Zatvorenikova dilema je klasičan primer iz teorije igara gde dva igrača moraju da odluče da li će sarađivati ili izdati jedan drugog. Na ovom turniru, vaš zadatak je da napišete bota koji će igrati protiv drugih botova i pokušati da ostvari najbolji mogući rezultat.

### Pravila bodovanja

- Ako oba bota sarađuju: svaki dobija 4 poena
- Ako oba bota izdaju: svaki dobija 2 poen
- Ako jedan bot sarađuje a drugi izda:
  - Bot koji je izdao dobija 6 poena
  - Bot koji je sarađivao dobija 0 poena

**Važno**: Svaki bot će igrati tačno 200 rundi protiv svakog protivničkog bota. Pobednik turnira se određuje isključivo na osnovu ukupnog broja osvojenih poena kroz sve mečeve. Pobede i porazi u pojedinačnim mečevima nisu relevantni - jedino što je bitno je maksimizovanje ukupnog broja poena kroz sve runde i sve mečeve!


## Kako učestvovati

1. Klonirajte ovaj repozitorijum:
```bash
git clone https://github.com/yourusername/prisoners-dilemma-tournament.git
cd prisoners-dilemma-tournament
```

2. Zavisnosti (dependancies):

Simulator je napisan tako da koristi samo Python standardnu biblioteku, pa je potreban samo Python 3.8 ili novija verzija. U slučaju da imate stariju verziju ili nekih drugih problema, trebalo bi da je dovoljno:
```bash
pip install tk
```

## Kreiranje vašeg bota

Vaš bot treba da nasledi `AbstractBot` klasu. Evo primera implementacije koji koristi sve dostupne parametre za određivanje svoje strategije:

```python
from utils.abstract_bot import AbstractBot
from utils.moves import Move
from typing import List


class PametniBot(AbstractBot):
    @property
    def name(self) -> str:
        return "Bot za primer :)"
    
    @property
    def description(self) -> str:
        return "Bot koji koristi sve dostupne parametre za određivanje svoje strategije"
    
    def strategy(self, my_history: List[Move], opponent_history: List[Move], 
                current_round: int, total_rounds: int) -> Move:
        # Ako je prva runda, sarađujemo
        if current_round == 1:
            return Move.COOPERATE
            
        # Računamo koliko je protivnik do sada prosečno izdavao
        betrayals = sum(1 for move in opponent_history if move == Move.BETRAY)
        betrayal_rate = betrayals / len(opponent_history)
        
        # Ako smo u ranoj fazi meča (prvih 25% rundi)
        if current_round < total_rounds * 0.25:
            # Testiramo protivnika - igramo milo za drago
            return opponent_history[-1]
            
        # U središnjoj fazi (25-75% rundi)
        elif current_round < total_rounds * 0.75:
            # Ako protivnik često izdaje (>30%), uzvraćamo istom merom
            if betrayal_rate > 0.3:
                return Move.DEFECT
            # Ako je protivnik uglavnom fer, sarađujemo
            return Move.COOPERATE
            
        # U završnoj fazi (poslednjih 25% rundi)
        else:
            # Gledamo protivnikova poslednja 3 poteza
            recent_moves = opponent_history[-3:]
            # Ako je nedavno izdao, uzvraćamo
            if Move.BETRAY in recent_moves:
                return Move.DEFECT
            return Move.COOPERATE
```

### Postojeće strategije za inspiraciju

Možete proučiti nekoliko već implementiranih strategija:
- **Uvek Sarađuj**: Uvek bira saradnju
- **Uvek Izdaj**: Uvek bira izdaju
- **Milo za Drago (Tit for Tat)**: Kopira protivnikov prethodni potez
- **Nasumično**: Nasumično bira poteze
- **Osvetnik**: Sarađuje dok ne bude izdan, nakon toga uvek izdaje

## Testiranje vašeg bota

Testirajte svog bota pokretanjem simulatora:
```bash
python main.py
```

## Saveti za razvoj strategije

1. **Iskoristite sve dostupne informacije**: 
   - Proučite svoju i protivničku istoriju poteza (`my_history`, `opponent_history`)
   - Koristite informacije o trenutnoj rundi i ukupnom broju rundi za adaptaciju strategije
   
2. **Razmišljajte o ukupnom skoru**:
   - Cilj nije pobediti protivnika u pojedinačnom meču
   - Cilj je maksimizovati ukupan broj poena kroz sve mečeve
   - Ponekad je bolje "izgubiti više" u jednom meču ako to znači više poena u ukupnom zbiru

3. **Testirajte protiv različitih protivnika**: 
   - Vaš bot treba da bude efikasan protiv raznih strategija
   - Pojedinačna strategija koja dobro radi protiv jednog protivnika možda nije optimalna za ceo turnir

4. **Budite kreativni**: 
   - Ne postoji optimalna strategija
   - Eksperimentišite sa različitim pristupima
   - Razmislite o tome kako da iskoristite informaciju o trenutnoj rundi

## Pravila turnira

1. Svaki bot igra 200 rundi protiv svakog drugog bota
2. Ukupan broj poena kroz sve mečeve određuje pobednika
3. Botovi koji pokušavaju da "varaju" biće diskvalifikovani

Srećno takmičenje! 🎮
