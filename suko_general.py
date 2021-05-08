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
        
        solver=SolverFactory('glpk')
        results = solver.solve(m, tee=True)
        
        # Storing and printing solutions
        answers = []
        for k, v in m.x.items():
            if v == 1:
                answers.append(k[2])
                
        # print(answers)
        
        grid = f"""\n
        [{answers[0]}][{answers[1]}][{answers[2]}]\n
        [{answers[3]}][{answers[4]}][{answers[5]}]\n
        [{answers[6]}][{answers[7]}][{answers[8]}]
        """
        print("\nThe solution is: "+grid)
   
             
# INPUTS
colour_1_cells = [(1,1),(2,1),(3,1)]
colour_2_cells = [(1,2),(1,3),(2,3)]
colour_3_cells = [(2,2),(3,2),(3,3)]
colour_sums = [11, 11, 23]  # sums for each colour
quadrant_sums = [19, 17, 21, 26]  # left to right, sums for each quadrant

# Creating Suko object and running the optimisation model to get results
suko = Suko(colour_1_cells, colour_2_cells, colour_3_cells, colour_sums,
            quadrant_sums)
suko.solve_problem()