
# CS422 Assignment 4 - Arbitrary Traffic Matrix
# Maximum Concurrent Flow and Network Design
#Choosing the option: linear (integer) program formulation
import gurobipy as gp
from gurobipy import GRB
import math

def find_best_topology(T):
    n = 8
    d = 4

    ##input validation
    if len(T) != n:
        raise ValueError("T must have 8 rows")
    for i in range(n):
        # Check that each row has exactly 8 columns
        if len(T[i]) != n:
            raise ValueError("Traffic matrix must be 8x8")

        # Traffic values cannot be negative
        for j in range(n):
            if not math.isfinite(T[i][j]) or T[i][j] < 0:
                raise ValueError("Traffic values must be finite and nonnegative")
        # Nodes cannot send traffic to themselves
        if T[i][i] != 0:
            raise ValueError("Diagonal entries must be zero")

        # Each node can send at most 4 units
        if sum(T[i]) > d + 1e-9:
            raise ValueError("Row sum cannot exceed 4")

    # Each node can receive at most 4 units
    for j in range(n):
        incoming = sum(T[i][j] for i in range(n))

        if incoming > d + 1e-9:
            raise ValueError("Column sum cannot exceed 4")
    ##input validation

    #handling no-traffic case:
    if all(T[i][j] == 0 for i in range(n)
                         for j in range(n)):
        print("Traffic matrix is all zeros.")
        print("No traffic needs to be routed.")
        print("Maximum concurrent flow is unbounded.")
        return None
    #handling no-traffic case

    model = gp.Model("best_topology") #creating an empty optimization model using Gurobi
    #edges holds a list of every possible directed connection between 2 different nodes
        #self loops not allowed, this is the overall candidates Gurobi will choose from
    edges = [(i, j) for i in range(n)
             for j in range(n) if i != j]

    # creates source-destination ordered pairs, we're considering traffic originating at
    # node S that is heading towards node T.
    demands = [(s, t) for s in range(n)
               for t in range(n) if s != t]

    # x[i,j] = number of directed links from i to j
    #this creates one binary decision variable for every edge, x determines network topology
    x = model.addVars(
        edges,
        vtype=GRB.BINARY,
        lb=0,
        name="x"
    )

    #f[s,t,i,j]: traffic originating at node s, traveling towards node t, that travels
    # across the physical connection i -> j
    f = model.addVars(
        [(s, t, i, j) for s, t in demands
                      for i, j in edges],
        vtype=GRB.CONTINUOUS,
        lb=0,
        name="flow"
    )

# constraint: sum of all traffic using a physical link must be <= its capacity


# Maximum concurrent flow factor - how much of each traffic demand the network can
    # simultaneously support
    lam = model.addVar(
        vtype=GRB.CONTINUOUS,
        lb=0,
        name="lambda"
    )

    # Each node has exactly d outgoing links (d = 4)
    model.addConstrs(
        (gp.quicksum(x[i, j] for j in range(n) if i != j) == d
         for i in range(n)),
        name="outdegree"
    )

    # Each node has exactly d incoming links (d = 4)
    model.addConstrs(
        (gp.quicksum(x[j, i] for j in range(n) if i != j) == d
         for i in range(n)),
        name="indegree"
    )

    # Total traffic on a connection cannot exceed the capacity of its physical links
#for every possible physical connection i -> j, this code adds up all the traffic using that connection
    for i, j in edges:
        model.addConstr(
            gp.quicksum(f[s, t, i, j] for s, t in demands)
            <= x[i, j],
            name=f"capacity_{i}_{j}"
        )

    # Flow conservation for each demand: source, intermediate nodes, and then destination
    for s, t in demands:
        for i in range(n):

            outgoing = gp.quicksum(
                f[s, t, i, j]
                for j in range(n) if j != i
            )
            #calculating incoming and outgoing traffic
            incoming = gp.quicksum(
                f[s, t, j, i]
                for j in range(n) if j != i
            )
            #determine the required balance
            if i == s: #case 1: the node is the source
                balance = lam * T[s][t]
            elif i == t: #case 2: the node is the destination
                balance = -lam * T[s][t]
            else: #case 3: the node is an intermediate node
                balance = 0

            model.addConstr( #add the constraint to gurobi
                outgoing - incoming == balance,
                name=f"flow_balance_{s}_{t}_{i}"
            )

    model.setObjective(lam, GRB.MAXIMIZE) #objective here is to maximize concurrent flow

    # Solve the optimization problem
    model.optimize()

    # Extract the solution
    if model.Status == GRB.OPTIMAL: #check gurobi has proved optimality
        print("\nMaximum concurrent flow:", lam.X)
        print("\nBest topology:")

        for i, j in edges: #print the selected links
            if x[i, j].X > 0.5:
                print(f"{i} -> {j}: {round(x[i, j].X)} link(s)")

    else:
        print("Gurobi did not prove an optimal solution.")
        print("Solver status:", model.Status)

    return model


# traffic matrix being used for input:
T = [[0.0 for j in range(8)] for i in range(8)]

for i in range(8):
    T[i][(i + 1) % 8] = 1.5
    T[i][(i + 2) % 8] = 1.5
    T[i][(i + 3) % 8] = 1.0

find_best_topology(T)