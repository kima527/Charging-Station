import warnings
import osmnx as ox
import networkx as nx
import math
from geopy.distance import great_circle

warnings.filterwarnings("ignore", category=DeprecationWarning)


# ---------------------------------------------------Data gathering----------------------------------------------------

def get_routes():
    # Define locations
    locations = {
        "Marienplatz": "Marienplatz, Munich, Germany",
        "Olympiapark": "Olympiapark, Munich, Germany",
        "HBF": "Hauptbahnhof, Munich, Germany",
        "BMW": "BMW Welt, Munich, Germany",
        "TUM City Center": "Arcisstraße 21, 80333 Munich, Germany",
        "Münchener Freiheit": "Münchener Freiheit, Munich, Germany"
    }

    # Geocode locations
    coords = {name: ox.geocode(loc) for name, loc in locations.items()}

    # Create a network graph for Munich
    G = ox.graph_from_address("Munich, Germany", network_type='drive', dist=3000)

    # Find the nearest nodes to the locations
    nearest_nodes = {name: ox.distance.nearest_nodes(G, point[1], point[0]) for name, point in coords.items()}

    # Calculate the shortest paths
    routes_nodes = {
        "Marienplatz to Olympiapark": nx.shortest_path(G, nearest_nodes["Marienplatz"], nearest_nodes["Olympiapark"], weight='length'),
        "Olympiapark to HBF": nx.shortest_path(G, nearest_nodes["Olympiapark"], nearest_nodes["HBF"], weight='length'),
        "HBF to BMW": nx.shortest_path(G, nearest_nodes["HBF"], nearest_nodes["BMW"], weight='length'),
        "BMW to TUM City Center": nx.shortest_path(G, nearest_nodes["BMW"], nearest_nodes["TUM City Center"], weight='length'),
        "TUM City Center to Münchener Freiheit": nx.shortest_path(G, nearest_nodes["TUM City Center"], nearest_nodes["Münchener Freiheit"], weight='length'),
        "Münchener Freiheit to Olympiapark": nx.shortest_path(G, nearest_nodes["Münchener Freiheit"], nearest_nodes["Olympiapark"], weight='length'),
    }

    routes_length = {
        "Marienplatz to Olympiapark": nx.shortest_path_length(G, nearest_nodes["Marienplatz"], nearest_nodes["Olympiapark"], weight='length'),
        "Olympiapark to HBF": nx.shortest_path_length(G, nearest_nodes["Olympiapark"], nearest_nodes["HBF"], weight='length'),
        "HBF to BMW": nx.shortest_path_length(G, nearest_nodes["HBF"], nearest_nodes["BMW"], weight='length'),
        "BMW to TUM City Center": nx.shortest_path_length(G, nearest_nodes["BMW"], nearest_nodes["TUM City Center"], weight='length'),
        "TUM City Center to Münchener Freiheit": nx.shortest_path_length(G, nearest_nodes["TUM City Center"], nearest_nodes["Münchener Freiheit"], weight='length'),
        "Münchener Freiheit to Olympiapark": nx.shortest_path_length(G, nearest_nodes["Münchener Freiheit"], nearest_nodes["Olympiapark"], weight='length'),
    }

    return coords, routes_nodes, routes_length, G


def get_flows(coords, routes_length):

    def calculate_centroid(coords):
        latitudes = [coord[0] for coord in coords.values()]
        longitudes = [coord[1] for coord in coords.values()]
        return sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)

    # Calculate the centroid of the nodes
    centroid = calculate_centroid(coords)

    # Function to calculate distance between two points
    def calculate_distance(point1, point2):
        return great_circle(point1, point2).kilometers

    # Find the maximum distance from the centroid to any node
    max_distance_to_centroid = max(calculate_distance(centroid, point) for point in coords.values())

    # Calculate the area of the circle
    area_of_circle = math.pi * (max_distance_to_centroid ** 2)

    # Munich's population density (people per square km)
    population_density = 4900  # Adjust as needed

    # Calculate C based on the area and population density
    C = area_of_circle * population_density

    # Custom function to estimate trips
    def estimate_trips(distance, C, alpha):
        return C * math.exp(-alpha * distance)

    # Constants for the model
    alpha = 0.1  # Decay constant, adjust based on scenario

    # Calculate estimated trips for each route
    estimated_trips = {}
    for route in routes_length.keys():
        distance = routes_length[route] / 1000  # Distance for the route in km
        trips = estimate_trips(distance, C, alpha)
        estimated_trips[route] = trips

    # Assuming 220 working days a year
    annual_trips = {route: trips * 260 for route, trips in estimated_trips.items()}

    # Print the estimated annual trips for each route
    for route, trips in annual_trips.items():
        print(f"{route}: {trips} trips/year")

    return annual_trips

# -------------------------------------------------------------Data translation-----------------------------------------


def get_parameters( routes_nodes, G,annual_trips):
    # OD-pairs based on our route_nodes (as strings)
    Q = list(routes_nodes.keys())

    # Nodes based on our route_nodes (as value)#Todo which value? Indexes from 1... might be better?
    K = set()
    for route in routes_nodes.values():
        K.update(route)
    K = list(K)

    # Nodes capable of capturing the flow of OD-pair q
    N_q = {od: routes_nodes[od] for od in Q}

    # Charges/ year of one fast charger
    Charger_annual_capacity = 17520 #30 mins for full charge
    # Flows through OD-pairs - Define based on your scenario
    f_q = {od: flow_value for od, flow_value in zip(Q, [])}
    for od, value in annual_trips.items():
        f_q[od] = value/Charger_annual_capacity

    # Initialize d_k with zeros for all nodes
    d_k = {node: 0 for node in G.nodes()}

    # Iterate over each OD pair and its route
    for od, route in routes_nodes.items():
        flow = f_q[od]  # Flow for the current OD pair
        for node in route:
            d_k[node] += flow  # Add the flow to the demand of the node

    for od, route in N_q.items():
        print(f"OD Pair '{od}' with flow {f_q[od]} per 30 minutes:")
        for node in route:
            print(f"  Node {node} has demand {d_k[node]}")

    # d_k now contains the summed demand for each node based on the routes and flows

    return Q, K, N_q, f_q, d_k

