import gurobipy as gp
from gurobipy import GRB
import DataGenerationAndProcessing as data
import DataGenerationAndProcessingExtended as extendData
import osmnx as ox
import matplotlib.pyplot as plt


class Model:  # base model and extended model

    def __init__(self, FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G,
                 is_extended=False, N_qp=None, f_qp=None, P=None):
        self.FC = FC
        self.VC = VC
        self.B = B
        self.CAP = CAP
        self.M = M
        self.Q = Q
        self.P = P
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
                     f_qp=None, P=None):

        if self.is_extended:
            coords, routesandpath_nodes, routes_shortestpath_length, G = extendData.get_routesandpaths()
            annual_trips = data.get_flows(coords, routes_shortestpath_length)
            Q, P, K, N_qp, f_q, f_qp, d_k = extendData.get_parameters_extended(routesandpath_nodes, annual_trips,
                                                                               routes_shortestpath_length, G)

            for q in Q:  # Iterate through each OD pair in Q
                for p in f_qp[q]:  # Iterate through each path for the OD pair
                    demand_value = f_qp[q][p]  # Access the demand value for this path
                    # Print the demand, rounding the value for readability, and formatting the string as required
                    print(f"Demand from {q} path {p}: {round(demand_value, 2)} per 30 minutes")

        # Create Gurobi model and set solving time limit to 2 minutes
        model = gp.Model("OD_Flow_Maximization")
        model.setParam('TimeLimit', 120)

        # Decision variables as in mathematical model description
        global x, y, z
        if self.is_extended:
            y = model.addVars(self.Q, P, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
        else:
            y = model.addVars(self.Q, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
        x = model.addVars(self.K, lb=0, vtype=GRB.INTEGER, name="x")
        z = model.addVars(self.K, vtype=GRB.BINARY, name="z")

        # Objective function as in mathematical model description
        if self.is_extended:
            model.setObjective(gp.quicksum(f_qp[q][p] * y[q, p] for q in Q for p in P), GRB.MAXIMIZE)
        else:
            model.setObjective(gp.quicksum(self.f_q[od] * y[od] for od in self.Q), GRB.MAXIMIZE)

        # Constraints as in mathematical model description
        if self.is_extended:
            model.addConstrs((gp.quicksum(x[k] / self.d_k[k] for k in N_qp[q][p]) >= y[q, p] for q in Q for p in P),
                             "Proportion_Refueled")
            model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")
            model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")
            model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station")
            # Uncomment for minimum service constraint and set value accordingly
            model.addConstrs((y[q, p] >= 0.4 for q in Q for p in P), "Minimum service ratio for all paths, when total service ratio >= minimum service ratio")

        else:
            model.addConstrs((gp.quicksum(x[k] / self.d_k[k] for k in self.N_q[od]) >= y[od] for od in self.Q),
                             "Proportion_Refueled")
            model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")
            model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")
            model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station")
            # Uncomment for minimum service constraint and set value accordingly
            #model.addConstrs((y[od] >= 0.5 for od in Q),"Minimum service ratio for all paths, when total service ratio >= minimum service ratio")

        return model

    def print_result(self, model):
        P = [1, 2, 3]
        result_locations = []

        if model.status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
            print("\nOptimal Objective Value:", round(model.objVal, 2))
            print("Final MIP gap value: %f" % model.MIPGap)
            print("\nCoverage:")
            if self.is_extended:
                for od in self.Q:
                    for p in P:
                        print(f"{od} path {p}: {round(y[od, p].x, 4) * 100}%")
            else:
                for od in self.Q:
                    print(f" {od}:", round(y[od].x, 4) * 100, "%")
            print("\nOptimal Solution:")

            #Uncomment this block for visualizing relative tour coverage (In the case of extended, only for equal flow dist!)

            q_values =12
            yq = []

            if self.is_extended:
                for od in self.Q:  # Assuming q_values is the number of OD-tours
                    yq.append(sum(y[od, p].X for p in P)/3)

            else:
                for od in self.Q:
                    yq.append(y[od].X)

            plt.bar(range(q_values), yq, color='blue')

            plt.xticks(range(q_values), range(q_values))

            plt.xlabel('OD-Tour, q')
            plt.ylabel('y[q]')
            plt.title('Relative coverage of OD-Tours with a Budget of $'+ str(self.B/1000) +'Mil ')
            plt.ylim(0,1.2)
            plt.show()


            # Node output for visualization. Uncomment for visualization
            """
            for k in self.K:
                if z[k].x == 1:
                    print(f" Node {k}:", round(x[k].x), "modules")
                    node_coords = self.get_node_coordinates(k)
                    result_locations.append(node_coords)
                    
            """
        else:
            print("Optimization problem did not converge to an optimal solution.")

        self.result_locations = result_locations

    def run(self):
        if self.is_extended:
            model = self.create_model(self.FC, self.VC, self.B, self.CAP, self.M, self.Q, self.K, self.N_q, self.f_q,
                                      self.d_k, self.coord, self.routes_nodes, self.routes_length, self.G, self.N_qp,
                                      self.f_qp, self.P)
        else:
            model = self.create_model(self.FC, self.VC, self.B, self.CAP, self.M, self.Q, self.K, self.N_q, self.f_q,
                                      self.d_k, self.coord, self.routes_nodes, self.routes_length, self.G)
        model.optimize()
        objective = model.objVal
        gap = model.MIPGap
        self.print_result(model)
        return objective, gap

    def get_node_coordinates(self, node_id):
        G = ox.graph_from_address("Munich, Germany", network_type='drive', dist=5000)
        x, y = G.nodes[node_id]['x'], G.nodes[node_id]['y']
        return (x, y)
