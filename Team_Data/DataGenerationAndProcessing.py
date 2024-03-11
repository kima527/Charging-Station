import warnings
import osmnx as ox
import networkx as nx
import math
from geopy.distance import great_circle

warnings.filterwarnings("ignore", category=DeprecationWarning)


# ---------------------------------------------------Data gathering----------------------------------------------------


def get_routes(): # Loads locations of denseley populated areas and connects them via shortest path (OD-pair creation)

    locations = {
        "Perlach": "Perlach, Munich, Germany",
        "Neuhausen": "Neuhausen, Munich, Germany",
        "Freimann": "Münchener Freiheit, Munich, Germany",
        "Thalkirchen": "Thalkirchen, Munich, Germany",
        "Bogenhausen": "Bogenhausen, Munich, Germany",
        "Feldmoching": "Feldmoching, Munich, Germany",
        "Hadern": "Hadern, Munich, Germany",
        "Moosach": "Claudiusplatz, Munich, Germany",
        "Oberfoehring": "Bürgerpark Oberföhring, Munich, Germany",
        "Berg-am-Laim": "Sankt Pius, Munich, Germany",
        "Giesing": "Wettersteinplatz, Munich, Germany",
        "Sendling": "Pilsenseestraße, Munich, Germany",
        "Stachus": "Karlsplatz, Munich, Germany",
        "Sendlinger-Tor": "Sendlinger-Tor-Platz 14, Munich, Germany",
        "Isartor": "Isartor/Zweibrückenstr., Munich, Germany",
        "Odeonsplatz": "Odeonsplatz, Munich, Germany"
    }

    # Geocode locations
    coords = {name: ox.geocode(loc) for name, loc in locations.items()}

    # Create a network graph for Munich of a reasonable size
    G = ox.graph_from_address("Munich, Germany", network_type='drive', dist=5000)

    # Find the nearest nodes to the locations
    nearest_nodes = {name: ox.distance.nearest_nodes(G, point[1], point[0]) for name, point in coords.items()}


    # Connect OD-pairs via shortest path and store route coordinates
    routes_nodes = {
        "Perlach to Neuhausen": nx.shortest_path(G, nearest_nodes["Perlach"], nearest_nodes["Neuhausen"],weight='length'),
        "Thalkirchen to Freimann": nx.shortest_path(G, nearest_nodes["Thalkirchen"], nearest_nodes["Freimann"],weight='length'),
        "Bogenhausen to Thalkirchen": nx.shortest_path(G, nearest_nodes["Bogenhausen"], nearest_nodes["Thalkirchen"],weight='length'),
        "Bogenhausen to Neuhausen": nx.shortest_path(G, nearest_nodes["Bogenhausen"], nearest_nodes["Neuhausen"],weight='length'),
        "Perlach to Freimann": nx.shortest_path(G, nearest_nodes["Perlach"], nearest_nodes["Freimann"],weight='length'),
        "Hadern to Stachus": nx.shortest_path(G, nearest_nodes["Hadern"], nearest_nodes["Stachus"],weight='length'),
        "Moosach to Stachus": nx.shortest_path(G, nearest_nodes["Moosach"], nearest_nodes["Stachus"],weight='length'),
        "Feldmoching to Odeonsplatz": nx.shortest_path(G, nearest_nodes["Feldmoching"], nearest_nodes["Odeonsplatz"],weight='length'),
        "Oberfoehring to Odeonsplatz": nx.shortest_path(G, nearest_nodes["Oberfoehring"], nearest_nodes["Odeonsplatz"],weight='length'),
        "Berg-am-Laim to Isartor": nx.shortest_path(G, nearest_nodes["Berg-am-Laim"], nearest_nodes["Isartor"],weight='length'),
        "Giesing to Sendlinger-Tor": nx.shortest_path(G, nearest_nodes["Giesing"], nearest_nodes["Sendlinger-Tor"],weight='length'),
        "Sendling to Sendlinger-Tor": nx.shortest_path(G, nearest_nodes["Sendling"], nearest_nodes["Sendlinger-Tor"], weight='length'),
    }

    # Stores the distance between OD-pairs
    routes_length = {
        "Perlach to Neuhausen": nx.shortest_path_length(G, nearest_nodes["Perlach"], nearest_nodes["Neuhausen"],weight='length'),
        "Thalkirchen to Freimann": nx.shortest_path_length(G, nearest_nodes["Thalkirchen"], nearest_nodes["Freimann"],weight='length'),
        "Bogenhausen to Thalkirchen": nx.shortest_path_length(G, nearest_nodes["Bogenhausen"], nearest_nodes["Thalkirchen"],weight='length'),
        "Bogenhausen to Neuhausen": nx.shortest_path_length(G, nearest_nodes["Bogenhausen"], nearest_nodes["Neuhausen"],weight='length'),
        "Perlach to Freimann": nx.shortest_path_length(G, nearest_nodes["Perlach"], nearest_nodes["Freimann"],weight='length'),
        "Hadern to Stachus": nx.shortest_path_length(G, nearest_nodes["Hadern"], nearest_nodes["Stachus"],weight='length'),
        "Moosach to Stachus": nx.shortest_path_length(G, nearest_nodes["Moosach"], nearest_nodes["Stachus"],weight='length')
        "Feldmoching to Odeonsplatz": nx.shortest_path_length(G, nearest_nodes["Feldmoching"], nearest_nodes["Odeonsplatz"],weight='length'),
        "Oberfoehring to Odeonsplatz": nx.shortest_path_length(G, nearest_nodes["Oberfoehring"], nearest_nodes["Odeonsplatz"],weight='length'),
        "Berg-am-Laim to Isartor": nx.shortest_path_length(G, nearest_nodes["Berg-am-Laim"], nearest_nodes["Isartor"],weight='length'),
        "Giesing to Sendlinger-Tor": nx.shortest_path_length(G, nearest_nodes["Giesing"], nearest_nodes["Sendlinger-Tor"],weight='length'),
        "Sendling to Sendlinger-Tor": nx.shortest_path_length(G, nearest_nodes["Sendling"], nearest_nodes["Sendlinger-Tor"], weight='length'),
    }

    print(routes_length)
    return coords, routes_nodes, routes_length, G


