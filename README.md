# CS422 Assignment 4 – Arbitrary Traffic Matrix

## Overview

This program uses Gurobi to find the best directed network topology for an arbitrary traffic matrix by maximizing the maximum concurrent flow.

The network consists of 8 nodes, where each node must have exactly 4 incoming and 4 outgoing links. Each directed link has a capacity of 1 unit.

## Requirements

- Python 3
- Gurobi Optimizer
- `gurobipy` Python package
- A valid Gurobi license

Install the Python package using:

```bash
pip install gurobipy
```

## Running the Program

Run the program using:

```bash
python main.py
```

The traffic matrix `T` is defined at the bottom of `main.py`. Modify this matrix to test different traffic demands.

The matrix must satisfy the following conditions:
- It must be 8 × 8.
- All entries must be finite and nonnegative.
- Diagonal entries must be zero.
- Every row and column must sum to at most 4.

## Implementation

The program formulates the network design problem as a Mixed-Integer Linear Program (MILP).

It uses three types of variables:

- `x[i,j]`: Binary variable indicating whether the directed link from node `i` to node `j` exists.
- `f[s,t,i,j]`: Amount of traffic from source `s` to destination `t` routed through link `i → j`.
- `lam`: Common scaling factor applied to all traffic demands.

The model includes constraints to ensure:
- Each node has exactly 4 incoming and 4 outgoing links.
- Total traffic on each link does not exceed its capacity.
- Flow is conserved at every node for each source-destination pair.

The objective is to maximize `lam`, which represents the maximum concurrent flow.

## Output

After solving, the program prints:
- The maximum concurrent flow value (`lambda`).
- The selected directed links forming the optimal topology.

If Gurobi cannot prove optimality, the program prints the solver status instead.

**Note:** The current implementation uses binary link variables, so at most one directed link is allowed between any ordered pair of distinct nodes. An all-zero traffic matrix is handled separately because its maximum concurrent flow factor is unbounded.
