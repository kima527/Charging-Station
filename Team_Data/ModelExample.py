import gurobipy as gp
from gurobipy import GRB

# Set of OD-pairs
Q = [0, 1, 2]  # Replace ... with the actual set of OD-pairs

# Set of path-options for each OD-pair
P = [0, 1, 2]

# Set of nodes
K = list(range(9)) # Replace ... with the actual set of nodes

# Set of nodes capable of capturing the flow of OD-pair q, on path p. First path is the main path - on q=2 we have the same path twice as it is the only option
N_qp = [[[1, 2, 3, 4],[1,0,4],[1,5,4]], [[0, 3, 5],[0,2,5],[0,4,5]], [[4, 6, 8],[4, 6, 8],[4,5,8]]]  # Replace ... with the actual sets of nodes

# Set of flows through OD-pairs q
f_q = {0:8, 1:2, 2:4}  # Replace ... with the actual sets of flows

# Set of flows through path-options of OD-pair q {50%,25%,25%}

f_qp = { 0:{ 0:4, 1:2, 2:2}, 1:{ 0:1, 1:0.5, 2:0.5},2:{0:2,1:1,2:1}}

# Set of flows through node k
#F_k = {0: {0, 1, ...}, 1: {2, 3, ...}, ...}  # Replace ... with the actual sets of flows

# Total demand at node k if OD-pair q has not been served yet - demand at start and end nodes is total demand
#d_k = {(q, k): ... for q in Q for k in K}  # Replace ... with the actual demand values
d_k = {0:4, 1:8, 2:4.5, 3:5, 4:12.5, 5:5, 6:3, 7:0, 8:4}

# Fixed charging station installation cost
FC = 20  # Replace ... with the actual installation costs

# Variable charging station installation cost depending on the number of modules installed
VC = 5  # Replace ... with the actual variable costs

# Budget available
B = 100

# Module Cap
CAP = 8

# Very large number
M = 999999

# Create a Gurobi model
model = gp.Model("OD_Flow_Maximization")

# Decision variables
y = model.addVars(Q,P, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
x = model.addVars(K, lb=0, vtype=GRB.INTEGER, name="x")
z = model.addVars(K, vtype=GRB.BINARY, name="z")

# Objective function
model.setObjective(gp.quicksum(f_qp[q][p] * y[q,p] for q in Q for p in P ), GRB.MAXIMIZE)


# Constraints

model.addConstrs((gp.quicksum(x[k] / d_k[k] for k in N_qp[q][p] ) >= y[q,p] for q in Q for p in P ), "Proportion_Refueled")


model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")

model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")

model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station")

# Solve the optimization problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal Objective Value:", model.objVal)
    print("Optimal Solution:")
    for q in Q:
        for p in P:
            print(f"y_{q}{p}:", y[q,p].x)
    for k in K:
        print(f"x_{k}:", x[k].x)
        print(f"z_{k}:", z[k].x)
else:
    print("Optimization problem did not converge to an optimal solution.")

# Visualization:
# Idea 1: Graph with q on x axis and yq on y axis
# Idea 2: Graph: Several iterations with varying B and FC/VC ratio and its impact on the objective (ratio of total flow covered)
# Idea 4: Bar chart: k on x-axis and xk,dk on y-axis
# Idea 3: In post-processing relate q-keys to coordinates, visualize network and nodes where stations are installed.
#         Then visualize the arcs in colours, depending on how much of their flow is covered.

# Important: Currently the model tries to install as many stations as possible on the node with highest demand -
#            Maybe we should cap x[k] - such that charging stations dont get to overcrowded- just as in this example