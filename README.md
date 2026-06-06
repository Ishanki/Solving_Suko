# Solving_Suko
The Suko puzzle was created by Jai Gomer of Kobayaashi Studios, and is usually solved by hand.
The code provided here can be used to get Suko solutions within seconds (if you are feeling a bit lazy).

Below is an example of a Suko grid, where Q and C are scalars given in the puzzle. The variables *x<sub>i,j</sub>* are what we are trying to find.
You can use the following websites to get free Suko problems and test the code: <br/>
http://feeds.thetimes.co.uk/puzzles/public/suko/20210508/863403/ <br/>
https://puzzlemadness.co.uk/suko/medium

<img src="/Suko_image.jpg" alt="Suko example grid"/>

Code dependencies: Pyomo, GLPK solver.

---

## Mathematical Formulation

### Sets & Indices

| Symbol | Description |
|---|---|
| $R = \{1,2,3\}$ | Row indices |
| $C = \{1,2,3\}$ | Column indices |
| $V = \{1,2,\ldots,9\}$ | Possible cell values |
| $S_k \subseteq R \times C,\ k=1,2,3$ | Sets of cells belonging to colour $k$ |
| $Q_j,\ j=1,2,3,4$ | Fixed sets of 4 cells forming each 2×2 quadrant |

### Decision Variables

$$x_{r,c,v} \in \{0,1\} \quad \forall\, r \in R,\ c \in C,\ v \in V$$

$x_{r,c,v} = 1$ if cell $(r,c)$ is assigned value $v$, and $0$ otherwise. There are $3 \times 3 \times 9 = 81$ binary variables in total.

### Objective

$$\min \quad 1$$

The problem is purely feasibility-seeking. The objective is a constant placeholder — any solution satisfying all constraints is optimal.

### Constraints

**C1 — Each value appears exactly once across the grid:**

$$\sum_{r \in R}\sum_{c \in C} x_{r,c,v} = 1 \qquad \forall\, v \in V$$

**C2 — Each cell takes exactly one value:**

$$\sum_{v \in V} x_{r,c,v} = 1 \qquad \forall\, r \in R,\ c \in C$$

**C3 — Colour sum constraints:**

$$\sum_{(r,c)\,\in\, S_k}\ \sum_{v \in V} v \cdot x_{r,c,v} = T_k \qquad k = 1,2,3$$

where $T_k$ is the target sum for colour $k$, provided as an input.

**C4 — Quadrant sum constraints:**

$$\sum_{(r,c)\,\in\, Q_j}\ \sum_{v \in V} v \cdot x_{r,c,v} = P_j \qquad j = 1,2,3,4$$

where $P_j$ is the target sum for quadrant $j$, provided as an input, and the quadrants are fixed as:

| Quadrant | Cells |
|---|---|
| $Q_1$ | $(1,1),\ (1,2),\ (2,1),\ (2,2)$ |
| $Q_2$ | $(1,2),\ (1,3),\ (2,2),\ (2,3)$ |
| $Q_3$ | $(2,1),\ (2,2),\ (3,1),\ (3,2)$ |
| $Q_4$ | $(2,2),\ (2,3),\ (3,2),\ (3,3)$ |

### Problem Size Summary

| Component | Count |
|---|---|
| Binary variables | 81 |
| C1 constraints (no repeated values) | 9 |
| C2 constraints (one value per cell) | 9 |
| C3 constraints (colour sums) | 3 |
| C4 constraints (quadrant sums) | 4 |
| **Total constraints** | **25** |