def get_flows(coords, routes_length): # Generate annual flow volumes on OD-paths

    # Function calculating centroids for given coordinates
    def calculate_centroid(coords):
        latitudes = [coord[0] for coord in coords.values()]
        longitudes = [coord[1] for coord in coords.values()]
        return sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)

    # Store the centroid of the nodes
    centroid = calculate_centroid(coords)

    # Function to calculate distance between two points
    def calculate_distance(point1, point2):
        return great_circle(point1, point2).kilometers

    # Store the maximum distance from the centroid to any node
    max_distance_to_centroid = max(calculate_distance(centroid, point) for point in coords.values())

    # Store the area of the circle
    area_of_circle = math.pi * (max_distance_to_centroid ** 2)

    # Munich's population density (people per square km): https://en.wikipedia.org/wiki/Munich
    population_density = 4900

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

    # Storing annual trips, assuming 230 working days a year https://www.steuergo.de/en/rechner/arbeitstage
    annual_trips = {route: trips * 230 for route, trips in estimated_trips.items()}

    return annual_trips

# -------------------------------------------------------------Data translation-----------------------------------------


def get_parameters(routes_nodes, G, annual_trips): # Generate all necessary parameters for the base model based on data pre-processing

    # OD-pairs based on our route_nodes sets (as strings)
    Q = list(routes_nodes.keys())

    # Nodes based on our route_nodes values within sets (as value)
    K = set()
    for route in routes_nodes.values():
        K.update(route)
    K = list(K)

    # Nodes capable of capturing the flow of OD-pair q
    N_q = {od: routes_nodes[od] for od in Q}

    # Charges/ year of one fast charger (assuming demand only on the 230 working days) with 30 mins for full charge
    Charger_annual_capacity = 11040 #vehicles/yr
    EVsPerCapitaGer = 15.6/1000
    # Flows through OD-pairs on each 30 mins
    f_q = {od: flow_value for od, flow_value in zip(Q, [])}
    for od, value in annual_trips.items():
        f_q[od] = (value/Charger_annual_capacity)*EVsPerCapitaGer

    # Summed demand on node keK based on all flows
    d_k = {node: 0 for node in G.nodes()}
    for od, route in routes_nodes.items():
        flow = f_q[od]  # Flow for the current OD pair
        for node in route:
            d_k[node] += flow  # Add the flow to the demand of the node

    for od, route in N_q.items():
        print(f"OD Pair '{od}' with flow {f_q[od]} per 30 minutes:")
        #for node in route:
        #    print(f"  Node {node} has demand {d_k[node]}")


    return Q, K, N_q, f_q, d_k

