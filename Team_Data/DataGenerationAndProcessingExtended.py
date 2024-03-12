import osmnx as ox
import networkx as nx
from DataGenerationAndProcessing import get_flows
from shapely.geometry import Point, LineString

def get_routesandpaths(): # Loads locations of denseley populated areas and connects them via shortest path and two additional perfectly divergent paths

    locations = {
        "Perlach": "Perlach, Munich, Germany",
        "Neuhausen": "Neuhausen, Munich, Germany",
        "Freimann": "Münchener Freiheit, Munich, Germany",
        "Thalkirchen": "Thalkirchen, Munich, Germany",
        "Bogenhausen": "Bogenhausen, Munich, Germany",
        "Feldmoching": "Milbertshofen, Munich, Germany",
        "Hadern": "Westendstraße, Munich, Germany",
        "Moosach": "Claudiusplatz, Munich, Germany",
        "Oberfoehring": "Bürgerpark Oberföhring, Munich, Germany",
        "Berg-am-Laim": "Sankt Pius, Munich, Germany",
        "Giesing": "Wettersteinplatz, Munich, Germany",
        "Sendling": "Pilsenseestraße, Munich, Germany",
        "Stachus": "Karlsplatz 11, Munich, Germany",
        "Sendlinger-Tor": "Sendlinger-Tor-Platz 14, Munich, Germany",
        "Isartor": "Isartor/Zweibrückenstr., Munich, Germany",
        "Odeonsplatz": "Odeonsplatz, Munich, Germany"
    }

    # Function finding the nearest node with more than min_edges in-/outgoing edges
    def find_nearest_crossing(G, point, min_edges, increment=0.0001):
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

    # Find the nearest crossing nodes to the OD-locations with at least six in-/outgoing edges
    nearest_crossings = {}
    for name, point in coords.items():
        nearest_crossings[name] = find_nearest_crossing(G, point, min_edges=6)


    # Connect OD-pairs via shortest path and two additional perfectly divergent paths and store route coordinates
    routesandpath_nodes = [
        list(nx.edge_disjoint_paths(G, nearest_crossings["Perlach"], nearest_crossings["Neuhausen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Thalkirchen"], nearest_crossings["Freimann"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Bogenhausen"], nearest_crossings["Thalkirchen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Bogenhausen"], nearest_crossings["Neuhausen"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Perlach"], nearest_crossings["Freimann"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Hadern"], nearest_crossings["Stachus"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Moosach"], nearest_crossings["Stachus"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Feldmoching"], nearest_crossings["Odeonsplatz"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Oberfoehring"], nearest_crossings["Odeonsplatz"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Berg-am-Laim"], nearest_crossings["Isartor"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Giesing"], nearest_crossings["Sendlinger-Tor"], cutoff=3)),
        list(nx.edge_disjoint_paths(G, nearest_crossings["Sendling"], nearest_crossings["Sendlinger-Tor"], cutoff=3))
    ]
    for i in routesandpath_nodes:
        print(len(i))
    # Stores the shortest distance between OD-pairs
    routes_shortestpath_length = {
        "Perlach to Neuhausen": nx.shortest_path_length(G, nearest_crossings["Perlach"], nearest_crossings["Neuhausen"],weight='length'),
        "Thalkirchen to Freimann": nx.shortest_path_length(G, nearest_crossings["Thalkirchen"], nearest_crossings["Freimann"],weight='length'),
        "Bogenhausen to Thalkirchen": nx.shortest_path_length(G, nearest_crossings["Bogenhausen"], nearest_crossings["Thalkirchen"],weight='length'),
        "Bogenhausen to Neuhausen": nx.shortest_path_length(G, nearest_crossings["Bogenhausen"], nearest_crossings["Neuhausen"],weight='length'),
        "Perlach to Freimann": nx.shortest_path_length(G, nearest_crossings["Perlach"], nearest_crossings["Freimann"],weight='length'),
        "Hadern to Stachus": nx.shortest_path_length(G, nearest_crossings["Hadern"], nearest_crossings["Stachus"],weight='length'),
        "Moosach to Stachus": nx.shortest_path_length(G, nearest_crossings["Moosach"], nearest_crossings["Stachus"],weight='length'),
        "Feldmoching to Odeonsplatz": nx.shortest_path_length(G, nearest_crossings["Feldmoching"], nearest_crossings["Odeonsplatz"],weight='length'),
        "Oberfoehring to Odeonsplatz": nx.shortest_path_length(G, nearest_crossings["Oberfoehring"], nearest_crossings["Odeonsplatz"],weight='length'),
        "Berg-am-Laim to Isartor": nx.shortest_path_length(G, nearest_crossings["Berg-am-Laim"], nearest_crossings["Isartor"],weight='length'),
        "Giesing to Sendlinger-Tor": nx.shortest_path_length(G, nearest_crossings["Giesing"], nearest_crossings["Sendlinger-Tor"],weight='length'),
        "Sendling to Sendlinger-Tor": nx.shortest_path_length(G, nearest_crossings["Sendling"], nearest_crossings["Sendlinger-Tor"], weight='length'),
    }



    return coords, routesandpath_nodes, routes_shortestpath_length, G


def get_parameters_extended(routesandpath_nodes, annual_trips,routes_shortestpath_length,G):

    # OD-pairs based on our routesandpath_nodes lists (as strings)
    Q = list(routes_shortestpath_length.keys())

    # Path options
    P = [1,2,3]

    # Nodes based on our routesandpath_nodes values within lists (as value)
    K = set()
    for route_paths in routesandpath_nodes:
        for path in route_paths:
            K.update(path)
    K = list(K)

    # Set of nodes capable of capturing the flow of OD-pair q, on path p. First path is the shortest path
    N_qp = {q: {p: routesandpath_nodes[Q.index(q)][p-1] for p in P} for q in Q}

    # Charges/ year of one fast charger (assuming demand only on the 230 working days) with 30 mins for full charge
    Charger_annual_capacity = 11040 #vehicles/yr
    EVsPerCapitaGer = 15.6/1000
    # Flows through OD-pairs on each 30 mins
    f_q = {od: flow_value for od, flow_value in zip(Q, [])}
    for od, value in annual_trips.items():
        f_q[od] = (value/Charger_annual_capacity) * EVsPerCapitaGer

    '''
    f_qp = {}
    for od, value in f_q.items():
        f_qp[od] = {int(i): value / 3 for i in range(1, 4)}
    '''
    # Flows through path options of OD-pairs on each 30 mins - adapt based on scenario
    f_qp = {}
    for od, value in f_q.items():
        # Explicitly assign the percentages to each path option
        f_qp[od] = {
            1: value * 0.7,
            2: value * 0.2,
            3: value * 0.1
        }

    # Summed demand on node keK based on all flows
    d_k = {node: 0 for node in G.nodes}
    for route_list in routesandpath_nodes:
        for route in route_list:
            for node in route:
                for i in range(1, 4):
                    od_key = int(i)
                    flow = f_qp.get(od, {}).get(od_key, 0)
                    d_k[node] += flow/2


    return Q, P, K, N_qp, f_q, f_qp, d_k

