import random
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np
import random
import math


class Ship:

    def __init__(self, size, row=None, col=None, orientation=None):
        self.size = size
        self.row = row if row is not None else random.randint(0, 9)
        self.col = col if col is not None else random.randint(0, 9)
        self.orientation = orientation if orientation is not None else random.choice(["h", "v"])
        self.indexes = self.compute_indexes()

    def compute_indexes(self):
        indexes = []
        if self.orientation == "h":
            for i in range(self.size):
                indexes.append(self.row * 10 + self.col + i)
        else:
            for i in range(self.size):
                indexes.append((self.row + i) * 10 + self.col)
        return indexes


def is_valid_placement(ship, other_ships):
    for other in other_ships:
        if set(ship.indexes).intersection(set(other.indexes)):
            return False
    return True


class Player:
    def __init__(self, use_ga=True):
        self.ships = []  # List of ships
        self.search = ["U" for _ in range(100)]  # Search grid: unknown ('U'), hit ('H'), sunk ('S'), miss ('M')
        self.corner_search = ["U" for _ in range(121)]  # Corner search (11x11)

        if use_ga:
            self.place_ships_with_ga()
        else:
            self.place_ships()
        self.update_indexes()  

    def valid_placement(self, ship):
        for idx in ship.indexes:
            if idx < 0 or idx >= 100:
                return False
            row, col = divmod(idx, 10)
            if ship.orientation == 'h' and (col + ship.size - 1) >= 10:
                return False
            if ship.orientation == 'v' and (row + ship.size - 1) >= 10:
                return False
        for s in self.ships:
            if set(ship.indexes).intersection(s.indexes):
                return False
        return True

    def place_ships(self):
        ship_sizes = [5, 4, 3, 3, 2]
        for size in ship_sizes:
            placed = False
            while not placed:
                orientation = random.choice(["h", "v"])
                if orientation == "h":
                    row = random.randint(0, 9)
                    col = random.randint(0, 10 - size)
                else:
                    row = random.randint(0, 10 - size)
                    col = random.randint(0, 9)

                new_ship = Ship(size=size, row=row, col=col, orientation=orientation)
                if self.valid_placement(new_ship):
                    self.ships.append(new_ship)
                    placed = True
        self.update_indexes()  

    def place_ships_with_ga(self):
        board_size = 10  
        ship_sizes = [5, 4, 3, 3, 2]  
        population_size = 30  
        generations = 150  
        mutation_rate = 0.05  

        ga = GeneticAlgorithm(population_size, mutation_rate, generations, board_size)
        best_placement = ga.evolve_population(
            ga.initialize_population(population_size, ship_sizes, board_size),
            generations, mutation_rate, board_size
        )
        if self.valid_placement_for_all(best_placement):
            print("GA produced valid placement")
            self.ships = [
                Ship(size=size, row=row, col=col, orientation=orientation)
                for (row, col, orientation, size) in best_placement
            ]
        else:
            print("GA produced invalid placement, using random placement instead.")
            self.place_ships()  
        self.update_indexes()

    def valid_placement_for_all(self, placement):
        occupied_positions = set()
        for row, col, orientation, size in placement:
            ship = Ship(size=size, row=row, col=col, orientation=orientation)

            
            if ship.orientation == 'h' and col + size > 10:
                print(f"Ship {ship} out of horizontal bounds.")
                return False
            if ship.orientation == 'v' and row + size > 10:
                print(f"Ship {ship} out of vertical bounds.")
                return False

            
            for idx in ship.indexes:
                if idx in occupied_positions:
                    print(f"Overlap detected for ship {ship} at index {idx}.")
                    return False
                occupied_positions.add(idx)
        return True

    def update_indexes(self):
        list_of_lists = [ship.indexes for ship in self.ships]
        self.indexes = [index for sublist in list_of_lists for index in sublist]

    def reset(self):
        self.ships = []
        self.search = ["U" for _ in range(100)]
        self.place_ships()
        self.update_indexes()

    def display_ship_placement(self):
        indexes = ["-" if i not in self.indexes else "X" for i in range(100)]
        for row in range(10):
            print(" ".join(indexes[(row) * 10:(row + 1) * 10]))


