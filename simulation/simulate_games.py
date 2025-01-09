import importlib.util
from utils.abstract_bot import AbstractBot
from utils.moves import Move
from utils.game_config import GameConfig
from datetime import datetime
import os
import random

class PrisonersDilemmaSimulation:
    def __init__(self, bot1_path):
        self.bot1_path = bot1_path  # Store path instead of instance
        
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def load_bot(self, path):
        """Load a bot from a file path"""
        try:
            spec = importlib.util.spec_from_file_location("bot_module", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for item in dir(module):
                obj = getattr(module, item)
                if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                    return obj()
            raise ValueError("No valid bot class found in file")
        except Exception as e:
            raise Exception(f"Error loading bot from {path}: {e}")

    def calculate_score(self, move1: Move, move2: Move):
        """Calculate scores based on moves"""
        if move1 == Move.COOPERATE and move2 == Move.COOPERATE:
            return GameConfig.MUTUAL_COOPERATION_POINTS, GameConfig.MUTUAL_COOPERATION_POINTS
        elif move1 == Move.COOPERATE and move2 == Move.DEFECT:
            return GameConfig.BETRAYED_POINTS, GameConfig.BETRAYAL_POINTS
        elif move1 == Move.DEFECT and move2 == Move.COOPERATE:
            return GameConfig.BETRAYAL_POINTS, GameConfig.BETRAYED_POINTS
        else:  # both defect
            return GameConfig.MUTUAL_DEFECTION_POINTS, GameConfig.MUTUAL_DEFECTION_POINTS

    def run_games(self, opponent_paths, rounds=GameConfig.NUMBER_OF_ROUNDS):
        """Run games against multiple opponents."""
        # Create fresh instance of bot1
        self.bot1 = self.load_bot(self.bot1_path)
        
        timestamp = datetime.now().strftime("%H%M%S")
        games_dir = os.path.join(self.logs_dir, f"{timestamp}_{self.bot1.name}_games")
        os.makedirs(games_dir)

        all_stats = []
        for opponent_path in opponent_paths:
            # Load opponent bot
            opponent = self.load_bot(opponent_path)
            
            # Calculate number of rounds for this match
            match_rounds = rounds
            if GameConfig.ADD_NOISE:
                min_rounds = int(rounds * 0.8)
                max_rounds = int(rounds * 1.2)
                match_rounds = random.randint(min_rounds, max_rounds)

            match_stats = self._run_match(opponent, match_rounds, games_dir)
            all_stats.append({
                'opponent': opponent.name,
                'stats': match_stats
            })

        # Write summary of all games
        self._write_games_summary(games_dir, all_stats)
        print(f"Games complete. Results saved to {games_dir}")

    def _run_match(self, opponent, rounds, tournament_dir):
        # Reinitialize both bots for this match
        bot1 = self.load_bot(self.bot1_path)
        opponent_class = opponent.__class__
        opponent = opponent_class()

        stats = {
            'mutual_cooperation': 0,
            'mutual_defection': 0,
            'bot1_betrayals': 0,
            'opponent_betrayals': 0,
            'scores': {bot1.name: 0, opponent.name: 0}
        }

        timestamp = datetime.now().strftime("%H%M%S")
        log_filename = f"{timestamp}_vs_{opponent.name}.txt"
        log_path = os.path.join(tournament_dir, log_filename)

        output_lines = []
        output_lines.extend([
            "="*50,
            f"MATCH RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Bot 1: {bot1.name}",
            f"Bot 2: {opponent.name}",
            "="*50,
            "",
            "ROUND HISTORY:",
            f"{'Round':^6} | {'Bot 1':^10} | {'Bot 2':^10} | {'Round Result':^12} | {'Current Score':^12}",
            "-"*60
        ])

        for round_num in range(rounds):
            move1 = bot1.make_decision()  # Change strategy([]) to make_decision()
            move2 = opponent.make_decision()   # Change strategy([]) to make_decision()

            # Update histories for both bots
            bot1.my_history.append(move1)
            bot1.opponent_history.append(move2)
            opponent.my_history.append(move2)
            opponent.opponent_history.append(move1)

            # Calculate score and determine round result
            if move1 == Move.COOPERATE and move2 == Move.COOPERATE:
                round_result = f"{GameConfig.MUTUAL_COOPERATION_POINTS:^2} - {GameConfig.MUTUAL_COOPERATION_POINTS:^2}"
                score1, score2 = GameConfig.MUTUAL_COOPERATION_POINTS, GameConfig.MUTUAL_COOPERATION_POINTS
                stats['mutual_cooperation'] += 1
            elif move1 == Move.COOPERATE and move2 == Move.DEFECT:
                round_result = f"{GameConfig.BETRAYED_POINTS:^2} - {GameConfig.BETRAYAL_POINTS:^2}"
                score1, score2 = GameConfig.BETRAYED_POINTS, GameConfig.BETRAYAL_POINTS
                stats['opponent_betrayals'] += 1
            elif move1 == Move.DEFECT and move2 == Move.COOPERATE:
                round_result = f"{GameConfig.BETRAYAL_POINTS:^2} - {GameConfig.BETRAYED_POINTS:^2}"
                score1, score2 = GameConfig.BETRAYAL_POINTS, GameConfig.BETRAYED_POINTS
                stats['bot1_betrayals'] += 1
            else:  # Both defect
                round_result = f"{GameConfig.MUTUAL_DEFECTION_POINTS:^2} - {GameConfig.MUTUAL_DEFECTION_POINTS:^2}"
                score1, score2 = GameConfig.MUTUAL_DEFECTION_POINTS, GameConfig.MUTUAL_DEFECTION_POINTS
                stats['mutual_defection'] += 1

            stats['scores'][bot1.name] += score1
            stats['scores'][opponent.name] += score2

            current_score = f"{stats['scores'][bot1.name]:^5} - {stats['scores'][opponent.name]:^5}"
            output_lines.append(f"{round_num+1:^6} | {move1.name:^10} | {move2.name:^10} | {round_result:^12} | {current_score}")

        output_lines.extend([
            "\nMATCH STATISTICS:",
            "-"*50,
            f"Total Rounds: {rounds}",
            f"Mutual Cooperation: {stats['mutual_cooperation']} ({stats['mutual_cooperation']/rounds*100:.1f}%)",
            f"Mutual Defection: {stats['mutual_defection']} ({stats['mutual_defection']/rounds*100:.1f}%)",
            f"Bot 1 Betrayals: {stats['bot1_betrayals']} ({stats['bot1_betrayals']/rounds*100:.1f}%)",
            f"Opponent Betrayals: {stats['opponent_betrayals']} ({stats['opponent_betrayals']/rounds*100:.1f}%)",
            "",
            "FINAL SCORES:",
            "-"*50,
            f"{bot1.name}: {stats['scores'][bot1.name]}",
            f"{opponent.name}: {stats['scores'][opponent.name]}",
            "="*50
        ])

        with open(log_path, 'w') as log_file:
            log_file.write('\n'.join(output_lines))

        return stats

    def _write_games_summary(self, directory, all_stats):
        """Write a summary of all games played."""
        summary_path = os.path.join(directory, "games_summary.txt")
        with open(summary_path, 'w') as f:
            f.write("="*50 + "\n")
            f.write(f"MULTIPLE GAMES SUMMARY\n")
            f.write(f"Player: {self.bot1.name}\n")
            f.write("="*50 + "\n\n")

            for stat in all_stats:
                opponent = stat['opponent']
                stats = stat['stats']
                f.write(f"Against {opponent}:\n")
                f.write("-"*30 + "\n")
                f.write(f"Score: {stats['scores'][self.bot1.name]} - {stats['scores'][opponent]}\n")
                f.write(f"Mutual Cooperation: {stats['mutual_cooperation']}\n")
                f.write(f"Mutual Defection: {stats['mutual_defection']}\n")
                f.write(f"Times Betrayed: {stats['opponent_betrayals']}\n")
                f.write(f"Times Betrayed Opponent: {stats['bot1_betrayals']}\n\n")

            # Overall statistics
            f.write("\nOVERALL STATISTICS\n")
            f.write("-"*30 + "\n")
            total_games = len(all_stats)
            total_score = sum(s['stats']['scores'][self.bot1.name] for s in all_stats)
            total_opponent_score = sum(s['stats']['scores'][s['opponent']] for s in all_stats)
            avg_score = total_score / total_games
            avg_opponent_score = total_opponent_score / total_games
            f.write(f"Total Games: {total_games}\n")
            f.write(f"Total Score: {total_score} - {total_opponent_score}\n")
            f.write(f"Average Score: {avg_score:.1f} - {avg_opponent_score:.1f}\n")
