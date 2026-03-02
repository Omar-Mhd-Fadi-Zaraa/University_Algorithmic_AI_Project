import random

grid = [[" . " for _ in range(12)] for _ in range(12)] 
coords = [(r, c) for r in range(12) for c in range(12)]
random.shuffle(coords) 

def place(symbol):
    r, c = coords.pop()
    grid[r][c] = symbol
    return (r, c)

start_pos = place(" S ")
place(" G ")
place(" D1"); place(" D2"); place(" D3")
for _ in range(39): place(" M ")
for _ in range(9): place(" X ")

def get_neighbors(r, c, grid):
    moves = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
    neighbors = []
    for m, (dr, dc) in moves.items():
        nr, nc = r + dr, c + dc
        if 0 <= nr < 12 and 0 <= nc < 12 and grid[nr][nc] != " X ":
            neighbors.append(((nr, nc), m))
    return neighbors

def dfs_optimal(grid, start, energy_limit):
    stack = [(start, energy_limit, frozenset(), [])]
    visited_energy = {}

    while stack:
        (r, c), curr_e, items, path = stack.pop()
        state = (r, c, items)

        if grid[r][c] == " G " and len(items) == 3:
            return curr_e, path

        if state in visited_energy and visited_energy[state] >= curr_e:
            continue
        visited_energy[state] = curr_e

        neighbors = get_neighbors(r, c, grid)

        for (nr, nc), move in neighbors:
            cell = grid[nr][nc]
            cost = -5 if cell == " M " else -1
            new_e = curr_e + cost
            new_items = items

            if cell in [" D1", " D2", " D3"] and cell not in items:
                new_items = items | {cell}
                new_e += 2

            if new_e >= 0:
                stack.append(((nr, nc), new_e, new_items, path + [move]))
    return None

def print_grid(grid):
    print("\n" + "="*50) 
    for row in grid:
        print("|" + " ".join(f"{str(cell):^2}" for cell in row) + " |")
    print("="*50 + "\n")



print_grid(grid)
result = dfs_optimal(grid, start_pos, 28)

if result:
    print(f"--- DFS SUCCESS ---\nEnergy Left: {result[0]}\nPath: {' -> '.join(result[1])}")
else:
    print("--- DFS FAILED ---")