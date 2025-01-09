from datetime import datetime
import os
from utils.abstract_bot import AbstractBot
from utils.moves import Move
from utils.game_config import GameConfig
import importlib.util
import random

class TournamentSimulation:
    def __init__(self):
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)

    def load_bot(self, bot_path):
        """Load a bot from a file path."""
        try:
            spec = importlib.util.spec_from_file_location("bot_module", bot_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for item in dir(module):
                obj = getattr(module, item)
                if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                    return obj()
            raise ValueError("No valid bot class found in file")
        except Exception as e:
            raise Exception(f"Failed to load bot: {str(e)}")

    def run_all_against_all(self, bot_paths, rounds=GameConfig.NUMBER_OF_ROUNDS, visualize=False):
        """Conduct a round-robin tournament where each bot plays against each other.
        
        If GameConfig.ADD_NOISE is True, the number of rounds per match will vary randomly
        between 80% and 120% of the specified rounds value.
        """
        timestamp = datetime.now().strftime("%H%M%S")
        tournament_dir = os.path.join(self.logs_dir, f"{timestamp}_tournament")
        os.makedirs(tournament_dir)

        # Track scores and statistics
        scores = {}
        matches_played = {}
        stats = {
            'mutual_cooperation': 0,
            'mutual_defection': 0,
            'betrayals': {}  # Will track betrayals per bot
        }

        # Calculate total rounds each bot should play
        num_opponents = len(bot_paths) - 1
        total_rounds_per_bot = num_opponents * rounds
        remaining_rounds = {bot_path: total_rounds_per_bot for bot_path in bot_paths}

        # Run matches between all pairs of bots
        for i, bot1_path in enumerate(bot_paths):
            bot1 = self.load_bot(bot1_path)
            stats['betrayals'][bot1.name] = 0
            
            for j, bot2_path in enumerate(bot_paths[i+1:], i+1):
                bot2 = self.load_bot(bot2_path)
                if j == i: continue  # Skip self-play
                
                if bot2.name not in stats['betrayals']:
                    stats['betrayals'][bot2.name] = 0

                # Initialize scores if needed
                for bot_name in [bot1.name, bot2.name]:
                    scores.setdefault(bot_name, 0)
                    matches_played.setdefault(bot_name, 0)

                # Calculate rounds for this match while maintaining total
                if GameConfig.ADD_NOISE:
                    min_rounds = int(rounds * 0.8)
                    max_rounds = int(rounds * 1.2)
                    
                    # Calculate remaining matches for both bots (including current match)
                    remaining_matches_bot1 = sum(1 for x in bot_paths[i+1:] if x != bot1_path)
                    remaining_matches_bot2 = sum(1 for x in bot_paths[i:] if x != bot2_path)
                    
                    # Ensure we have valid remaining matches counts
                    if remaining_matches_bot1 == 0 or remaining_matches_bot2 == 0:
                        match_rounds = remaining_rounds[bot1_path] if remaining_matches_bot1 == 0 else remaining_rounds[bot2_path]
                    else:
                        # Calculate average rounds needed per remaining match
                        avg_rounds_bot1 = remaining_rounds[bot1_path] // remaining_matches_bot1
                        avg_rounds_bot2 = remaining_rounds[bot2_path] // remaining_matches_bot2
                        
                        # Set bounds for this match
                        match_min = max(min_rounds, min(avg_rounds_bot1, avg_rounds_bot2))
                        match_max = min(max_rounds, 
                                      remaining_rounds[bot1_path],
                                      remaining_rounds[bot2_path])
                        
                        match_rounds = random.randint(match_min, max(match_min, match_max))
                else:
                    match_rounds = rounds

                # Update remaining rounds
                remaining_rounds[bot1_path] -= match_rounds
                remaining_rounds[bot2_path] -= match_rounds

                # Run match
                match_stats = self._run_match(bot1, bot2, match_rounds, tournament_dir)
                
                # Update scores and statistics
                scores[bot1.name] += match_stats['scores'][bot1.name]
                scores[bot2.name] += match_stats['scores'][bot2.name]
                matches_played[bot1.name] += 1
                matches_played[bot2.name] += 1
                
                stats['mutual_cooperation'] += match_stats['mutual_cooperation']
                stats['mutual_defection'] += match_stats['mutual_defection']
                stats['betrayals'][bot1.name] += match_stats['betrayals'][bot1.name]
                stats['betrayals'][bot2.name] += match_stats['betrayals'][bot2.name]

        # Verify all bots played their expected number of rounds
        for bot_path, remaining in remaining_rounds.items():
            if remaining != 0:
                print(f"Warning: {os.path.basename(bot_path)} has {remaining} unplayed rounds")

        # After matches are done and before writing summary
        bot_stats = []
        for bot_name in scores.keys():
            avg_score = scores[bot_name] / matches_played[bot_name]
            bot_stats.append((bot_name, avg_score))
        
        # Sort bots by average score
        bot_names = [bot[0] for bot in sorted(bot_stats, key=lambda x: x[1], reverse=True)]
        display_names = {name: name.replace(" Bot", "").strip() for name in bot_names}
        
        # Create score matrix
        score_matrix = {bot1: {bot2: 0 for bot2 in bot_names} for bot1 in bot_names}
        
        # Fill score matrix from match results
        for bot1 in bot_names:
            for bot2 in bot_names:
                if bot1 != bot2:
                    match_file = os.path.join(tournament_dir, f"{bot1}_vs_{bot2}.txt")
                    if os.path.exists(match_file):
                        with open(match_file, 'r') as mf:
                            for line in mf:
                                if line.startswith(f"{bot1}: "):
                                    score = int(line.split(": ")[1])
                                    score_matrix[bot1][bot2] = score
                    else:
                        match_file = os.path.join(tournament_dir, f"{bot2}_vs_{bot1}.txt")
                        if os.path.exists(match_file):
                            with open(match_file, 'r') as mf:
                                for line in mf:
                                    if line.startswith(f"{bot1}: "):
                                        score = int(line.split(": ")[1])
                                        score_matrix[bot1][bot2] = score
        
        # Write summary and export CSV
        self._write_tournament_summary(tournament_dir, scores, stats, matches_played, rounds, bot_names, display_names, score_matrix)
        self._export_score_matrix_csv(directory=tournament_dir, bot_names=bot_names, display_names=display_names, score_matrix=score_matrix)
        
        return tournament_dir

    def _run_match(self, bot1, bot2, rounds, tournament_dir):
        """Run a single match between two bots and return match statistics."""
        # Reinitialize bots for this match by creating new instances
        bot1_class = bot1.__class__
        bot2_class = bot2.__class__
        bot1 = bot1_class()
        bot2 = bot2_class()
        
        scores = {bot1.name: 0, bot2.name: 0}
        stats = {
            'mutual_cooperation': 0,
            'mutual_defection': 0,
            'betrayals': {bot1.name: 0, bot2.name: 0}
        }
        
        # Reset bot histories at start of match
        bot1.my_history = []
        bot1.opponent_history = []
        bot2.my_history = []
        bot2.opponent_history = []
        
        # Prepare output lines for detailed match history
        output_lines = [
            "="*50,
            f"MATCH RESULTS - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"Bot 1: {bot1.name}",
            f"Bot 2: {bot2.name}",
            "="*50,
            "",
            "ROUND HISTORY:",
            f"{'Round':^6} | {'Bot 1':^10} | {'Bot 2':^10} | {'Round Result':^12} | {'Current Score':^12}",
            "-"*60
        ]
        
        # Play rounds
        for round_num in range(rounds):
            # Get both moves before updating histories
            move1 = bot1.make_decision()
            move2 = bot2.make_decision()
            
            # Update histories for both bots after both moves are known
            bot1.opponent_history.append(move2)
            bot1.my_history.append(move1)
            bot2.opponent_history.append(move1)
            bot2.my_history.append(move2)
            
            # Calculate round result and update scores
            if move1 == Move.COOPERATE and move2 == Move.COOPERATE:
                round_result = f"{GameConfig.MUTUAL_COOPERATION_POINTS:^2} - {GameConfig.MUTUAL_COOPERATION_POINTS:^2}"
                scores[bot1.name] += GameConfig.MUTUAL_COOPERATION_POINTS
                scores[bot2.name] += GameConfig.MUTUAL_COOPERATION_POINTS
                stats['mutual_cooperation'] += 1
            elif move1 == Move.COOPERATE and move2 == Move.DEFECT:
                round_result = f"{GameConfig.BETRAYED_POINTS:^2} - {GameConfig.BETRAYAL_POINTS:^2}"
                scores[bot1.name] += GameConfig.BETRAYED_POINTS
                scores[bot2.name] += GameConfig.BETRAYAL_POINTS
                stats['betrayals'][bot2.name] += 1
            elif move1 == Move.DEFECT and move2 == Move.COOPERATE:
                round_result = f"{GameConfig.BETRAYAL_POINTS:^2} - {GameConfig.BETRAYED_POINTS:^2}"
                scores[bot1.name] += GameConfig.BETRAYAL_POINTS
                scores[bot2.name] += GameConfig.BETRAYED_POINTS
                stats['betrayals'][bot1.name] += 1
            else:  # Both defect
                round_result = f"{GameConfig.MUTUAL_DEFECTION_POINTS:^2} - {GameConfig.MUTUAL_DEFECTION_POINTS:^2}"
                scores[bot1.name] += GameConfig.MUTUAL_DEFECTION_POINTS
                scores[bot2.name] += GameConfig.MUTUAL_DEFECTION_POINTS
                stats['mutual_defection'] += 1
                
            current_score = f"{scores[bot1.name]:^5} - {scores[bot2.name]:^5}"
            output_lines.append(f"{round_num+1:^6} | {move1.name:^10} | {move2.name:^10} | {round_result:^12} | {current_score}")
        
        # Add final statistics
        output_lines.extend([
            "\nMATCH STATISTICS:",
            "-"*50,
            f"Total Rounds: {rounds}",
            f"Mutual Cooperation: {stats['mutual_cooperation']} ({stats['mutual_cooperation']/rounds*100:.1f}%)",
            f"Mutual Defection: {stats['mutual_defection']} ({stats['mutual_defection']/rounds*100:.1f}%)",
            f"Betrayals by {bot1.name}: {stats['betrayals'][bot1.name]} ({stats['betrayals'][bot1.name]/rounds*100:.1f}%)",
            f"Betrayals by {bot2.name}: {stats['betrayals'][bot2.name]} ({stats['betrayals'][bot2.name]/rounds*100:.1f}%)",
            "",
            "FINAL SCORES:",
            "-"*50,
            f"{bot1.name}: {scores[bot1.name]}",
            f"{bot2.name}: {scores[bot2.name]}",
            "="*50
        ])
        
        # Write match results to file
        match_file = os.path.join(tournament_dir, f"{bot1.name}_vs_{bot2.name}.txt")
        with open(match_file, 'w') as f:
            f.write('\n'.join(output_lines))
        
        return {
            'scores': scores,
            'mutual_cooperation': stats['mutual_cooperation'],
            'mutual_defection': stats['mutual_defection'],
            'betrayals': stats['betrayals']
        }

    def _write_tournament_summary(self, directory, scores, stats, matches_played, rounds_per_match, bot_names, display_names, score_matrix):
        def clean_name(name):
            if name == "Always Cooperate":
                return "Always C"
            elif name == "Always Defect":
                return "Always D"
            return display_names[name]

        summary_path = os.path.join(directory, "tournament_summary.txt")
        with open(summary_path, 'w') as f:
            f.write("="*50 + "\n")
            f.write("TOURNAMENT SUMMARY\n")
            f.write("="*50 + "\n\n")

            # Get unique bot names and calculate averages
            bot_stats = []
            for bot_name in scores.keys():
                avg_score = scores[bot_name] / matches_played[bot_name]
                bot_stats.append((bot_name, avg_score))
            
            # Sort bots by average score and clean names for display
            bot_names = [bot[0] for bot in sorted(bot_stats, key=lambda x: x[1], reverse=True)]
            display_names = {name: clean_name(name) for name in bot_names}
            
            # Calculate widths - need to account for "vs " prefix in header width
            name_width = max(len(name) for name in display_names.values())
            vs_width = max(len(f"vs {name}") for name in display_names.values())  # Width including "vs "
            score_width = max(vs_width, 5)  # Width for score columns
            
            # Create and fill score matrix
            score_matrix = {bot1: {bot2: 0 for bot2 in bot_names} for bot1 in bot_names}
            
            # Fill in score matrix from match results
            for bot1 in bot_names:
                for bot2 in bot_names:
                    if bot1 != bot2:
                        match_file = os.path.join(directory, f"{bot1}_vs_{bot2}.txt")
                        if os.path.exists(match_file):
                            with open(match_file, 'r') as mf:
                                for line in mf:
                                    if line.startswith(f"{bot1}: "):
                                        score = int(line.split(": ")[1])
                                        score_matrix[bot1][bot2] = score
                        else:
                            match_file = os.path.join(directory, f"{bot2}_vs_{bot1}.txt")
                            if os.path.exists(match_file):
                                with open(match_file, 'r') as mf:
                                    for line in mf:
                                        if line.startswith(f"{bot1}: "):
                                            score = int(line.split(": ")[1])
                                            score_matrix[bot1][bot2] = score

            # Write score matrix
            f.write("SCORE MATRIX\n")
            f.write("-"*50 + "\n\n")
            
            # Header row
            f.write("Bot".ljust(name_width))
            for bot in bot_names:
                f.write(f" | {f'vs {display_names[bot]}'.center(score_width)}")
            f.write(f" | {'Avg score'.center(score_width)}\n")
            
            # Separator line - adjust for new widths
            total_width = name_width + (len(bot_names) + 1) * (score_width + 3)
            f.write("-" * total_width + "\n")
            
            # Data rows - all cells use same width as headers
            for bot1 in bot_names:
                f.write(display_names[bot1].ljust(name_width))
                total_score = 0
                matches = 0
                
                for bot2 in bot_names:
                    if bot1 == bot2:
                        f.write(f" | {'---'.center(score_width)}")
                    else:
                        score = score_matrix[bot1][bot2]
                        f.write(f" | {str(score).center(score_width)}")
                        total_score += score
                        matches += 1
                
                # Average column uses same width
                avg_score = total_score / matches if matches > 0 else 0
                f.write(f" | {f'{avg_score:.1f}'.center(score_width)}\n")
            
            f.write("\n\n")

            # Write statistics
            f.write("AGGREGATE STATISTICS\n")
            f.write("-"*50 + "\n")
            total_matches = sum(matches_played.values()) // 2
            f.write(f"Total Matches: {total_matches}\n")
            f.write(f"Average Mutual Cooperation: {stats['mutual_cooperation']/total_matches:.1f} per match\n")
            f.write(f"Average Mutual Defection: {stats['mutual_defection']/total_matches:.1f} per match\n")
            f.write(f"Average Bot Betrayals: {sum(stats['betrayals'].values())/total_matches:.1f} per match\n")
        
        # After writing the tournament summary, export the CSV
        self._export_score_matrix_csv(directory, bot_names, display_names, score_matrix)

    def _export_score_matrix_csv(self, directory, bot_names, display_names, score_matrix):
        """Export the score matrix as a CSV file."""
        csv_path = os.path.join(directory, "results.csv")
        with open(csv_path, 'w') as f:
            # Write header row
            f.write("Bot," + ",".join([display_names[bot] for bot in bot_names]) + ",Average\n")
            
            # Write data rows using actual match scores
            for bot1 in bot_names:
                row = [display_names[bot1]]
                total_score = 0
                matches = 0
                
                for bot2 in bot_names:
                    if bot1 == bot2:
                        row.append("")  # Empty cell for self-play
                    else:
                        match_score = score_matrix[bot1][bot2]
                        row.append(str(match_score))
                        total_score += match_score
                        matches += 1
                
                # Calculate and append average
                avg_score = total_score / matches if matches > 0 else 0
                row.append(f"{avg_score:.1f}")
                
                f.write(",".join(row) + "\n")