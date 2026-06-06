# -*- coding: utf-8 -*-
"""
Created on Fri May  7 21:22:25 2021
@author: Ishanki
"""
from pyomo.environ import *

class Suko:
    """
    Creates the Suko problem from data given.
    Attributes:
        colour_1_cells(list): contains tuples for cells with the first colour
        colour_2_cells(list): contains tuples for cells with the second colour
        colour_3_cells(list): contains tuples for cells with the third colour
        colour_sums(list): totals for first, second, and third colours
        quadrant_sums(list): totals for each set of four cells from left to right
    """
    def __init__(self,colour_1_cells, colour_2_cells, colour_3_cells, colour_sums,
                 quadrant_sums):
        self.colour_1_cells = colour_1_cells
        self.colour_2_cells = colour_2_cells
        self.colour_3_cells = colour_3_cells
        self.colour_sums = colour_sums
        self.quadrant_sums = quadrant_sums
        
    def solve_problem(self):
        m = ConcreteModel()  # creating Pyomo concrete model
        m.r = RangeSet(3)  # no. of rows in the grid
        m.c = RangeSet(3)  # no. of columns in the grid
        N = list(range(1,10))  # list of values to go in the suko grid
        m.v = Set(initialize=N)  # value taken by square
        m.x = Var(m.r, m.c, m.v, within=Binary) # binary variables
        
        def C1(m,v):
            return sum(m.x[r,c,v] for r in m.r for c in m.c) == 1
        m.no_repeats = Constraint(m.v, rule=C1)
        
        def C2(m,r,c):
            return sum(m.x[r,c,v] for v in m.v) == 1
        m.all_filled = Constraint(m.r, m.c, rule=C2)
        
        m.colour_1 = ConstraintList()
        expr_1 = 0
        for i in self.colour_1_cells:
            for v in m.v:
                expr_1 += m.x[i,v]*N[v-1]
            # print(expr_1)
        m.colour_1.add(expr_1 == self.colour_sums[0])
        
        m.colour_2 = ConstraintList()
        expr_2 = 0
        for i in self.colour_2_cells:
            for v in m.v:
                expr_2 += m.x[i,v]*N[v-1]
            # print(expr_2)
        m.colour_2.add(expr_2 == self.colour_sums[1])
        
        m.colour_3 = ConstraintList()
        expr_3 = 0
        for i in self.colour_3_cells:
            for v in m.v:
                expr_3 += m.x[i,v]*N[v-1]
            # print(expr_3)
        m.colour_3.add(expr_3 == self.colour_sums[2])   
        
        def C6(m):
            return sum(m.x[1,1,v]*N[v-1] + m.x[1,2,v]*N[v-1] + m.x[2,1,v]*N[v-1] \
                        + m.x[2,2,v]*N[v-1] for v in m.v) == self.quadrant_sums[0]
        m.quadrant_1 = Constraint(rule=C6)
        
        def C7(m):
            return sum(m.x[1,2,v]*N[v-1] + m.x[1,3,v]*N[v-1] + m.x[2,2,v]*N[v-1] \
                        + m.x[2,3,v]*N[v-1] for v in m.v) == self.quadrant_sums[1]
        m.quadrant_2 = Constraint(rule=C7)
        
        def C8(m):
            return sum(m.x[2,1,v]*N[v-1] + m.x[2,2,v]*N[v-1] + m.x[3,1,v]*N[v-1] \
                        + m.x[3,2,v]*N[v-1] for v in m.v) == self.quadrant_sums[2]
        m.quadrant_3 = Constraint(rule=C8)
        
        def C9(m):
            return sum(m.x[2,2,v]*N[v-1] + m.x[2,3,v]*N[v-1] + m.x[3,2,v]*N[v-1] \
                        + m.x[3,3,v]*N[v-1] for v in m.v) == self.quadrant_sums[3]
        m.quadrant_4 = Constraint(rule=C9)
        
        m.obj = Objective(sense = minimize, expr=1)
        
        # Solving the model
        # solver=SolverFactory('gams')
        # results = solver.solve(m, tee=True, solver = 'cplex')
        
        solver=SolverFactory('glpk', executable='/opt/homebrew/bin/glpsol')
        results = solver.solve(m, tee=True)
        
        # Storing and printing solutions
        answers = []
        for k, v in m.x.items():
            if value(v) == 1:
                answers.append(k[2])
                
        # print(answers)
        
        grid = f"""\n
        [{answers[0]}][{answers[1]}][{answers[2]}]\n
        [{answers[3]}][{answers[4]}][{answers[5]}]\n
        [{answers[6]}][{answers[7]}][{answers[8]}]
        """
        print("\nThe solution is: "+grid)
   

