import gurobipy as gp
from gurobipy import GRB
import DataGenerationAndProcessing as data
import DataGenerationAndProcessingExtended as extendData

class Model:

    def __init__(self, FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, is_extended=False, N_qp=None, f_qp=None):
        self.FC = FC
        self.VC = VC
        self.B = B
        self.CAP = CAP
        self.M = M
        self.Q = Q
        self.K = K
        self.N_q = N_q
        self.f_q = f_q
        self.d_k = d_k
        self.coord = coords
        self.routes_nodes = routes_nodes
        self.routes_length = routes_length
        self.G = G
        self.is_extended = is_extended
        self.N_qp = N_qp
        self.f_qp = f_qp

    def create_model(self, FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, N_qp=None,
                     f_qp=None):
        if self.is_extended:
            coords, routesandpath_nodes, routes_shortestpath_length, G = extendData.get_routesandpaths()
            annual_trips = data.get_flows(coords, routes_shortestpath_length)
            Q, P, K, N_qp, f_q, f_qp, d_k = extendData.get_parameters_extended(routesandpath_nodes, annual_trips)

        # Create a Gurobi model
        model = gp.Model("OD_Flow_Maximization")

        # Decision variables
        global x, y, z
        y = model.addVars(self.Q, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
        x = model.addVars(self.K, lb=0, vtype=GRB.INTEGER, name="x")
        z = model.addVars(self.K, vtype=GRB.BINARY, name="z")

        # Objective function
        if self.is_extended:
            model.setObjective(gp.quicksum(f_qp[q][p] * y[q, p] for q in Q for p in P), GRB.MAXIMIZE)
        else:
            model.setObjective(gp.quicksum(self.f_q[od] * y[od] for od in self.Q), GRB.MAXIMIZE)

        # Constraints
        if self.is_extended:
            model.addConstrs((gp.quicksum(x[k] / self.d_k[k] for k in N_qp[q][p]) >= y[q, p] for q in Q for p in P), "Proportion_Refueled")
        else:
            model.addConstrs((gp.quicksum(x[k] / self.d_k[k] for k in self.N_q[od]) >= y[od] for od in self.Q), "Proportion_Refueled")
            model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")
            model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")
            model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station")

        return model

    def print_result(self, model):
        if model.status == GRB.OPTIMAL:
            print("\nOptimal Objective Value:", round(model.objVal, 2))
            print("\nCoverage:")
            for od in self.Q:
                print(f" {od}:", round(y[od].x, 4) * 100, "%")
            print("\nOptimal Solution:")
            for k in self.K:
                if z[k].x == 1:
                    print(f" Node {k}:", round(x[k].x), "modules")
        else:
            print("Optimization problem did not converge to an optimal solution.")

    def run(self):
        if self.is_extended:
            model = self.create_model(self.FC, self.VC, self.B, self.CAP, self.M, self.Q, self.K, self.N_qp, self.f_qp,
                                      self.d_k, self.coord, self.routes_nodes, self.routes_length, self.G)
        else:
            model = self.create_model(self.FC, self.VC, self.B, self.CAP, self.M, self.Q, self.K, self.N_q, self.f_q,
                                  self.d_k, self.coord, self.routes_nodes, self.routes_length, self.G)
        model.optimize()
        self.print_result(model)