class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, generations, grid_size):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.grid_size = grid_size

    def initialize_population(self, pop_size, ship_sizes, board_size):
        population = []
        for _ in range(pop_size):
            placement = []
            for size in ship_sizes:
                valid = False
                while not valid:
                    orientation = random.choice(['h', 'v'])
                    if orientation == 'h':
                        row = random.randint(1, board_size - 2)
                        col = random.randint(1, board_size - size)
                    else:
                        row = random.randint(1, board_size - size)
                        col = random.randint(1, board_size - 2)
                    new_ship = (row, col, orientation, size)
                    if self.valid_ship_placement(placement, new_ship):
                        placement.append(new_ship)
                        valid = True
            population.append(placement)
        return population

    def valid_ship_placement(self, existing_placements, new_ship):
        
        if not isinstance(new_ship, tuple) or len(new_ship) != 4:
           
            return False

        row, col, orientation, size = new_ship
        ship_indexes = []
        if orientation == 'h':
            ship_indexes = [(row, col + k) for k in range(size)]
        elif orientation == 'v':
            ship_indexes = [(row + k, col) for k in range(size)]

        # Check if any index is out of bounds
        for r, c in ship_indexes:
            if r < 0 or r >= self.grid_size or c < 0 or c >= self.grid_size:
               
                return False

        # Ensure existing_placements contains only tuples of (row, col, orientation, size)
        for existing_ship in existing_placements:
            if not isinstance(existing_ship, tuple) or len(existing_ship) != 4:
               
                continue  # Skip invalid entries

            er, ec, e_orientation, e_size = existing_ship
            existing_indexes = []
            if e_orientation == 'h':
                existing_indexes = [(er, ec + k) for k in range(e_size)]
            elif e_orientation == 'v':
                existing_indexes = [(er + k, ec) for k in range(e_size)]

            if set(ship_indexes).intersection(existing_indexes):
                # print(f"Overlap detected with ship: {new_ship} and existing ship: {existing_ship}")
                return False

        return True

    def fitness(self, placement):
        total_distance = 0
        edge_penalty = 0
        corner_penalty = 0
        coverage_bonus = 0

        occupied_positions = set()

        for i in range(len(placement)):
            row, col, orientation, size = placement[i]

            ship_indexes = []
            if orientation == 'h':
                ship_indexes = [(row, col + k) for k in range(size)]
            elif orientation == 'v':
                ship_indexes = [(row + k, col) for k in range(size)]

            occupied_positions.update(ship_indexes)

            for (r, c) in ship_indexes:
                if r == 0 or r == self.grid_size - 1 or c == 0 or c == self.grid_size - 1:
                    edge_penalty += 1
                if (r == 0 and c == 0) or (r == 0 and c == self.grid_size - 1) or (
                        r == self.grid_size - 1 and c == 0) or (r == self.grid_size - 1 and c == self.grid_size - 1):
                    corner_penalty += 2

            for j in range(i + 1, len(placement)):
                other_row, other_col, other_orientation, other_size = placement[j]
                distance = abs(row - other_row) + abs(col - other_col)
                total_distance += distance

        unique_rows = {r for r, c in occupied_positions}
        unique_cols = {c for r, c in occupied_positions}
        coverage_bonus = len(unique_rows) + len(unique_cols)

        fitness_score = total_distance + coverage_bonus - (edge_penalty + corner_penalty)
        return fitness_score

    def select_parents(self, population, fitnesses):
        selected = random.choices(population, weights=fitnesses, k=2)
        return selected[0], selected[1]

    def crossover(self, parent1, parent2):
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]

        if not self.valid_placement_for_all(child1):
            print(f"Invalid child1 from crossover: {child1}")
        if not self.valid_placement_for_all(child2):
            print(f"Invalid child2 from crossover: {child2}")

        return child1, child2

    def mutate(self, individual, mutation_rate, board_size):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                valid = False
                while not valid:
                    orientation = random.choice(['h', 'v'])
                    if orientation == 'h':
                        row = random.randint(0, board_size - 1)
                        col = random.randint(0, board_size - individual[i][3])
                    else:
                        row = random.randint(0, board_size - individual[i][3])
                        col = random.randint(0, board_size - 1)
                    new_ship = (row, col, orientation, individual[i][3])
                    if self.valid_ship_placement(individual[:i] + individual[i + 1:], new_ship):
                        individual[i] = new_ship
                        valid = True
        return individual

    def evolve_population(self, population, generations, mutation_rate, board_size):
        for generation in range(generations):
            fitnesses = [self.fitness(ind) for ind in population]
            next_population = []
            for _ in range(len(population) // 2):
                parent1, parent2 = self.select_parents(population, fitnesses)
                child1, child2 = self.crossover(parent1, parent2)
                next_population.append(self.mutate(child1, mutation_rate, board_size))
                next_population.append(self.mutate(child2, mutation_rate, board_size))
            population = next_population

            for individual in population:
                if any(len(ship) != 4 for ship in individual):
                    print("Found an individual with incorrect structure:", individual)

        fitnesses = [self.fitness(ind) for ind in population]
        best_index = fitnesses.index(max(fitnesses))
        best_placement = population[best_index]

        if not self.valid_placement_for_all(best_placement):
            print("Best placement after GA is invalid:", best_placement)
        else:
            print("Best placement after GA is valid:", best_placement)

        return best_placement

    def valid_placement_for_all(self, placement):
        occupied_positions = set()
        for row, col, orientation, size in placement:
            ship = Ship(size=size, row=row, col=col, orientation=orientation)
            if not self.valid_ship_placement(occupied_positions, (row, col, orientation, size)):
                print(f"Invalid placement detected for ship {ship}")
                return False
            occupied_positions.update(ship.indexes)
        return True


class Game:
    def __init__(self, human1, human2, player1, player2):
        self.human1 = human1
        self.human2 = human2
        self.player1 = player1
        self.player2 = player2
        self.player1_turn = True
        self.computer_turn = not self.human1
        self.over = False
        self.result = None
        self.n_shots = 0
        self.in_sinking_mode = False
        self.hit_stack = []
        self.actual_misses = set()  # Track actual miss cells

    def place_ship(self, ship, player):
        if is_valid_placement(ship, player.ships):
            player.ships.append(ship)
            player.update_indexes()
            return True
        return False

    def make_move(self, i, is_corner_click=False):
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1
        if is_corner_click:
            return self.handle_corner_click(i, player, opponent)
        else:
            return self.handle_single_click(i, player, opponent)

    def handle_single_click(self, i, player, opponent):
        hit = False

        for ship in opponent.ships:
            if i in ship.indexes:
                player.search[i] = "H"
                hit = True
                sunk = True
                for idx in ship.indexes:
                    if player.search[idx] == "U":
                        sunk = False
                        break
                if sunk:
                    for idx in ship.indexes:
                        player.search[idx] = "S"
                    self.in_sinking_mode = False
                break

        if not hit:
            player.search[i] = "M"
            self.actual_misses.add(i)  # Track the actual miss

        game_over = True
        for ship in opponent.ships:
            if any(player.search[idx] == "U" for idx in ship.indexes):
                game_over = False
                break
        self.over = game_over
        if self.over:
            self.result = 1 if self.player1_turn else 2

        if not hit:
            self.player1_turn = not self.player1_turn
            if (self.human1 and not self.human2) or (not self.human1 and self.human2):
                self.computer_turn = not self.computer_turn
        self.n_shots += 1

        if not self.player1_turn:
            # print(player.search[i])
            if player.search[i] == 'H':
                return 1
            elif player.search[i] == 'S':
                return 2
        return None

    def handle_corner_click(self, corner_index, player, opponent):
        """Handle corner click that affects 4 adjacent grid cells"""
        # Get the 4 grid cells adjacent to this corner
        adjacent_cells = self.get_adjacent_grids_from_corner(corner_index)

        hits_detected = 0
        any_hit = False
        sunk_ships = []

        # Check each adjacent cell for hits
        for cell_index in adjacent_cells:
            cell_hit = False
            for ship in opponent.ships:
                if cell_index in ship.indexes:
                    # Mark as hit if it's unknown
                    if player.search[cell_index] == "U":
                        player.search[cell_index] = "H"
                        hits_detected += 1
                        any_hit = True
                        cell_hit = True

                    # Check if ship is sunk
                    sunk = True
                    for idx in ship.indexes:
                        if player.search[idx] == "U":
                            sunk = False
                            break
                    if sunk and ship not in sunk_ships:
                        sunk_ships.append(ship)
                        for idx in ship.indexes:
                            player.search[idx] = "S"
                        self.in_sinking_mode = False
                    break

            # Mark as miss if not hit and unknown
            if not cell_hit and player.search[cell_index] == "U":
                player.search[cell_index] = "M"
                self.actual_misses.add(cell_index)

        # Check game over condition
        game_over = True
        for ship in opponent.ships:
            if any(player.search[idx] == "U" for idx in ship.indexes):
                game_over = False
                break
        self.over = game_over
        if self.over:
            self.result = 1 if self.player1_turn else 2

        # Only switch turns if no hits were made in this corner click
        if not any_hit:
            self.player1_turn = not self.player1_turn
            if (self.human1 and not self.human2) or (not self.human1 and self.human2):
                self.computer_turn = not self.computer_turn

        self.n_shots += 1

        # Return results for GUI update
        if not self.player1_turn:
            return {
                'type': 'corner_click',
                'hits_detected': hits_detected,
                'sunk_ships': len(sunk_ships),
                'affected_cells': adjacent_cells
            }

            # Return results for GUI update
        return {
            'type': 'corner_click',
            'hits_detected': hits_detected,
            'sunk_ships': len(sunk_ships),
            'affected_cells': adjacent_cells,
            'player_turn': self.player1_turn  # Add this to identify whose turn it was
        }

    def get_adjacent_grids_from_corner(self, corner_index):
        """
        Convert corner index to the 4 adjacent grid cells
        For a 10x10 grid, corners are numbered 0-120 (11x11 corners)
        Each corner affects the 4 surrounding grid cells
        """
        # Calculate corner position in 11x11 grid
        corner_row = corner_index // 11
        corner_col = corner_index % 11

        adjacent_cells = []

        # Get the 4 grid cells surrounding this corner
        # Top-left cell (if valid)
        if corner_row > 0 and corner_col > 0:
            cell_index = (corner_row - 1) * 10 + (corner_col - 1)
            if cell_index < 100:  # Ensure within 10x10 grid
                adjacent_cells.append(cell_index)

        # Top-right cell (if valid)
        if corner_row > 0 and corner_col < 10:
            cell_index = (corner_row - 1) * 10 + corner_col
            if cell_index < 100:
                adjacent_cells.append(cell_index)

        # Bottom-left cell (if valid)
        if corner_row < 10 and corner_col > 0:
            cell_index = corner_row * 10 + (corner_col - 1)
            if cell_index < 100:
                adjacent_cells.append(cell_index)

        # Bottom-right cell (if valid)
        if corner_row < 10 and corner_col < 10:
            cell_index = corner_row * 10 + corner_col
            if cell_index < 100:
                adjacent_cells.append(cell_index)

        return adjacent_cells

    def random_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search

        # Sometimes use corner clicks (25% chance)
        if random.random() < 0.25:
            corners = [i for i in range(121)]  # 0-120 corners
            random_corner = random.choice(corners)
            return self.make_move(random_corner, is_corner_click=True)
        else:
            unknown = [i for i, square in enumerate(search) if square == "U" and i not in self.actual_misses]
            if unknown:
                random_index = random.choice(unknown)
                return self.make_move(random_index, is_corner_click=False)

    def basic_ai(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # First, check if we should use corner click (strategic decision)
        should_use_corner = self.should_basic_ai_use_corner(search, hits, unknown)
        if should_use_corner:
            best_corner = self.find_best_corner_for_basic_ai(search, hits, unknown)
            if best_corner is not None:
                result = self.make_move(best_corner, is_corner_click=True)
                return result

        # Original targeting logic for single cells
        unknown_with_neighbouring_hits1 = []
        unknown_with_neighbouring_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbouring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                unknown_with_neighbouring_hits2.append(u)

        for u in unknown:
            if u in unknown_with_neighbouring_hits1 and u in unknown_with_neighbouring_hits2:
                num = self.make_move(u, is_corner_click=False)
                return num

        if unknown_with_neighbouring_hits1:
            num = self.make_move(random.choice(unknown_with_neighbouring_hits1), is_corner_click=False)
            return num

        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if checker_board:
            num = self.make_move(random.choice(checker_board), is_corner_click=False)
            return num

        # Fallback to random AI (which can also use corners)
        return self.random_ai()

    def should_basic_ai_use_corner(self, search, hits, unknown):
        """
        Determine when basic AI should use corner clicks
        """
        # Use corner clicks strategically:

        # 1. Early game exploration (first 20 shots)
        total_shots = 100 - len(unknown)  # Shots taken so far
        if total_shots < 20:
            return random.random() < 0.2  # 20% chance in early game

        # 2. When we have multiple isolated hits that could be different ships
        if len(hits) >= 2:
            # Check if hits are isolated (not adjacent)
            isolated_hits = 0
            for hit in hits:
                neighbors = [hit + 1, hit - 1, hit + 10, hit - 10]
                if not any(n in hits for n in neighbors if 0 <= n < 100):
                    isolated_hits += 1
            if isolated_hits >= 2:
                return random.random() < 0.4  # 40% chance with isolated hits

        # 3. When we need to explore large unknown areas
        large_unknown_areas = self.detect_large_unknown_areas(search)
        if large_unknown_areas:
            return random.random() < 0.3

        return False

    def find_best_corner_for_basic_ai(self, search, hits, unknown):
        
       # Find the best corner for basic AI to click based on current game state
        
        best_corner = None
        best_score = -1

        for corner in range(121):  # All possible corners (0-120)
            score = self.score_corner_for_basic_ai(corner, search, hits, unknown)
            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner if best_score > 0 else None

    def score_corner_for_basic_ai(self, corner, search, hits, unknown):
       
       # Score a corner based on strategic value for basic AI
       
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        score = 0

        # Base score: number of unknown cells in the area
        unknown_count = sum(1 for cell in adjacent_cells if cell in unknown)
        score += unknown_count * 5

        # Bonus: if corner covers areas near hits (for ship hunting)
        for cell in adjacent_cells:
            if cell in unknown:
                # Check if this cell is adjacent to hits
                neighbors = [cell + 1, cell - 1, cell + 10, cell - 10]
                if any(n in hits for n in neighbors if 0 <= n < 100):
                    score += 10

                # Extra bonus for cells that could complete ship patterns
                if any(n in hits for n in [cell + 2, cell - 2, cell + 20, cell - 20] if 0 <= n < 100):
                    score += 15

        # Penalty: if corner would hit too many already-missed cells
        miss_count = sum(1 for cell in adjacent_cells if search[cell] == "M")
        score -= miss_count * 8

        # Penalty: if corner would hit cells adjacent to many misses (wasted potential)
        for cell in adjacent_cells:
            if cell in unknown:
                cell_neighbors = [cell + 1, cell - 1, cell + 10, cell - 10]
                neighbor_misses = sum(1 for n in cell_neighbors if n in self.actual_misses)
                score -= neighbor_misses * 3

        # Bonus: strategic corner positions (center-focused)
        corner_row = corner // 11
        corner_col = corner % 11
        distance_from_center = abs(corner_row - 5) + abs(corner_col - 5)
        center_bonus = (10 - distance_from_center) * 2
        score += center_bonus

        return score

    def detect_large_unknown_areas(self, search):
        """
        Detect if there are large contiguous areas of unknown cells
        """
        visited = set()
        large_areas = []

        for cell in range(100):
            if search[cell] == "U" and cell not in visited:
                # BFS to find contiguous unknown area
                area_size = 0
                queue = [cell]
                visited.add(cell)

                while queue:
                    current = queue.pop(0)
                    area_size += 1

                    # Check neighbors
                    for neighbor in [current + 1, current - 1, current + 10, current - 10]:
                        if (0 <= neighbor < 100 and
                                search[neighbor] == "U" and
                                neighbor not in visited):
                            visited.add(neighbor)
                            queue.append(neighbor)

                if area_size >= 6:  # Consider 6+ cells as a large area
                    large_areas.append(area_size)

        return len(large_areas) > 0

    def fuzzy_search(self, search_grid, use_corners=False):
        # Define fuzzy variables for single cell evaluation
        hits = ctrl.Antecedent(np.arange(0, 5, 1), 'hits')
        unknowns = ctrl.Antecedent(np.arange(0, 5, 1), 'unknowns')
        probability = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'probability')

        # Membership functions
        hits['low'] = fuzz.trimf(hits.universe, [0, 0, 2])
        hits['medium'] = fuzz.trimf(hits.universe, [1, 2, 3])
        hits['high'] = fuzz.trimf(hits.universe, [2, 4, 4])

        unknowns['low'] = fuzz.trimf(unknowns.universe, [0, 0, 2])
        unknowns['medium'] = fuzz.trimf(unknowns.universe, [1, 2, 3])
        unknowns['high'] = fuzz.trimf(unknowns.universe, [2, 4, 4])

        probability['low'] = fuzz.trimf(probability.universe, [0, 0, 0.5])
        probability['medium'] = fuzz.trimf(probability.universe, [0.3, 0.5, 0.7])
        probability['high'] = fuzz.trimf(probability.universe, [0.5, 1, 1])

        # Define rules
        rule1 = ctrl.Rule(hits['low'] & unknowns['high'], probability['medium'])  # Exploratory, moderate chance
        rule2 = ctrl.Rule(hits['low'] & unknowns['medium'], probability['low'])  # Less likely, less unknowns
        rule3 = ctrl.Rule(hits['low'] & unknowns['low'], probability['low'])  # Unlikely, few unknowns and hits

        rule4 = ctrl.Rule(hits['medium'] & unknowns['high'],
                          probability['high'])  # Good chance, could be part of a ship
        rule5 = ctrl.Rule(hits['medium'] & unknowns['medium'], probability['medium'])  # Possible, but less unknowns
        rule6 = ctrl.Rule(hits['medium'] & unknowns['low'], probability['low'])  # Unlikely, explored area

        rule7 = ctrl.Rule(hits['high'] & unknowns['high'],
                          probability['high'])  # Very likely, possible ship continuation
        rule8 = ctrl.Rule(hits['high'] & unknowns['medium'], probability['high'])  # Likely, possible ship
        rule9 = ctrl.Rule(hits['high'] & unknowns['low'], probability['medium'])  # Lower chance, but still possible

        # Control system creation
        probability_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
        probability_simulation = ctrl.ControlSystemSimulation(probability_ctrl)

        if use_corners:
            return self.fuzzy_corner_search(search_grid, probability_simulation)
        else:
            return self.fuzzy_single_cell_search(search_grid, probability_simulation)

    def fuzzy_search(self, search_grid, use_corners=False):
        # Define fuzzy variables for single cell evaluation
        hits = ctrl.Antecedent(np.arange(0, 5, 1), 'hits')
        unknowns = ctrl.Antecedent(np.arange(0, 5, 1), 'unknowns')
        probability = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'probability')

        # Membership functions
        hits['low'] = fuzz.trimf(hits.universe, [0, 0, 2])
        hits['medium'] = fuzz.trimf(hits.universe, [1, 2, 3])
        hits['high'] = fuzz.trimf(hits.universe, [2, 4, 4])

        unknowns['low'] = fuzz.trimf(unknowns.universe, [0, 0, 2])
        unknowns['medium'] = fuzz.trimf(unknowns.universe, [1, 2, 3])
        unknowns['high'] = fuzz.trimf(unknowns.universe, [2, 4, 4])

        probability['low'] = fuzz.trimf(probability.universe, [0, 0, 0.5])
        probability['medium'] = fuzz.trimf(probability.universe, [0.3, 0.5, 0.7])
        probability['high'] = fuzz.trimf(probability.universe, [0.5, 1, 1])

        # Define rules
        rule1 = ctrl.Rule(hits['low'] & unknowns['high'], probability['medium'])  # Exploratory, moderate chance
        rule2 = ctrl.Rule(hits['low'] & unknowns['medium'], probability['low'])  # Less likely, less unknowns
        rule3 = ctrl.Rule(hits['low'] & unknowns['low'], probability['low'])  # Unlikely, few unknowns and hits

        rule4 = ctrl.Rule(hits['medium'] & unknowns['high'],
                          probability['high'])  # Good chance, could be part of a ship
        rule5 = ctrl.Rule(hits['medium'] & unknowns['medium'], probability['medium'])  # Possible, but less unknowns
        rule6 = ctrl.Rule(hits['medium'] & unknowns['low'], probability['low'])  # Unlikely, explored area

        rule7 = ctrl.Rule(hits['high'] & unknowns['high'],
                          probability['high'])  # Very likely, possible ship continuation
        rule8 = ctrl.Rule(hits['high'] & unknowns['medium'], probability['high'])  # Likely, possible ship
        rule9 = ctrl.Rule(hits['high'] & unknowns['low'], probability['medium'])  # Lower chance, but still possible

        # Control system creation
        probability_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
        probability_simulation = ctrl.ControlSystemSimulation(probability_ctrl)

        if use_corners:
            return self.fuzzy_corner_search(search_grid, probability_simulation)
        else:
            return self.fuzzy_single_cell_search(search_grid, probability_simulation)

    def fuzzy_single_cell_search(self, search_grid, probability_simulation):
        """Original single cell fuzzy search"""
        max_probability = 0
        best_index = None

        # Evaluate each unknown cell
        for i, state in enumerate(search_grid):
            if state == 'U':
                neighboring_hits = 0
                neighboring_unknowns = 0

                for offset in [-1, 1, -10, 10]:  # Check immediate neighbors
                    neighbor_index = i + offset
                    if 0 <= neighbor_index < len(search_grid):
                        if search_grid[neighbor_index] == 'H':
                            neighboring_hits += 1
                        elif search_grid[neighbor_index] == 'U':
                            neighboring_unknowns += 1

                probability_simulation.input['hits'] = neighboring_hits
                probability_simulation.input['unknowns'] = neighboring_unknowns
                probability_simulation.compute()

                prob = probability_simulation.output['probability']
                if prob > max_probability:
                    max_probability = prob
                    best_index = i

        return best_index

    def basic_ai_with_fuzzy(self):
        search = self.player1.search if self.player1_turn else self.player2.search
        hits = [i for i, square in enumerate(search) if square == "H"]
        unknown = [i for i, square in enumerate(search) if square == "U"]

        # Strategic decision: when to use corner clicks
        should_use_corner = self.should_fuzzy_ai_use_corner(search, hits, unknown)

        if should_use_corner:
            best_corner = self.find_fuzzy_corner(search, hits, unknown)
            if best_corner is not None:
                result = self.make_move(best_corner, is_corner_click=True)
                return result

        # If there are no hits yet, use fuzzy logic to find the first target
        if not hits:
            index = self.fuzzy_search(search, use_corners=False)
            if index is not None:
                num = self.make_move(index, is_corner_click=False)
                return num

        # Enhanced targeting with fuzzy logic for single cells
        return self.enhanced_targeting_with_fuzzy(search, hits, unknown)

    def should_fuzzy_ai_use_corner(self, search, hits, unknown):
        """
        Enhanced decision logic for when fuzzy AI should use corner clicks
        """
        total_unknown = len(unknown)
        total_hits = len(hits)

        # Early game: use corners for exploration
        if total_unknown > 80:  # First 20 shots
            return random.random() < 0.25  # 25% chance

        # When we have isolated hits that might be different ships
        if total_hits >= 2:
            isolated_hits = self.count_isolated_hits(hits)
            if isolated_hits >= 2:
                return random.random() < 0.4

        # When fuzzy logic suggests good corner opportunities
        fuzzy_corner_score = self.calculate_fuzzy_corner_opportunity(search, hits, unknown)
        if fuzzy_corner_score > 0.6:
            return True

        # When there are large unexplored areas
        large_areas = self.detect_large_unknown_areas(search)
        if large_areas and random.random() < 0.3:
            return True

        return False

    def find_fuzzy_corner(self, search, hits, unknown):
        """
        Find the best corner using fuzzy-enhanced evaluation
        """
        best_corner = None
        best_score = -1

        for corner in range(121):  # All possible corners
            score = self.fuzzy_corner_evaluation(corner, search, hits, unknown)
            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner if best_score > 0 else None

    def fuzzy_corner_evaluation(self, corner, search, hits, unknown):
        """
        Enhanced corner evaluation using fuzzy logic principles
        """
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        if not adjacent_cells:
            return -1

        # Calculate basic metrics
        unknown_count = sum(1 for cell in adjacent_cells if cell in unknown)
        hit_count = sum(1 for cell in adjacent_cells if cell in hits)
        miss_count = sum(1 for cell in adjacent_cells if search[cell] == "M")

        # Base score from unknown cells
        score = unknown_count * 3

        # Fuzzy-like scoring for hit proximity
        proximity_bonus = 0
        for cell in adjacent_cells:
            if cell in unknown:
                # Check immediate neighbors for hits
                for offset in [-1, 1, -10, 10]:
                    neighbor = cell + offset
                    if 0 <= neighbor < 100 and neighbor in hits:
                        proximity_bonus += 2

                # Check two steps away for hits (ship alignment)
                for offset in [-2, 2, -20, 20]:
                    neighbor = cell + offset
                    if 0 <= neighbor < 100 and neighbor in hits:
                        proximity_bonus += 1

        score += proximity_bonus

        # Penalty for misses
        score -= miss_count * 4

        # Strategic positioning bonus
        corner_row = corner // 11
        corner_col = corner % 11
        center_bonus = 10 - (abs(corner_row - 5) + abs(corner_col - 5))
        score += center_bonus * 0.5

        # Bonus for covering checkerboard pattern
        checkerboard_bonus = 0
        for cell in adjacent_cells:
            row = cell // 10
            col = cell % 10
            if (row + col) % 2 == 0:
                checkerboard_bonus += 1
        score += checkerboard_bonus * 0.3

        return max(score, 0)

    def enhanced_targeting_with_fuzzy(self, search, hits, unknown):
        """
        Enhanced targeting that combines basic AI logic with fuzzy evaluation
        """
        # First priority: cells with multiple hit indications (your original logic)
        unknown_with_neighbouring_hits1 = []
        unknown_with_neighbouring_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbouring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                unknown_with_neighbouring_hits2.append(u)

        # Priority 1: Cells with both immediate and extended hit neighbors
        high_priority_targets = []
        for u in unknown:
            if u in unknown_with_neighbouring_hits1 and u in unknown_with_neighbouring_hits2:
                high_priority_targets.append(u)

        if high_priority_targets:
            # Use fuzzy logic to choose the best high-priority target
            best_target = self.fuzzy_choose_best_target(high_priority_targets, search)
            num = self.make_move(best_target, is_corner_click=False)
            return num

        # Priority 2: Cells with immediate hit neighbors
        if unknown_with_neighbouring_hits1:
            # Use fuzzy logic to choose the best target
            best_target = self.fuzzy_choose_best_target(unknown_with_neighbouring_hits1, search)
            num = self.make_move(best_target, is_corner_click=False)
            return num

        # Priority 3: Checkerboard pattern with fuzzy enhancement
        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)

        if checker_board:
            # Use fuzzy logic to choose the best checkerboard cell
            best_target = self.fuzzy_choose_best_target(checker_board, search)
            num = self.make_move(best_target, is_corner_click=False)
            return num

        # Final fallback: random AI with corner capability
        return self.enhanced_random_ai()

    def fuzzy_choose_best_target(self, candidate_cells, search):
        """
        Use fuzzy logic to choose the best target from candidate cells
        """
        if not candidate_cells:
            return random.choice(candidate_cells) if candidate_cells else None

        best_cell = None
        best_score = -1

        for cell in candidate_cells:
            score = self.fuzzy_cell_evaluation(cell, search)
            if score > best_score:
                best_score = score
                best_cell = cell

        return best_cell if best_cell is not None else random.choice(candidate_cells)

    def fuzzy_cell_evaluation(self, cell, search):
        """
        Evaluate a single cell using fuzzy-like scoring
        """
        score = 0

        # Count unknown neighbors (exploration potential)
        unknown_neighbors = 0
        for offset in [-1, 1, -10, 10]:
            neighbor = cell + offset
            if 0 <= neighbor < 100 and search[neighbor] == "U":
                unknown_neighbors += 1
        score += unknown_neighbors * 2

        # Bonus for hit neighbors (targeting)
        hit_neighbors = 0
        for offset in [-1, 1, -10, 10]:
            neighbor = cell + offset
            if 0 <= neighbor < 100 and search[neighbor] == "H":
                hit_neighbors += 3  # Higher weight for hits
        score += hit_neighbors

        # Penalty for miss neighbors
        miss_neighbors = 0
        for offset in [-1, 1, -10, 10]:
            neighbor = cell + offset
            if 0 <= neighbor < 100 and search[neighbor] == "M":
                miss_neighbors += 1
        score -= miss_neighbors * 1.5

        # Strategic positioning
        row = cell // 10
        col = cell % 10
        center_bonus = 8 - (abs(row - 4.5) + abs(col - 4.5))
        score += center_bonus * 0.3

        return max(score, 0)

    def calculate_fuzzy_corner_opportunity(self, search, hits, unknown):
        """
        Calculate fuzzy score for corner opportunity
        """
        if not unknown:
            return 0

        opportunity_score = 0

        # Factor 1: Game phase (more opportunity early)
        game_phase = len(unknown) / 100  # 1.0 = early, 0.0 = late
        opportunity_score += game_phase * 0.4

        # Factor 2: Hit distribution
        if hits:
            isolated_hits = self.count_isolated_hits(hits)
            hit_distribution = isolated_hits / len(hits) if hits else 0
            opportunity_score += hit_distribution * 0.3

        # Factor 3: Unexplored area size
        large_areas_count = self.detect_large_unknown_areas(search)

        area_factor = min(large_areas_count * 0.2, 0.3)
        opportunity_score += area_factor

        return min(opportunity_score, 1.0)

    def count_isolated_hits(self, hits):
        """
        Count hits that don't have adjacent hits (potential different ships)
        """
        isolated_count = 0
        for hit in hits:
            is_isolated = True
            for offset in [-1, 1, -10, 10]:
                neighbor = hit + offset
                if neighbor in hits:
                    is_isolated = False
                    break
            if is_isolated:
                isolated_count += 1
        return isolated_count

    def enhanced_random_ai(self):
        """
        Random AI that can also use corner clicks occasionally
        """
        search = self.player1.search if self.player1_turn else self.player2.search

        # 20% chance to use corner click in random mode
        if random.random() < 0.2:
            corners = [i for i in range(121)]
            random_corner = random.choice(corners)
            result = self.make_move(random_corner, is_corner_click=True)
            return result
        else:
            unknown = [i for i, square in enumerate(search) if square == "U" and i not in self.actual_misses]
            if unknown:
                random_index = random.choice(unknown)
                result = self.make_move(random_index, is_corner_click=False)
                return result

        return None

    def basic_ai_MM1(self):
        print("Entering basic_ai_MM")
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # Check if we should use corner click in sinking mode
        if self.in_sinking_mode and len(hits) >= 2:
            # When in sinking mode with multiple hits, consider corner click to find ship orientation
            best_corner = self.find_sinking_mode_corner(search, hits, unknown)
            if best_corner is not None:
                result = self.make_move(best_corner, is_corner_click=True)
                print(f"Trying corner move {best_corner}, result: {result}")
                if isinstance(result, dict) and result.get('hits_detected', 0) > 0:
                    print(f"Corner hit detected {result['hits_detected']} ships, staying in sinking mode")
                    self.in_sinking_mode = True
                    return result
                elif isinstance(result, dict) and result.get('sunk_ships', 0) > 0:
                    print(f"Corner sunk {result['sunk_ships']} ships, resetting sinking mode")
                    self.in_sinking_mode = False
                    return result

        unknown_with_neighbouring_hits1 = []
        unknown_with_neighbouring_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbouring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                unknown_with_neighbouring_hits2.append(u)

        for u in unknown:
            if u in unknown_with_neighbouring_hits1 and u in unknown_with_neighbouring_hits2:
                num = self.make_move(u, is_corner_click=False)
                print(f"Trying move {u}, result: {num}")
                if self.player1.search[u] == "H" and not self.is_ship_sunk(u):
                    print(f"Hit without sink at {u}, staying in sinking mode")
                    self.in_sinking_mode = True
                    return num
                elif self.player1.search[u] == "S":
                    print(f"Ship sunk at {u}, resetting sinking mode")
                    self.in_sinking_mode = False

        if unknown_with_neighbouring_hits1:
            num = self.make_move(random.choice(unknown_with_neighbouring_hits1), is_corner_click=False)
            print(f"Trying move {num} from neighbouring hits 1, result: {num}")
            if self.player1.search[num] == "H" and not self.is_ship_sunk(num):
                print(f"Hit without sink at {num}, staying in sinking mode")
                self.in_sinking_mode = True
                return num
            elif self.player1.search[num] == "S":
                print(f"Ship sunk at {num}, resetting sinking mode")
                self.in_sinking_mode = False

        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if checker_board:
            num = self.make_move(random.choice(checker_board), is_corner_click=False)
            print(f"Trying move {num} from checkerboard, result: {num}")
            if self.player1.search[num] == "H" and not self.is_ship_sunk(num):
                print(f"Hit without sink at {num}, staying in sinking mode")
                self.in_sinking_mode = True
                return num
            elif self.player1.search[num] == "S":
                print(f"Ship sunk at {num}, resetting sinking mode")
                self.in_sinking_mode = False

        # Reset sinking mode if no appropriate moves are found
        print("No appropriate moves found, resetting sinking mode and switching to minmax_ai")
        self.in_sinking_mode = False
        return self.minmax_ai()  # Switch to MinMax AI if no hits are found

    def basic_ai_MM(self):
        print("Entering basic_ai_MM")
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # Strategic corner decision for MM algorithm
        should_use_corner = self.should_mm_use_corner(search, hits, unknown)
        if should_use_corner:
            best_corner = self.find_mm_corner(search, hits, unknown)
            if best_corner is not None:
                result = self.make_move(best_corner, is_corner_click=True)
                print(f"Trying strategic corner move {best_corner}, result: {result}")
                if isinstance(result, dict):
                    if result.get('hits_detected', 0) > 0:
                        print(f"Corner hit {result['hits_detected']} cells, entering sinking mode")
                        self.in_sinking_mode = True
                    if result.get('sunk_ships', 0) > 0:
                        print(f"Corner sunk {result['sunk_ships']} ships")
                        self.in_sinking_mode = False
                    return result

        # Check if there are any hits that are not part of sunk ships
        unsunk_hits_exist = False
        for hit in hits:
            if not self.is_ship_sunk(hit):
                unsunk_hits_exist = True
                self.in_sinking_mode = True
                break

        if not unsunk_hits_exist:
            self.in_sinking_mode = False

        unknown_with_neighbouring_hits1 = []
        unknown_with_neighbouring_hits2 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbouring_hits1.append(u)
            if u + 2 in hits or u - 2 in hits or u + 20 in hits or u - 20 in hits:
                unknown_with_neighbouring_hits2.append(u)

        # Priority 1: High confidence targets (both immediate and extended neighbors)
        for u in unknown:
            if u in unknown_with_neighbouring_hits1 and u in unknown_with_neighbouring_hits2:
                num = self.make_move(u, is_corner_click=False)
                print(f"Trying move {u}, result: {num}")
                if not self.is_ship_sunk(u):
                    print(f"Hit without sink at {u}, staying in sinking mode")
                    self.in_sinking_mode = True
                    return num
                else:
                    print(f"Ship sunk at {u}, resetting sinking mode")
                    self.in_sinking_mode = False
                    return num

        # Priority 2: Immediate hit neighbors
        if unknown_with_neighbouring_hits1:
            # Use intelligent selection instead of random
            best_target = self.select_best_mm_target(unknown_with_neighbouring_hits1, search, hits)
            num = self.make_move(best_target, is_corner_click=False)
            print(f"Trying move {num} from neighbouring hits 1, result: {num}")
            if not self.is_ship_sunk(num):
                print(f"Hit without sink at {num}, staying in sinking mode")
                self.in_sinking_mode = True
                return num
            else:
                print(f"Ship sunk at {num}, resetting sinking mode")
                self.in_sinking_mode = False
                return num

        # Priority 3: Checkerboard pattern
        checker_board = []
        for u in unknown:
            row = u // 10
            col = u % 10
            if (row + col) % 2 == 0:
                checker_board.append(u)
        if checker_board:
            best_target = self.select_best_mm_target(checker_board, search, hits)
            num = self.make_move(best_target, is_corner_click=False)
            print(f"Trying move {num} from checkerboard, result: {num}")
            if not self.is_ship_sunk(num):
                print(f"Hit without sink at {num}, staying in sinking mode")
                self.in_sinking_mode = True
                return num
            else:
                print(f"Ship sunk at {num}, resetting sinking mode")
                self.in_sinking_mode = False
                return num

        # Before switching to minmax_ai, check if there are any unsunk hits
        for hit in hits:
            if not self.is_ship_sunk(hit):
                print(f"Unresolved hit at {hit}, staying in basic_ai_MM")
                self.in_sinking_mode = True

                # Try a strategic corner click to resolve stuck situation
                rescue_corner = self.find_rescue_corner(hit, search, unknown)
                if rescue_corner is not None:
                    result = self.make_move(rescue_corner, is_corner_click=True)
                    print(f"Trying rescue corner {rescue_corner} for hit {hit}, result: {result}")
                    return result

                return self.basic_ai_MM()  # Continue in basic_ai_MM if there are unsunk hits

        # Reset sinking mode if no appropriate moves are found
        print("No appropriate moves found, resetting sinking mode and switching to minmax_ai")
        self.in_sinking_mode = False
        return self.minmax_ai()  # Switch to MinMax AI if no hits are found

    def should_mm_use_corner(self, search, hits, unknown):
        """
        Decision logic for when MinMax-enhanced AI should use corner clicks
        """
        # Calculate unknown_with_neighbouring_hits1 first
        unknown_with_neighbouring_hits1 = []
        for u in unknown:
            if u + 1 in hits or u - 1 in hits or u + 10 in hits or u - 10 in hits:
                unknown_with_neighbouring_hits1.append(u)

        # Use corners in early game for exploration
        if len(unknown) > 85:  # First 15 shots
            return random.random() < 0.2

        # Use corners when we have multiple isolated hits
        if len(hits) >= 2:
            isolated_hits = self.count_isolated_hits(hits)
            if isolated_hits >= 2:
                return random.random() < 0.3

        # Use corners when stuck in sinking mode with limited options
        if self.in_sinking_mode and len(unknown_with_neighbouring_hits1) < 3:
            return random.random() < 0.4

        # Use corners for large unexplored areas
        large_areas = self.detect_large_unknown_areas(search)
        if large_areas:
            return random.random() < 0.25

        return False

    def count_isolated_hits(self, hits):
        """
        Count hits that don't have adjacent hits (potential different ships)
        """
        isolated_count = 0
        for hit in hits:
            is_isolated = True
            for offset in [-1, 1, -10, 10]:
                neighbor = hit + offset
                if neighbor in hits:
                    is_isolated = False
                    break
            if is_isolated:
                isolated_count += 1
        return isolated_count

    def detect_large_unknown_areas(self, search):
        """
        Detect if there are large contiguous areas of unknown cells
        """
        visited = set()
        # large_areas = []
        large_areas_count = 0

        for cell in range(100):
            if search[cell] == "U" and cell not in visited:
                # BFS to find contiguous unknown area
                area_size = 0
                queue = [cell]
                visited.add(cell)

                while queue:
                    current = queue.pop(0)
                    area_size += 1

                    # Check neighbors
                    for neighbor in [current + 1, current - 1, current + 10, current - 10]:
                        if (0 <= neighbor < 100 and
                                search[neighbor] == "U" and
                                neighbor not in visited):
                            visited.add(neighbor)
                            queue.append(neighbor)

                if area_size >= 6:  # Consider 6+ cells as a large area
                    # large_areas.append(area_size)
                    large_areas_count += 1

        return large_areas_count

    def find_mm_corner(self, search, hits, unknown):
        """
        Find the best corner for MinMax-enhanced AI
        """
        best_corner = None
        best_score = -1

        for corner in range(121):
            score = self.score_mm_corner(corner, search, hits, unknown)
            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner

    def score_mm_corner(self, corner, search, hits, unknown):
        """
        Score a corner for MinMax strategy
        """
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        if not adjacent_cells:
            return -1

        score = 0

        # Base score from unknown cells
        unknown_count = sum(1 for cell in adjacent_cells if cell in unknown)
        score += unknown_count * 4

        # Bonus for covering areas near unsunk hits
        for hit in hits:
            if not self.is_ship_sunk(hit):
                for cell in adjacent_cells:
                    distance = abs(cell // 10 - hit // 10) + abs(cell % 10 - hit % 10)
                    if distance <= 2:
                        score += 3

        # Penalty for misses
        miss_count = sum(1 for cell in adjacent_cells if search[cell] == "M")
        score -= miss_count * 5

        # Strategic positioning
        corner_row = corner // 11
        corner_col = corner % 11
        center_bonus = 10 - (abs(corner_row - 5) + abs(corner_col - 5))
        score += center_bonus * 0.5

        return max(score, 0)

    def find_sinking_mode_corner(self, search, hits, unknown):
        """
        Find corner specifically for sinking mode situations
        """
        best_corner = None
        best_score = -1

        # Get unsunk hits
        unsunk_hits = [hit for hit in hits if not self.is_ship_sunk(hit)]

        for corner in range(121):
            adjacent_cells = self.get_adjacent_grids_from_corner(corner)
            if not adjacent_cells:
                continue

            score = 0

            # Focus on corners that can help determine ship orientation
            for hit in unsunk_hits:
                # Check if this corner covers potential ship extensions
                for cell in adjacent_cells:
                    if cell in unknown:
                        # Check if this cell aligns with hit pattern
                        if (cell // 10 == hit // 10) or (cell % 10 == hit % 10):  # Same row or column
                            score += 2

            # Bonus for covering multiple unsunk hits
            hit_coverage = 0
            for hit in unsunk_hits:
                for cell in adjacent_cells:
                    if abs(cell - hit) in [1, 10]:  # Adjacent to hit
                        hit_coverage += 1
                        break
            score += hit_coverage * 3

            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner if best_score > 0 else None

    def find_rescue_corner(self, stuck_hit, search, unknown):
        """
        Find a corner to rescue stuck sinking situation
        """
        best_corner = None
        best_score = -1

        for corner in range(121):
            adjacent_cells = self.get_adjacent_grids_from_corner(corner)
            if not adjacent_cells:
                continue

            score = 0

            # Check if this corner covers the stuck hit area
            for cell in adjacent_cells:
                if cell in unknown:
                    # Distance to stuck hit
                    distance = abs(cell // 10 - stuck_hit // 10) + abs(cell % 10 - stuck_hit % 10)
                    if distance <= 2:
                        score += 5 - distance  # Closer is better

            # Bonus for covering multiple unknown cells around the stuck hit
            unknown_around_hit = 0
            for offset in [-1, 1, -10, 10, -2, 2, -20, 20]:
                neighbor = stuck_hit + offset
                if 0 <= neighbor < 100 and neighbor in unknown:
                    unknown_around_hit += 1

            coverage = sum(1 for cell in adjacent_cells if cell in unknown and
                           abs(cell - stuck_hit) in [1, 2, 10, 20, 9, 11, -9, -11])
            score += coverage * 2

            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner if best_score > 0 else None

    def select_best_mm_target(self, candidate_cells, search, hits):
        """
        Intelligently select the best target from candidate cells for MM algorithm
        """
        if not candidate_cells:
            return random.choice(candidate_cells) if candidate_cells else None

        best_cell = None
        best_score = -1

        for cell in candidate_cells:
            score = self.score_mm_target(cell, search, hits)
            if score > best_score:
                best_score = score
                best_cell = cell

        return best_cell

    def score_mm_target(self, cell, search, hits):
        """
        Score a target cell for MM algorithm
        """
        score = 0

        # Base score from hit proximity
        for hit in hits:
            if not self.is_ship_sunk(hit):
                distance = abs(cell // 10 - hit // 10) + abs(cell % 10 - hit % 10)
                if distance == 1:
                    score += 10
                elif distance == 2:
                    score += 5

        # Bonus for strategic positioning
        row = cell // 10
        col = cell % 10
        center_bonus = 8 - (abs(row - 4.5) + abs(col - 4.5))
        score += center_bonus

        # Penalty for adjacent misses
        for offset in [-1, 1, -10, 10]:
            neighbor = cell + offset
            if 0 <= neighbor < 100 and search[neighbor] == "M":
                score -= 3

        return max(score, 0)

    def minmax_ai(self, depth=2):
        print("Entering minmax_ai")

        # If in sinking mode, use basic AI (simpler)
        if self.in_sinking_mode:
            return self.basic_ai_MM()

        # Occasionally use corners (10% chance)
        if random.random() < 0.1:
            corner_result = self.minmax_corner_evaluation()
            if corner_result is not None:
                return corner_result

        # Use existing single-cell logic (keep this part)
        best_score = -math.inf
        best_move = None

        # SIMPLIFIED: Only evaluate a few moves for performance
        available_moves = self.get_available_moves()
        if not available_moves:
            return self.basic_ai()  # Fallback

        # Check only first 10 moves for performance
        for move in available_moves[:10]:
            # Simple evaluation (not full MinMax)
            score = self.simple_move_score(move)
            if score > best_score:
                best_score = score
                best_move = move

        if best_move is not None:
            return self.make_move(best_move, is_corner_click=False)

        # Final fallback
        return self.basic_ai()

    def simple_move_score(self, move):
        """
        SIMPLIFIED move scoring - no MinMax
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        score = 0

        # Check neighbors for hits
        for neighbor in self.get_neighbors(move):
            if search[neighbor] == "H":
                score += 10

        # Center preference
        row, col = divmod(move, 10)
        center_bonus = 8 - (abs(row - 4.5) + abs(col - 4.5))
        score += center_bonus

        return score

    def find_sinking_orientation_corner(self, hits, unknown):
        """
        Find corner to determine ship orientation when we have multiple hits
        """
        best_corner = None
        best_score = -1

        # Get unsunk hits
        unsunk_hits = [hit for hit in hits if not self.is_ship_sunk(hit)]

        if len(unsunk_hits) < 2:
            return None  # Need at least 2 hits to determine orientation

        for corner in range(121):
            adjacent_cells = self.get_adjacent_grids_from_corner(corner)
            if not adjacent_cells:
                continue

            score = 0

            # Look for corners that can help determine if ship is horizontal or vertical
            for hit in unsunk_hits:
                hit_row, hit_col = divmod(hit, 10)

                for cell in adjacent_cells:
                    if cell in unknown:
                        cell_row, cell_col = divmod(cell, 10)

                        # Bonus if this cell aligns with potential ship orientation
                        if cell_row == hit_row:  # Same row - could be horizontal
                            # Check if there are hits in the same row
                            same_row_hits = [h for h in unsunk_hits if h // 10 == hit_row]
                            if len(same_row_hits) >= 2:
                                score += 3

                        if cell_col == hit_col:  # Same column - could be vertical
                            # Check if there are hits in the same column
                            same_col_hits = [h for h in unsunk_hits if h % 10 == hit_col]
                            if len(same_col_hits) >= 2:
                                score += 3

            if score > best_score:
                best_score = score
                best_corner = corner

        return best_corner if best_score > 0 else None

    def enhanced_sinking_mode(self):
        """
        Enhanced sinking mode that can use corner clicks strategically
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        hits = [i for i, square in enumerate(search) if square == "H"]
        unknown = [i for i, square in enumerate(search) if square == "U"]

        # Check if we should use corner in sinking mode
        if len(hits) >= 2:
            # Use corner to determine ship orientation when multiple hits exist
            sinking_corner = self.find_sinking_orientation_corner(hits, unknown)
            if sinking_corner is not None:
                result = self.make_move(sinking_corner, is_corner_click=True)
                print(f"Using orientation corner {sinking_corner} in sinking mode, result: {result}")
                if isinstance(result, dict) and result.get('hits_detected', 0) > 0:
                    return result

        # Fall back to basic_ai_MM (not basic_ai_MM1)
        return self.basic_ai_MM()

    def should_minmax_use_corner(self):
        """
        Determine if MinMax should consider corner clicks
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        unknown = [i for i, square in enumerate(search) if square == "U"]
        hits = [i for i, square in enumerate(search) if square == "H"]

        # Early game: use corners for exploration
        if len(unknown) > 85:  # First 15 shots
            return random.random() < 0.25

        # When we have multiple isolated hits
        if len(hits) >= 2:
            isolated_hits = self.count_isolated_hits(hits)
            if isolated_hits >= 2:
                return random.random() < 0.35

        # When game is stuck or predictable
        if len(self.get_available_moves()) > 60:  # Many moves available
            return random.random() < 0.2

        return False

    def minmax_corner_evaluation(self, depth=1):  # Reduced depth for performance
        """
        FAST corner evaluation using heuristic scoring instead of deep MinMax
        """
        # Get top corners using simple heuristic (much faster)
        top_corners = self.get_top_corner_candidates_fast(count=3)  # Evaluate only top 3

        best_corner = None
        best_score = -math.inf

        for corner in top_corners:
            # Use simple heuristic scoring instead of deep MinMax
            score = self.fast_corner_score(corner)
            if score > best_score:
                best_score = score
                best_corner = corner

        if best_corner is not None and best_score > 15:  # Minimum threshold
            result = self.make_move(best_corner, is_corner_click=True)
            print(f"MinMax selected corner {best_corner} with score {best_score}, result: {result}")
            return result

        return None


    def get_strategic_corners(self):
        """
        Return only strategically important corners to reduce computation
        """
        # Focus on center and areas near hits
        strategic_corners = []

        # Center area corners (most important)
        for row in range(3, 8):  # 3-7 (center rows)
            for col in range(3, 8):  # 3-7 (center columns)
                strategic_corners.append(row * 11 + col)

        # Add corners near hits
        search = self.player1.search if self.player1_turn else self.player2.search
        hits = [i for i, square in enumerate(search) if square == "H"]

        for hit in hits:
            hit_row, hit_col = divmod(hit, 10)
            # Add corners around hits
            for r_offset in [-1, 0, 1]:
                for c_offset in [-1, 0, 1]:
                    corner_row = hit_row + r_offset
                    corner_col = hit_col + c_offset
                    if 0 <= corner_row < 11 and 0 <= corner_col < 11:
                        corner_idx = corner_row * 11 + corner_col
                        if corner_idx not in strategic_corners:
                            strategic_corners.append(corner_idx)

        return strategic_corners

    def get_top_corner_candidates_fast(self, count=5):
        """
        SIMPLIFIED - Fast corner selection
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        corner_scores = []

        # Only check strategic corners (not all 121)
        for corner in range(0, 121, 3):  # Check every 3rd corner for speed
            score = self.fast_corner_score(corner)
            if score > 0:
                corner_scores.append((corner, score))

        # Return top N corners
        corner_scores.sort(key=lambda x: x[1], reverse=True)
        return [corner for corner, score in corner_scores[:count]]

    def fast_corner_score(self, corner):
        """
        Fast heuristic scoring for corners - no MinMax simulation
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        hits = [i for i, square in enumerate(search) if square == "H"]
        unknown = [i for i, square in enumerate(search) if square == "U"]

        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        if not adjacent_cells:
            return -1

        score = 0

        # 1. Unknown cells coverage (most important)
        unknown_count = sum(1 for cell in adjacent_cells if cell in unknown)
        score += unknown_count * 8  # Higher weight for coverage

        # 2. Proximity to unsunk hits
        unsunk_hits = [hit for hit in hits if not self.is_ship_sunk(hit)]
        for hit in unsunk_hits:
            for cell in adjacent_cells:
                if cell in unknown:
                    # Distance to hit
                    distance = abs(cell // 10 - hit // 10) + abs(cell % 10 - hit % 10)
                    if distance == 1:
                        score += 12  # Adjacent to hit - very valuable
                    elif distance == 2:
                        score += 6  # Near hit - valuable

        # 3. Penalty for misses
        miss_count = sum(1 for cell in adjacent_cells if search[cell] == "M")
        score -= miss_count * 10  # High penalty for wasted shots

        # 4. Strategic positioning
        corner_row = corner // 11
        corner_col = corner % 11
        center_bonus = 10 - (abs(corner_row - 5) + abs(corner_col - 5))
        score += center_bonus * 2

        # 5. Information gain (simple version)
        info_gain = 0
        for cell in adjacent_cells:
            if cell in unknown:
                # Check if this resolves orientation
                if self.can_resolve_orientation_simple(cell, search):
                    info_gain += 3
        score += info_gain

        return max(score, 0)

    def can_resolve_orientation_simple(self, cell, search):
        """
        Simple version of orientation resolution check
        """
        row, col = divmod(cell, 10)

        # Check if we have horizontal hints but not vertical, or vice versa
        horizontal_hints = False
        vertical_hints = False

        # Check left/right
        if (col > 0 and search[row * 10 + (col - 1)] == "H") or \
                (col < 9 and search[row * 10 + (col + 1)] == "H"):
            horizontal_hints = True

        # Check up/down
        if (row > 0 and search[(row - 1) * 10 + col] == "H") or \
                (row < 9 and search[(row + 1) * 10 + col] == "H"):
            vertical_hints = True

        return horizontal_hints != vertical_hints  # Resolves ambiguity



    def assume_corner_hits(self, corner, player, search):
        """
        Estimate how many hits a corner click would produce
        """
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        hit_count = 0

        for cell in adjacent_cells:
            if 0 <= cell < 100 and self.assume_cell_hit(cell, player, search):
                hit_count += 1

        return hit_count

    def assume_cell_hit(self, cell, player, search):
        """
        Enhanced cell hit assumption for MinMax
        """
        row, col = divmod(cell, 10)
        score = 0

        # Factor 1: Proximity to known hits
        for neighbor in self.get_neighbors(cell):
            if 0 <= neighbor < 100 and search[neighbor] == "H":
                if not self.is_ship_sunk(neighbor):
                    score += 15  # Higher weight for unsunk hits
                else:
                    score -= 5  # Penalty near sunk ships

        # Factor 2: Strategic positioning
        if (row + col) % 2 == 0:  # Checkerboard pattern
            score += 2

        # Factor 3: Center preference
        distance_from_center = abs(row - 4.5) + abs(col - 4.5)
        center_bonus = (8 - distance_from_center) * 0.5
        score += center_bonus

        # Factor 4: Avoid recent misses
        for neighbor in self.get_neighbors(cell):
            if neighbor in self.actual_misses:
                score -= 3

        # Factor 5: Ship placement probability
        placement_score = self.get_ship_placement_probability(cell, search)
        score += placement_score * 2

        return score > 12  # Adjusted threshold

    def get_ship_placement_probability(self, cell, search):
        """
        Calculate probability of ship placement at this cell
        """
        row, col = divmod(cell, 10)
        score = 0

        # Check horizontal placement possibilities
        for size in [2, 3, 4, 5]:
            # Check left extension
            can_extend_left = True
            for i in range(1, size):
                if col - i < 0 or search[row * 10 + (col - i)] == "M":
                    can_extend_left = False
                    break
            if can_extend_left:
                score += 1

            # Check right extension
            can_extend_right = True
            for i in range(1, size):
                if col + i >= 10 or search[row * 10 + (col + i)] == "M":
                    can_extend_right = False
                    break
            if can_extend_right:
                score += 1

        # Check vertical placement possibilities
        for size in [2, 3, 4, 5]:
            # Check up extension
            can_extend_up = True
            for i in range(1, size):
                if row - i < 0 or search[(row - i) * 10 + col] == "M":
                    can_extend_up = False
                    break
            if can_extend_up:
                score += 1

            # Check down extension
            can_extend_down = True
            for i in range(1, size):
                if row + i >= 10 or search[(row + i) * 10 + col] == "M":
                    can_extend_down = False
                    break
            if can_extend_down:
                score += 1

        return score

    def get_top_corner_candidates(self, count=5):
        """
        Get top corner candidates for MinMax evaluation
        """
        search = self.player1.search if self.player1_turn else self.player2.search
        hits = [i for i, square in enumerate(search) if square == "H"]
        unknown = [i for i, square in enumerate(search) if square == "U"]

        corner_scores = []

        for corner in range(121):
            score = self.score_corner_for_minmax(corner, search, hits, unknown)
            corner_scores.append((corner, score))

        # Sort by score and return top candidates
        corner_scores.sort(key=lambda x: x[1], reverse=True)
        return [corner for corner, score in corner_scores[:count]]

    def score_corner_for_minmax(self, corner, search, hits, unknown):
        """
        Score a corner specifically for MinMax algorithm
        """
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        if not adjacent_cells:
            return -1

        score = 0

        # Base score from unknown cells
        unknown_count = sum(1 for cell in adjacent_cells if cell in unknown)
        score += unknown_count * 5

        # Strategic value: coverage of potential ship areas
        strategic_value = self.calculate_corner_strategic_value(corner, search, hits)
        score += strategic_value * 3

        # Information gain: how much this corner reveals
        information_gain = self.calculate_corner_information_gain(corner, search)
        score += information_gain * 2

        # Penalty for misses
        miss_count = sum(1 for cell in adjacent_cells if search[cell] == "M")
        score -= miss_count * 6

        return max(score, 0)


    def can_resolve_orientation(self, cell, search):
        """
        Check if this cell can help resolve ship orientation
        """
        row, col = divmod(cell, 10)
        has_horizontal_hints = False
        has_vertical_hints = False

        # Check horizontal alignment hints
        if (col > 0 and search[row * 10 + (col - 1)] == "H") or \
                (col < 9 and search[row * 10 + (col + 1)] == "H"):
            has_horizontal_hints = True

        # Check vertical alignment hints
        if (row > 0 and search[(row - 1) * 10 + col] == "H") or \
                (row < 9 and search[(row + 1) * 10 + col] == "H"):
            has_vertical_hints = True

        return has_horizontal_hints != has_vertical_hints  # Resolves ambiguity

    def is_ship_sunk(self, index):
        player = self.player1 if self.player1_turn else self.player2
        for ship in player.ships:
            if index in ship.indexes:
                for idx in ship.indexes:
                    if player.search[idx] == "U":
                        return False
                return True
        return False

    def get_available_moves(self):
        """Get all available single-cell moves"""
        search = self.player1.search if self.player1_turn else self.player2.search
        return [i for i, square in enumerate(search) if square == "U" and i not in self.actual_misses]

    def get_available_corners(self):
        """Get all available corner moves"""
        # All corners are always available (0-120)
        return list(range(121))

    def get_all_available_moves(self):
        """Get both single-cell and corner moves"""
        single_moves = self.get_available_moves()
        corner_moves = self.get_available_corners()
        return single_moves, corner_moves



    def assume_hit(self, player, move, search):
        """Enhanced logic for assuming a hit with corner-aware evaluation"""
        row, col = divmod(move, 10)
        score = 0

        # Factor 1: Proximity to Known Hits (with sunk ship awareness)
        for neighbor in self.get_neighbors(move):
            if search[neighbor] == "H":
                if self.is_ship_sunk(neighbor):
                    score -= 8  # Higher penalty for proximity to sunk ship
                else:
                    score += 25  # Very high value for unsunk hit proximity

        # Factor 2: Potential Ship Placements
        potential_placements = self.get_potential_ship_placements(move, search)
        score += potential_placements * 4

        # Factor 3: Density of Unknown Cells
        unknown_density = self.get_unknown_density(move, search)
        score += unknown_density * 3

        # Factor 4: Avoid Clustering with Misses
        for neighbor in self.get_neighbors(move):
            if neighbor in self.actual_misses:
                score -= 8

        # Factor 5: Strategic Positioning
        if (row + col) % 2 == 0:
            score += 3  # Checkerboard pattern bonus

        # Factor 6: Center preference
        distance_from_center = abs(row - 4.5) + abs(col - 4.5)
        center_bonus = (8 - distance_from_center) * 0.8
        score += center_bonus

        # Factor 7: Ship size probability
        ship_probability = self.calculate_ship_probability(move, search)
        score += ship_probability * 2

        # Reduced randomness for more consistent evaluation
        random_factor = random.uniform(0, 5)
        score += random_factor

        return score > 20  # Adjusted threshold

    def assume_corner_hits(self, corner, player, search):
        """Estimate how many hits a corner click would produce"""
        adjacent_cells = self.get_adjacent_grids_from_corner(corner)
        hit_count = 0

        for cell in adjacent_cells:
            if 0 <= cell < 100 and self.assume_hit(player, cell, search):
                hit_count += 1

        return hit_count

    def get_potential_ship_placements(self, move, search):
        """Calculate potential ship placements through this cell"""
        count = 0
        row, col = divmod(move, 10)

        # Check horizontal placements
        for direction in [-1, 1]:  # Left and right
            for size in [2, 3, 4, 5]:
                valid = True
                for step in range(size):
                    check_col = col + direction * step
                    if check_col < 0 or check_col >= 10:
                        valid = False
                        break
                    check_index = row * 10 + check_col
                    if search[check_index] == "M":  # Can't place over misses
                        valid = False
                        break
                if valid:
                    count += 1
                    break  # Count each direction only once per size

        # Check vertical placements
        for direction in [-1, 1]:  # Up and down
            for size in [2, 3, 4, 5]:
                valid = True
                for step in range(size):
                    check_row = row + direction * step
                    if check_row < 0 or check_row >= 10:
                        valid = False
                        break
                    check_index = check_row * 10 + col
                    if search[check_index] == "M":  # Can't place over misses
                        valid = False
                        break
                if valid:
                    count += 1
                    break  # Count each direction only once per size

        return count

    def get_unknown_density(self, move, search):
        """Calculate density of unknown cells around the move"""
        neighbors = self.get_neighbors(move)
        return sum(1 for neighbor in neighbors if search[neighbor] == "U")

    def calculate_ship_probability(self, move, search):
        """Calculate probability of ship presence based on remaining ships"""
        row, col = divmod(move, 10)
        probability = 0

        # Check if this cell could be part of any remaining ships
        remaining_ships = self.get_remaining_ship_sizes(search)

        for ship_size in remaining_ships:
            # Check horizontal possibilities
            for start_col in range(max(0, col - ship_size + 1), min(10 - ship_size + 1, col + 1)):
                valid = True
                for i in range(ship_size):
                    check_index = row * 10 + (start_col + i)
                    if search[check_index] == "M":
                        valid = False
                        break
                if valid:
                    probability += 1

            # Check vertical possibilities
            for start_row in range(max(0, row - ship_size + 1), min(10 - ship_size + 1, row + 1)):
                valid = True
                for i in range(ship_size):
                    check_index = (start_row + i) * 10 + col
                    if search[check_index] == "M":
                        valid = False
                        break
                if valid:
                    probability += 1

        return probability

    def get_remaining_ship_sizes(self, search):
        """Get sizes of ships that haven't been sunk yet"""
        player = self.player1 if self.player1_turn else self.player2
        opponent = self.player2 if self.player1_turn else self.player1

        original_ships = [5, 4, 3, 3, 2]
        sunk_ships = []

        # Check which ships are sunk
        for ship in opponent.ships:
            sunk = True
            for idx in ship.indexes:
                if search[idx] == "U":
                    sunk = False
                    break
            if sunk:
                sunk_ships.append(ship.size)

        # Remove sunk ships from original list
        remaining_ships = original_ships.copy()
        for sunk_size in sunk_ships:
            if sunk_size in remaining_ships:
                remaining_ships.remove(sunk_size)

        return remaining_ships

    def evaluate(self, search):
        """Enhanced evaluation function considering corner strategy"""
        player_hits = sum(1 for i in search if i == "H")
        opponent_hits = sum(1 for i in self.player2.search if i == "H")

        # Base score
        base_score = player_hits - opponent_hits

        # Add strategic bonuses
        strategic_bonus = self.calculate_strategic_bonus(search)

        return base_score + strategic_bonus

    def calculate_strategic_bonus(self, search):
        """Calculate strategic bonus for position evaluation"""
        bonus = 0

        # Bonus for unsunk hits (active targets)
        unsunk_hits = self.get_unsunk_hits(search)
        bonus += len(unsunk_hits) * 2

        # Bonus for clustered hits (indicating ship damage)
        clustered_bonus = self.evaluate_hit_clustering(search)
        bonus += clustered_bonus

        # Bonus for board control (unknown cells in strategic positions)
        control_bonus = self.evaluate_board_control(search)
        bonus += control_bonus * 0.5

        return bonus

    def get_unsunk_hits(self, search):
        """Get hits that are part of unsunk ships"""
        unsunk_hits = []
        for i, cell in enumerate(search):
            if cell == "H":
                # Check if this hit is part of a sunk ship
                if not self.is_ship_sunk(i):
                    unsunk_hits.append(i)
        return unsunk_hits

    def evaluate_hit_clustering(self, search):
        """Evaluate how well hits are clustered (indicating ship damage)"""
        hits = [i for i, cell in enumerate(search) if cell == "H"]
        if not hits:
            return 0

        clusters = []
        visited = set()

        for hit in hits:
            if hit not in visited:
                # Find cluster using BFS
                cluster = []
                queue = [hit]
                visited.add(hit)

                while queue:
                    current = queue.pop(0)
                    cluster.append(current)

                    # Check adjacent hits
                    for neighbor in self.get_neighbors(current):
                        if neighbor in hits and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                clusters.append(cluster)

        # Score based on cluster sizes (larger clusters are better)
        cluster_score = 0
        for cluster in clusters:
            cluster_score += len(cluster) ** 1.5  # Non-linear scaling

        return cluster_score

    def evaluate_board_control(self, search):
        """Evaluate control over strategic board positions"""
        control_score = 0
        unknown_cells = [i for i, cell in enumerate(search) if cell == "U"]

        for cell in unknown_cells:
            row, col = divmod(cell, 10)

            # Center control
            distance_from_center = abs(row - 4.5) + abs(col - 4.5)
            center_value = max(0, 8 - distance_from_center)

            # Checkerboard pattern value
            checker_value = 1 if (row + col) % 2 == 0 else 0

            # Information value (cells that reveal more about surroundings)
            info_value = self.calculate_information_value(cell, search)

            control_score += center_value + checker_value + info_value

        return control_score

    def calculate_information_value(self, cell, search):
        """Calculate how much information this cell would reveal"""
        value = 0
        row, col = divmod(cell, 10)

        # Value for resolving ship orientations
        if self.can_resolve_orientation(cell, search):
            value += 2

        # Value for connecting isolated hits
        isolated_hits_nearby = self.count_isolated_hits_nearby(cell, search)
        value += isolated_hits_nearby * 1.5

        return value

    def count_isolated_hits_nearby(self, cell, search):
        """Count isolated hits near this cell"""
        count = 0
        for neighbor in self.get_neighbors(cell):
            if search[neighbor] == "H":
                # Check if this hit is isolated
                is_isolated = True
                for n2 in self.get_neighbors(neighbor):
                    if n2 != cell and search[n2] == "H":
                        is_isolated = False
                        break
                if is_isolated:
                    count += 1
        return count

    def evaluate_pattern_completion(self, search):
        """Evaluate pattern completion bonus for strategic positioning"""
        bonus = 0

        # Check for potential ship patterns
        for i in range(100):
            if search[i] == "H":
                # Check if this hit completes a ship pattern
                row, col = i // 10, i % 10

                # Check horizontal pattern
                horizontal_pattern = self.check_horizontal_pattern(i, search)
                bonus += horizontal_pattern

                # Check vertical pattern
                vertical_pattern = self.check_vertical_pattern(i, search)
                bonus += vertical_pattern

        return bonus * 0.5  # Scale down the bonus

    def check_horizontal_pattern(self, index, search):
        """Check for horizontal ship patterns"""
        row, col = index // 10, index % 10
        pattern_score = 0

        # Check left and right for consecutive hits
        left_count = 0
        right_count = 0

        # Check left
        for c in range(col - 1, max(-1, col - 4), -1):
            if 0 <= c and search[row * 10 + c] == "H":
                left_count += 1
            else:
                break

        # Check right
        for c in range(col + 1, min(10, col + 4)):
            if c < 10 and search[row * 10 + c] == "H":
                right_count += 1
            else:
                break

        # Score based on pattern length
        total_hits = left_count + right_count + 1  # +1 for current cell
        if total_hits >= 2:
            pattern_score += total_hits * 2

        return pattern_score

    def check_vertical_pattern(self, index, search):
        """Check for vertical ship patterns"""
        row, col = index // 10, index % 10
        pattern_score = 0

        # Check up and down for consecutive hits
        up_count = 0
        down_count = 0

        # Check up
        for r in range(row - 1, max(-1, row - 4), -1):
            if 0 <= r and search[r * 10 + col] == "H":
                up_count += 1
            else:
                break

        # Check down
        for r in range(row + 1, min(10, row + 4)):
            if r < 10 and search[r * 10 + col] == "H":
                down_count += 1
            else:
                break

        # Score based on pattern length
        total_hits = up_count + down_count + 1  # +1 for current cell
        if total_hits >= 2:
            pattern_score += total_hits * 2

        return pattern_score

    def evaluate_threat_level(self, search):
        """Evaluate threat level based on remaining ship potential"""
        threat = 0

        # Count remaining unknown cells that could contain ships
        unknown_count = sum(1 for cell in search if cell == "U")
        threat += unknown_count * 0.1

        # Add threat for areas with high ship placement probability
        for i in range(100):
            if search[i] == "U":
                placement_prob = self.get_ship_placement_probability(i, search)
                threat += placement_prob * 0.05

        return threat


    def evaluate_enhanced(self, search):
        """Final enhanced evaluation function"""
        base_score = self.evaluate(search)

        # Additional strategic factors
        pattern_bonus = self.evaluate_pattern_completion(search)
        threat_bonus = self.evaluate_threat_level(search)

        return base_score + pattern_bonus + threat_bonus

    def is_game_over(self, search):
        """Check if game is over in simulated state"""
        # Count unknown cells that could contain ships
        unknown_count = sum(1 for cell in search if cell == "U")
        return unknown_count == 0

    def get_neighbors(self, move):
        """Get valid neighboring cells"""
        neighbors = []
        row, col = divmod(move, 10)
        if col > 0:
            neighbors.append(move - 1)
        if col < 9:
            neighbors.append(move + 1)
        if row > 0:
            neighbors.append(move - 10)
        if row < 9:
            neighbors.append(move + 10)
        return neighbor





