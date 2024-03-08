import gurobipy as gp
from gurobipy import GRB
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Example Data----------------------------------------------------------------------------------------------------------

#Coordinates of K
Coordinates = [[3,4],[1,3],[2,3],[3,3],[4,3],[3,2],[4,2],[5,2],[4,1]]

# Set of OD-pairs
Q = [0, 1, 2]

# Set of path-options for each OD-pair
P = [0, 1, 2]

# Set of nodes
K = list(range(9))

# Set of nodes capable of capturing the flow of OD-pair q, on path p. First path is the main path - on q=2 we have the same path twice as it is the only option
N_qp = [[[1, 2, 3, 4], [1, 0, 4], [1, 5, 4]], [[0, 3, 5], [0, 2, 5], [0, 4, 5]],
        [[4, 6, 8], [4, 6, 8], [4, 5, 8]]]

# Set of flows through OD-pairs q
f_q = {0: 9, 1: 6, 2: 3}  # Replace ... with the actual sets of flows

# Set of flows through path-options of OD-pair q {50%,25%,25%}

f_qp = {0: {0: 3, 1: 3, 2: 3}, 1: {0: 2, 1: 2, 2: 2}, 2: {0: 1, 1: 1, 2: 1}}

# Set of flows through node k
# F_k = {0: {0, 1, ...}, 1: {2, 3, ...}, ...}  # Repetitive since we have Nqp

# Total demand at node k if OD-pair q has not been served yet - demand at start and end nodes is total demand
d_k = {0: 6, 1: 9, 2: 5, 3: 5, 4: 14, 5: 10, 6: 2, 7: 0, 8: 3}

# Fixed charging station installation cost
FC = 21

# Variable charging station installation cost depending on the number of modules installed
VC = 20
# Reliable data on the ratio FC/VC: https://afdc.energy.gov/files/u/publication/evse_cost_report_2015.pdf
# Ratio is 1:1, see article page 30
# Values in 1000$

# Budget available
B = 250

# Module Cap
CAP = 8

# Model---------------------------------------------------------------------------------------------------------------
def create_model(B,Q,P,K,N_qp,f_qp,d_k,FC,VC,CAP):


    # Very large number
    M = 999999

    # Create a Gurobi model
    model = gp.Model("OD_Flow_Maximization")

    # Decision variables
    global y
    global x
    y = model.addVars(Q,P, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="y")
    x = model.addVars(K, lb=0, vtype=GRB.INTEGER, name="x")
    z = model.addVars(K, vtype=GRB.BINARY, name="z")

    # Objective function
    model.setObjective(gp.quicksum(f_qp[q][p] * y[q,p] for q in Q for p in P ), GRB.MAXIMIZE)


    # Constraints

    model.addConstrs((gp.quicksum(x[k] / d_k[k] for k in N_qp[q][p] ) >= y[q,p] for q in Q for p in P ), "Proportion_Refueled")


    model.addConstr(gp.quicksum(z[k] * FC + x[k] * VC for k in K) <= B, "Budget_Constraint")

    model.addConstrs((x[k] <= z[k] * M for k in K), "Module_Capacity")

    model.addConstrs((x[k] <= CAP for k in K), "Cap on modules at one station") # against congestion

    return model


def print_modelresults(model):
    variables = model.getVars()

    for variable in variables:
        var_name = variable.VarName
        var_value = variable.X
        print(f"{var_name}: {var_value}")
    # Print the objective value
    print(f"Objective Value: {model.objVal}")


# Visualization---------------------------------------------------------------------------------------------------------


