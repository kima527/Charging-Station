#TODO data visualization
# Implement Marcos OUtput processing
# Implement Kimas post processing

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopy.distance
#-----------------------------------------------------Pre------------------------------------------------
#TODO not very generic, make it dependent on data generation...
def visualize_Nq():

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
    routes = [
        nx.shortest_path(G, nearest_nodes["Marienplatz"], nearest_nodes["Olympiapark"], weight='length'),
        nx.shortest_path(G, nearest_nodes["HBF"], nearest_nodes["BMW"], weight='length'),
        nx.shortest_path(G, nearest_nodes["Münchener Freiheit"], nearest_nodes["TUM City Center"], weight='length'),
        nx.shortest_path(G, nearest_nodes["Münchener Freiheit"], nearest_nodes["Olympiapark"], weight='length'),
        nx.shortest_path(G, nearest_nodes["TUM City Center"], nearest_nodes["Marienplatz"], weight='length')
    ]

    # Initialize a list to store the coordinates of all nodes in each route
    routes_coords = []

    # Define a function to get the coordinates of a node
    def get_coords_from_node(graph, node_id):
        node = graph.nodes[node_id]
        return node['y'], node['x']

    # Iterate over each route and extract the coordinates of all nodes
    for route in routes:
        route_coords = [get_coords_from_node(G, node) for node in route]
        routes_coords.append(route_coords)

    # Display the routes with their node coordinates
    # for i, route_coords in enumerate(routes_coords, start=1):
    #    print(f"Route {i} Coordinates: {route_coords}")

    # Plot the graph and routes
    fig, ax = ox.plot_graph_routes(G, routes, route_colors=['r', 'b', 'y', 'green', 'skyblue'], route_linewidth=6,
                                   node_size=8)
    plt.show()
#-----------------------------------------------------Output---------------------------------------------

#-----------------------------------------------------Post-----------------------------------------------
# TODO not very generic, make it dependent on data generation... & highlight nodes where chargers are installed
# to show where we actually would install stations
def visualize_potential_facility_location():
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
    G = ox.graph_from_address("Munich, Germany", network_type='drive', dist=4000)

    # Find the nearest nodes to the locations
    nearest_nodes = {name: ox.distance.nearest_nodes(G, point[1], point[0]) for name, point in coords.items()}

    # Calculate the shortest paths
    routes = {
        "Marienplatz to Olympiapark": nx.shortest_path(G, nearest_nodes["Marienplatz"], nearest_nodes["Olympiapark"],
                                                       weight='length'),
        "Olympiapark to HBF": nx.shortest_path(G, nearest_nodes["Olympiapark"], nearest_nodes["HBF"], weight='length'),
        "HBF to BMW": nx.shortest_path(G, nearest_nodes["HBF"], nearest_nodes["BMW"], weight='length'),
        "BMW to TUM City Center": nx.shortest_path(G, nearest_nodes["BMW"], nearest_nodes["TUM City Center"],
                                                   weight='length'),
        "TUM City Center to Münchener Freiheit": nx.shortest_path(G, nearest_nodes["TUM City Center"],
                                                                  nearest_nodes["Münchener Freiheit"], weight='length'),
        "Münchener Freiheit to Olympiapark": nx.shortest_path(G, nearest_nodes["Münchener Freiheit"],
                                                              nearest_nodes["Olympiapark"], weight='length'),
    }

    # Define a function to get the coordinates of a node
    def get_coords_from_node(graph, node_id):
        node = graph.nodes[node_id]
        return node['y'], node['x']

    # Iterate over each route and extract the coordinates of all nodes
    routes_coords = {}
    for route_name, route in routes.items():
        route_coords = [Point(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
        routes_coords[route_name] = LineString(route_coords)

    # Fetch parking data for Munich
    parking = ox.features_from_place("Munich, Germany", tags={'amenity': 'parking'})
    print(f"Total parking lots: {len(parking)}")

    # Function to check if a parking lot is within 1km of any route
    def is_parking_near_any_route(parking_point, routes_coords):
        for route_line in routes_coords.values():
            # Use geopy to calculate distance
            nearest_point = route_line.interpolate(route_line.project(parking_point))
            distance = geopy.distance.distance((parking_point.y, parking_point.x),
                                               (nearest_point.y, nearest_point.x)).km
            if distance < 0.5:  # 1 km
                return True
        return False

    filtered_parking = parking[
        parking.apply(lambda x: is_parking_near_any_route(x.geometry.centroid, routes_coords), axis=1)]
    print(f"Filtered parking lots: {len(filtered_parking)}")  # Print filtered parking lots

    # Get the coordinates of filtered parking lots
    filtered_parking_coordinates = [(p.geometry.centroid.y, p.geometry.centroid.x) for p in
                                    filtered_parking.itertuples()]

    # Extract the route lists from the routes dictionary for plotting
    route_lists = list(routes.values())

    # Ensure that route_colors has the same number of elements as route_lists
    route_colors = ['orange', 'b', 'purple', 'green', 'skyblue', 'pink'] * (len(route_lists) // 5 + 1)
    route_colors = route_colors[:len(route_lists)]  # Trim the list to the length of route_lists

    # Plot the graph and routes
    fig, ax = ox.plot_graph_routes(G, route_lists, route_colors=route_colors, route_linewidth=6, node_size=50,
                                   figsize=(12, 12), show=False, close=False)

    # Plot filtered parking lots
    for y, x in filtered_parking_coordinates:
        ax.scatter(x, y, c='red', s=30, alpha=0.7, zorder=5)  # Increase the size for visibility

    plt.show()

visualize_Nq()
visualize_potential_facility_location()