import gurobipy as gp
from gurobipy import GRB

# Set of OD-pairs
Q = [0, 1, 2]  # Replace ... with the actual set of OD-pairs

# Set of nodes
K = list(range(9)) # Replace ... with the actual set of nodes

# Set of nodes capable of capturing the flow of OD-pair q
N_q = [[1, 2, 3, 4], [0, 3, 5], [4, 6, 8]]  # Replace ... with the actual sets of nodes

# Set of flows through OD-pairs q
f_q = {0:6, 1:2, 2:4}  # Replace ... with the actual sets of flows

# Set of flows through node k
#F_k = {0: {0, 1, ...}, 1: {2, 3, ...}, ...}  # Replace ... with the actual sets of flows

# Total demand at node k if OD-pair q has not been served yet
#d_k = {(q, k): ... for q in Q for k in K}  # Replace ... with the actual demand values
d_k = {0:2, 1:6, 2:6, 3:8, 4:10, 5:2, 6:4, 7:0, 8:4}

# Fixed charging station installation cost
FC = 10  # Replace ... with the actual installation costs

# Variable charging station installation cost depending on the number of modules installed
VC = 5  # Replace ... with the actual variable costs

# Budget available
B = 15

# Parameter that caps the available capacity of each station to a fraction of its real capacity
ConCap = 0.8

# Very large number
M = 999999

# Create a Gurobi model
model = gp.Model("OD_Flow_Maximization")

# Decision variables
y = model.addVars(Q, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
x = model.addVars(K, lb=0, vtype=GRB.INTEGER, name="x")
z = model.addVars(K, vtype=GRB.BINARY, name="z")

# Objective function
model.setObjective(gp.quicksum(f_q[q] * y[q] for q in Q ), GRB.MAXIMIZE)


# Constraints

model.addConstrs((gp.quicksum(x[k] / d_k[k] for k in N_q[q] ) >= y[q] for q in Q), "Proportion_Refueled")


model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")

model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")


# Solve the optimization problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal Objective Value:", model.objVal)
    print("Optimal Solution:")
    for q in Q:
        print(f"y_{q}:", y[q].x)
    for k in K:
        print(f"x_{k}:", x[k].x)
        print(f"z_{k}:", z[k].x)
else:
    print("Optimization problem did not converge to an optimal solution.")

