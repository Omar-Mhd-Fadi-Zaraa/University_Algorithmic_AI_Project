from collections import deque
import random 

grid = [[" . " for _ in range(12) ] for _ in range(12)] 
coords = [(r, c) for r in range(12) for c in range(12)]
random.shuffle(coords) 

def place(symbol):
    r, c = coords.pop()
    grid[r][c] = symbol
    return (r, c)

start_energy = 28
start_pos = place(" S ")
place(" G ")
place(" D1"); place(" D2"); place(" D3")
for _ in range(39): place(" M ")
for _ in range(9): place(" X ")

def get_neighbors( r , c ,grid) :
    MOVES = {
      "UP"    :  (-1 ,0) ,
      "DOWN"  :  (1,0)   ,
      "LEFT"  :  (0,-1)  ,
      "RIGHT" :  (0,1)   ,
            }
    neighbors = []
    for move_name ,(x , y) in MOVES.items() :
        x = x + r 
        y = y + c 
        if x>= 0 and x <12 and y>= 0 and y <12 and grid[x][y] != " X " :
                neighbors.append(((x,y), move_name))   
    return neighbors  

def prepare_sol ( steps_taken ,parent , curr_l ) :
    solution = []
    while curr_l in parent :
        solution.append((steps_taken[curr_l]))
        curr_l = parent[curr_l] 
    solution.reverse()    
    return solution


def bfs(start_energy ,grid , s ) :
    D_collected = frozenset()
    queue = deque([(s , start_energy , D_collected)])
    visited = {(s[0], s[1] , D_collected)}
    steps_taken = {}
    parent = {}
    while queue :
            (r, c), curr_E, curr_D = queue.popleft() 
            curr_state = (r ,c ,curr_D)
            if grid[r][c] == " G " and  len(curr_D) == 3 :
                return curr_E ,prepare_sol( steps_taken ,parent, curr_state)
            
            neighbors = get_neighbors(r,c,grid)

            for (x,y) , move  in neighbors :
                new_E = curr_E + (-5 if grid[x][y] == " M " else -1)
                new_D = curr_D 

                if grid[x][y] in [" D1" , " D2" , " D3"] and grid[x][y] not in curr_D :
                    new_D = curr_D| {grid[x][y]}
                    new_E += 2

                if new_E >= 0:
                    new_state = (x, y, new_D)
                    if new_state not in visited:
                        visited.add(new_state)
                        parent[new_state] = curr_state
                        steps_taken[new_state] = move
                        queue.append(((x, y), new_E, new_D))
                    
    return None    
       
def print_grid(grid):
    print("\n" + "="*50) 
    for row in grid:
        print("|" + " ".join(f"{str(cell):^2}" for cell in row) + " |")
    print("="*50 + "\n")


print_grid(grid)     
result = bfs( start_energy ,grid, start_pos)

if result:
    rem_energy, path = result
    print(f"--- SUCCESS! ---")
    print(f"Remaining Energy: {rem_energy}")
    print(f"Path taken: {' -> '.join(path)}")
else:
    print("--- FAILED: No path found to Goal with all 3 deliveries ---")