def visualize_network(coordinates, N_qp,f_qp, d_k):
    G = nx.Graph()

    # Add nodes and edges
    for i, coord in enumerate(coordinates):
        G.add_node(i, pos=(coord[0], coord[1]))

    # Add demand as labels next to nodes
    node_labels = {}
    for node, demand in d_k.items():
        x, y = coordinates[node]
        node_labels[node] = {'demand': demand, 'pos': (x, y - 0.2)}

    # Iterate over paths and add edges with flow volumes
    for q, paths in enumerate(N_qp):
        for p, path in enumerate(paths):
            edge_color = 'blue' if p == 0 else 'grey'
            for i in range(len(path) - 1):
                edge = (path[i], path[i + 1])
                flow = f_qp[q][p]
                if G.has_edge(*edge):
                    # If the edge already exists, update the flow
                    G[edge[0]][edge[1]]['flow'] += flow
                else:
                    # If the edge does not exist, add it with the flow
                    G.add_edge(*edge, color=edge_color, flow=flow)

    # Get positions
    pos = nx.get_node_attributes(G, 'pos')

    # Draw the graph
    edges = G.edges()
    edge_colors = [G[u][v]['color'] for u, v in edges]
    edge_labels = {(u, v): G[u][v]['flow'] for u, v in edges}

    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=8, edge_color=edge_colors)

    # Draw labels next to nodes
    for node, label in node_labels.items():
        x, y = label['pos']
        demand = label['demand']
        plt.text(x, y, f'Demand: {demand}', fontsize=8, ha='center', va='center',
                 bbox=dict(facecolor='white', alpha=0.7))

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Display the graph
    plt.show()


def visualize_ODflowdemandcoverage(Q,P,f_q,f_qp,B):   # Graph with q on x axis and yq on y axis.

    q_values = len(Q)
    num_paths = len(P)

    yq=[]

    for q in range(q_values):
        sum=0
        for p in range(num_paths):
            sum+= ((y[q, p].X)*f_qp[q][p])/f_q[q]
            #Yqp now only gives us the fraction of which path option p is refueled
        yq.append(sum)
    print(yq)

    plt.bar(range(q_values), yq, color='blue')

    plt.xticks(range(q_values), range(q_values))

    plt.xlabel('OD-Tour, q')
    plt.ylabel('y[q]')
    plt.title('Relative coverage of OD-Tours with a Budget of ' + str(B))

    plt.show()


def visualize_nodedemandocoverage(K,d_k, B):        # Bar chart: k on x-axis and xk,dk on y-axis.
                                                    # How does demand intensity at nodes relate to stations installed?
                                                    # Note: d[k] does not have to be covered at every node to fully cover f_qp
    bar_positions = np.arange(len(K))
    bar_width = 0.35  # Adjust the width as needed

    # Create bar chart
    plt.bar(bar_positions, [x[k].X for k in K], width=bar_width, label='x[k]', color='blue')
    plt.bar(bar_positions + bar_width, [d_k[k] for k in K], width=bar_width, label='d[k]', color='orange')

    # Add labels and title
    plt.xlabel('Node, k')
    plt.ylabel('Flow in vehicles/period')
    plt.title('Stations installed respective demand intensity with a Budget of ' + str(B))
    plt.xticks(bar_positions + bar_width / 2, K)  # Center x-tick labels between bars
    plt.legend()

    plt.show()


# Solving model---------------------------------------------------------------------------------------------------------

def get_modelresults(B, Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP):

    visualize_network(Coordinates, N_qp, f_qp, d_k)

    model = create_model(B, Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP)

    model.optimize()

    print_modelresults(model)

    visualize_ODflowdemandcoverage(Q,P,f_q, f_qp, B)
    visualize_nodedemandocoverage(K, d_k, B)


# Several iterations with varying B and FC/VC ratio and its impact on the objective (ratio of total flow covered)
# Visualize in Graph
def get_modelresults_budgetiterations(Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP):

    Iterations = range(15)
    Initial_budget = 80
    Budget_steps = 15
    B = Initial_budget

    visualize_network(Coordinates, N_qp, f_qp, d_k)

    budget_values = []
    objective_values = []

    for i in Iterations:

        model = create_model(B, Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP)

        model.optimize()
        objective = model.objVal

        print("ITERATION", i, "BUDGET", B)
        print_modelresults(model)

        visualize_ODflowdemandcoverage(Q,P,f_q,f_qp,B)
        visualize_nodedemandocoverage(K, d_k, B)

        budget_values.append(B)
        objective_values.append(objective)

        B += Budget_steps

    # Plotting the graph
    plt.plot(budget_values, objective_values, marker='o')
    plt.xlabel('Budget')
    plt.ylabel('Flow covered')
    plt.title('Objective Value related to Budget')
    plt.grid(True)
    plt.show()



#TODO In post-processing relate q-keys to coordinates, visualize network and nodes where stations are installed.----
#     Then visualize the arcs in colours, depending on how much of their flow is covered.---------------------------

get_modelresults(B, Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP)
#get_modelresults_budgetiterations(Q, P, K, N_qp, f_qp, d_k, FC, VC, CAP)