# We run the code in here
#TODO remove all suspicious comments of code....
from DataGenerationAndProcessing import get_routes, get_flows, get_parameters

coords, routes_nodes, routes_length, G = get_routes()
annual_trips = get_flows(coords, routes_length)

Q, K, N_q, f_q, d_k = get_parameters( routes_nodes, G,annual_trips)

# TODO refactor to model generic.py
import gurobipy as gp
from gurobipy import GRB
FC = 20  # Fixed charging station installation cost
VC = 5   # Variable charging station installation cost
B = 100  # Budget
CAP = 8  # Module Cap
M = 999999  # Very large number

# Create a Gurobi model
model = gp.Model("OD_Flow_Maximization")

# Decision variables
y = model.addVars(Q, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
x = model.addVars(K, lb=0, vtype=GRB.INTEGER, name="x")
z = model.addVars(K, vtype=GRB.BINARY, name="z")

# Objective function
model.setObjective(gp.quicksum(f_q[od] * y[od] for od in Q), GRB.MAXIMIZE)

# Constraints
model.addConstrs((gp.quicksum(x[k] / d_k[k] for k in N_q[od]) >= y[od] for od in Q), "Proportion_Refueled")
model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")
model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")
model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station")

# Solve the optimization problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal Objective Value:", model.objVal)
    print("Optimal Solution:")
    for od in Q:
        print(f"y_{od}:", y[od].x)
    for k in K:
        print(f"x_{k}:", x[k].x)
        print(f"z_{k}:", z[k].x)
else:
    print("Optimization problem did not converge to an optimal solution.")