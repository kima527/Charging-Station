import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt


locations = {
    "Ostbahnhof": "Ostbahnhof, Munich, Germany",
    "Olympiapark": "Olympiapark, Munich, Germany",
    "HBF": "Hauptbahnhof, Munich, Germany",
    "BMW": "BMW Welt, Munich, Germany",
    "TUM City Center": "Arcisstraße 21, 80333 Munich, Germany",
    "Münchener Freiheit": "Münchener Freiheit, Munich, Germany"
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
routes = [
    list(nx.node_disjoint_paths(G, nearest_crossings["Ostbahnhof"], nearest_crossings["Olympiapark"], cutoff=4)),
    list(nx.edge_disjoint_paths(G, nearest_crossings["HBF"], nearest_crossings["BMW"], cutoff=4)),
    list(nx.edge_disjoint_paths(G, nearest_crossings["Münchener Freiheit"], nearest_crossings["TUM City Center"], cutoff=4)),
    list(nx.edge_disjoint_paths(G, nearest_crossings["Münchener Freiheit"], nearest_crossings["Olympiapark"], cutoff=4)),
    list(nx.edge_disjoint_paths(G, nearest_crossings["TUM City Center"], nearest_crossings["Ostbahnhof"], cutoff=4)),
]
flattened_routes = [node for route in routes for node in route]
print(len(routes[0]))
print(len(routes[1]))
print(len(routes[2]))
print(len(routes[3]))
print(len(routes[4]))
print(routes)


# Initialize a list to store the coordinates of all nodes in each route
routes_coords = []
# Define a function to get the coordinates of a node
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

route_colors=['red', 'red', 'blue', 'blue', 'green', 'green', 'green', 'yellow', 'yellow', 'orange', 'orange', 'orange']
# Plot the graph and routes
fig, ax = ox.plot_graph_routes(G, flattened_routes, route_colors=route_colors , route_linewidth=6, node_size=8)
plt.show()

