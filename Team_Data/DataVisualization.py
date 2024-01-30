#TODO data visualization
# Implement Marcos OUtput processing
# Potential locations are not shown correctly
# Implement the visualization of solution ( which node, how many if possible)

import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopy.distance
from DataGenerationAndProcessing import get_routes
from PotentialLocation import get_filtered_parking, filtered_parking_coordinates


def visualize_potential_facility_location():
    coords, routes_nodes, routes_length, G = get_routes()

    # Extract the route lists from the routes dictionary for plotting
    route_lists = list(routes_nodes.values())

    # Ensure that route_colors has the same number of elements as route_lists
    route_colors = ['orange', 'b', 'purple', 'green', 'skyblue', 'pink'] * (len(route_lists) // 5 + 1)
    route_colors = route_colors[:len(route_lists)]  # Trim the list to the length of route_lists

    # Plot filtered parking lots
    parking_coords = filtered_parking_coordinates()

    # Plot the graph and routes
    fig, ax = ox.plot_graph_routes(G, route_lists, route_colors=route_colors, route_linewidth=6, node_size=10,
                                   figsize=(12, 12), show=False, close=False)
    for y, x in parking_coords:
        ax.scatter(x, y, c='red', s=30, alpha=0.7, zorder=5)  # Increase the size for visibility

    plt.show()