def print_grid(colour_map):
    """Print the 3x3 grid with colour labels for assigned cells."""
    symbols = {1: 'A', 2: 'B', 3: 'C'}
    cell_label = {}
    for colour, cells in colour_map.items():
        for cell in cells:
            cell_label[cell] = symbols[colour]

    print()
    for r in range(1, 4):
        row = ""
        for c in range(1, 4):
            label = cell_label.get((r, c), ' ')
            row += f"[({r},{c})={label}]  "
        print("  " + row)
    print()


def print_quadrant_diagram():
    print("""
  Quadrant layout (each quadrant is a 2x2 block):

    Q1: (1,1)(1,2)    Q2: (1,2)(1,3)
        (2,1)(2,2)        (2,2)(2,3)

    Q3: (2,1)(2,2)    Q4: (2,2)(2,3)
        (3,1)(3,2)        (3,2)(3,3)

  Enter sums left-to-right: Q1, Q2, Q3, Q4
""")


def parse_cells(raw):
    """Parse a string like '(1,1),(2,3),(3,2)' into a list of tuples."""
    import re
    pairs = re.findall(r'\((\d)\s*,\s*(\d)\)', raw)
    if not pairs:
        raise ValueError("No valid cell tuples found. Use format: (row,col),(row,col),...")
    cells = [(int(r), int(c)) for r, c in pairs]
    for r, c in cells:
        if r not in (1, 2, 3) or c not in (1, 2, 3):
            raise ValueError(f"Cell ({r},{c}) is out of range — rows and columns must be 1, 2, or 3.")
    return cells


def get_inputs():
    print("\n=== SUKO PUZZLE SOLVER ===")
    print("\nThe grid uses (row, col) coordinates, rows and columns numbered 1–3 top-to-bottom, left-to-right.")
    print("\nStep 1: Assign each of the 9 cells to one of 3 colours (A, B, C).")
    print("        All 9 cells must be covered with no overlaps.\n")

    colour_map = {}
    all_assigned = set()

    for i, label in enumerate(['A', 'B', 'C'], start=1):
        while True:
            try:
                print_grid(colour_map)
                raw = input(f"  Enter cells for colour {label} (e.g. (1,1),(2,1),(3,1)): ").strip()
                cells = parse_cells(raw)
                overlap = all_assigned & set(cells)
                if overlap:
                    print(f"  Error: cells {sorted(overlap)} are already assigned to another colour.\n")
                    continue
                colour_map[i] = cells
                all_assigned |= set(cells)
                break
            except ValueError as e:
                print(f"  Error: {e}\n")

    if all_assigned != {(r, c) for r in range(1, 4) for c in range(1, 4)}:
        missing = {(r, c) for r in range(1, 4) for c in range(1, 4)} - all_assigned
        print(f"\n  Warning: cells {sorted(missing)} were not assigned to any colour.")

    print_grid(colour_map)

    print("Step 2: Enter the target sum for each colour.\n")
    colour_sums = []
    for i, label in enumerate(['A', 'B', 'C'], start=1):
        while True:
            try:
                s = int(input(f"  Target sum for colour {label}: ").strip())
                colour_sums.append(s)
                break
            except ValueError:
                print("  Please enter a whole number.")

    print()
    print_quadrant_diagram()
    print("Step 3: Enter the target sum for each quadrant.\n")
    quadrant_sums = []
    for label in ['Q1', 'Q2', 'Q3', 'Q4']:
        while True:
            try:
                s = int(input(f"  Target sum for {label}: ").strip())
                quadrant_sums.append(s)
                break
            except ValueError:
                print("  Please enter a whole number.")

    return colour_map[1], colour_map[2], colour_map[3], colour_sums, quadrant_sums


colour_1_cells, colour_2_cells, colour_3_cells, colour_sums, quadrant_sums = get_inputs()

suko = Suko(colour_1_cells, colour_2_cells, colour_3_cells, colour_sums, quadrant_sums)
suko.solve_problem()