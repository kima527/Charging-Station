import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from DataGenerationAndProcessing import get_flows
#TODO: translate data - for flows we take the same approach as in DataGenerationAndProcessing and distribute them evenly
# on to each path p in each q:(1/3)(1/3)(1/3). E.g. f_q[0]=3 -> f_qp[0]=[1,1,1]. Therefore we import get_flows and apply
# it in line 129. The Translated data has to fit into the model in OptModelExtended and run results.


def get_routesandpaths():

    locations = {
        "Perlach": "Perlach, Munich, Germany",
        "Neuhausen": "Neuhausen, Munich, Germany",
        "Münchener Freiheit": "Münchener Freiheit, Munich, Germany",
        "Thalkirchen": "Thalkirchen, Munich, Germany",
        "Bogenhausen": "Bogenhausen, Munich, Germany",
        "Milbertshofen": "Milbertshofen, Munich, Germany"
    }

    def find_nearest_crossing(G, point, min_edges=4, increment=0.0001):
        while True:
            nearest_node = ox.distance.nearest_nodes(G, point[1], point[0], return_dist=False)
            if G.degree[nearest_node] >= min_edges:
                return nearest_node
            else:
                point = (point[0] + increment, point[1] + increment)

    # Geocode locations
    coords = {name: ox.geocode(loc) for name, loc in locations.items()}

    # Create a network graph for Munich
    G = ox.graph_from_address("Munich, Germany", network_type='drive', dist=5000)

    # Find the nearest crossing nodes to the locations with at least four incident edges
    nearest_crossings = {}
    for name, point in coords.items():
        nearest_crossings[name] = find_nearest_crossing(G, point, min_edges=6)


    # Calculate the shortest paths
    routesandpath_nodes = [
        list(nx.edge_disjoint_paths(G, nearest_crossings["Perlach"], nearest_crossings["Neuhausen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Thalkirchen"], nearest_crossings["Münchener Freiheit"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Bogenhausen"], nearest_crossings["Thalkirchen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Bogenhausen"], nearest_crossings["Neuhausen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Perlach"], nearest_crossings["Milbertshofen"], cutoff=3)),
    ]

    routes_shortestpath_length = {
        "Perlach to Neuhausen": nx.shortest_path_length(G, nearest_crossings["Perlach"], nearest_crossings["Neuhausen"], weight='length'),
        "Thalkirchen to Freimann": nx.shortest_path_length(G, nearest_crossings["Thalkirchen"], nearest_crossings["Münchener Freiheit"], weight='length'),
        "Bogenhausen to Thalkirchen": nx.shortest_path_length(G, nearest_crossings["Bogenhausen"], nearest_crossings["Thalkirchen"], weight='length'),
        "Bogenhausen to Neuhausen": nx.shortest_path_length(G, nearest_crossings["Bogenhausen"], nearest_crossings["Neuhausen"], weight='length'),
        "Perlach to Milbertshofen": nx.shortest_path_length(G, nearest_crossings["Perlach"], nearest_crossings["Milbertshofen"], weight='length'),
    }

    # Initialize a list to store the coordinates of all nodes in each route
    routes_coords = []
    # Define a function to get the coordinates of a node
    """
    def get_coords_from_node(graph, node_id):
        node = graph.nodes[node_id]
        return node['y'], node['x']
    

    # Iterate over each route and extract the coordinates of all nodes
    for route_edge_disjoint_paths in routes:
        route_coords = []
        for edge_disjoint_path in route_edge_disjoint_paths:
            path_coords = [get_coords_from_node(G, node) for node in edge_disjoint_path]
            route_coords.append(path_coords)
        routes_coords.append(route_coords)
        print(route_coords)
    """

    # Plot the graph and routes
    #flattened_routes = [node for route in routesandpath_nodes for node in route]
    #route_colors=['red', 'red', 'red', 'blue', 'blue','blue', 'green', 'green', 'green', 'yellow', 'yellow','yellow', 'orange', 'orange', 'orange']
    #fig, ax = ox.plot_graph_routes(G, flattened_routes, route_colors=route_colors , route_linewidth=6, node_size=8)
    #plt.show()

    return coords, routesandpath_nodes, routes_shortestpath_length, G


def get_parameters_extended(routesandpath_nodes, annual_trips):

    # OD-pairs based on our route_nodes (as indices)
    Q = list(routes_shortestpath_length.keys())

    # Path options
    P = [1,2,3]

    # Nodes based on our route_nodes (as value)
    K = set()
    for route_paths in routesandpath_nodes:
        for path in route_paths:
            K.update(path)
    K = list(K)

    # Set of nodes capable of capturing the flow of OD-pair q, on path p. First path is the main path
    N_qp = routesandpath_nodes

    # Charges/ year of one fast charger
    Charger_annual_capacity = 17520 #30 mins for full charge
    # Flows through OD-pairs - Define based on your scenario
    f_q = {od: flow_value for od, flow_value in zip(Q, [])}
    for od, value in annual_trips.items():
        f_q[od] = value/Charger_annual_capacity

    f_qp = {}
    for od, value in f_q.items():
        f_qp[od] = {int(i): value / 3 for i in range(1, 4)}

    # Initialize d_k dictionary with zeros for all nodes
    d_k = {node: 0 for node in G.nodes}

    # Iterate over the routesandpath_nodes list
    for route_list in routesandpath_nodes:
        for route in route_list:
            for node in route:
                for i in range(1, 4):
                    od_key = int(i)  # Construct the key for the corresponding flow in f_qp
                    flow = f_qp.get(od, {}).get(od_key, 0)  # Get the flow value from f_qp or use 0 if not found
                    d_k[node] += flow

    # d_k now contains the summed demand for each node based on the routes and flows

    return Q, P, K, N_qp, f_q, f_qp, d_k


coords, routesandpath_nodes, routes_shortestpath_length, G = get_routesandpaths()
annual_trips = get_flows(coords,routes_shortestpath_length )
Q, P, K, N_qp, f_q, f_qp, d_k = get_parameters_extended(routesandpath_nodes, annual_trips)