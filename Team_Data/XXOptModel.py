import gurobipy as gp
from gurobipy import GRB
from DataGenerationAndProcessing import get_routes, get_flows, get_parameters


def model_run(FC, VC, B, CAP, M):
    coords, routes_nodes, routes_length, G = get_routes()
    annual_trips = get_flows(coords, routes_length)
    Q, K, N_q, f_q, d_k = get_parameters(routes_nodes, G, annual_trips)

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
        print("\nOptimal Objective Value:", round(model.objVal, 2))
        print("\nCoverage:")
        for od in Q:
            print(f" {od}:", round(y[od].x, 4) * 100, "%")
        print("\nOptimal Solution:")
        for k in K:
            if z[k].x == 1:
                print(f" Node {k}:", round(x[k].x), "modules")
    else:
        print("Optimization problem did not converge to an optimal solution.")