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
import PotentialLocation

class Visualize:

    def __init__(self, result_location=None):
        self.result_location = result_location

    def paths(self, G, routes_nodes):
        flattened_routes = [node for route in routes_nodes for node in route]
        route_colors=['red', 'red', 'red', 'blue', 'blue','blue', 'green', 'green', 'green', 'yellow', 'yellow','yellow', 'orange', 'orange', 'orange']
        fig, path = ox.plot_graph_routes(G, flattened_routes, route_colors=route_colors , route_linewidth=6, node_size=8)
        plt.show()

    def where_to_install(self, G):
        fig, location = ox.plot_graph(G, figsize=(12, 12), show=False, close=False)
        for (x, y) in self.result_location:
            location.scatter(x, y, c='red', s=100, alpha=0.7, zorder=5)
        plt.show()

    def base_model_map(self, G, routes_nodes):

        # Extract the route lists from the routes dictionary for plotting
        route_lists = list(routes_nodes.values())

        # Ensure that route_colors has the same number of elements as route_lists
        route_colors = ['orange', 'b', 'purple', 'green', 'skyblue', 'pink'] * (len(route_lists) // 5 + 1)
        route_colors = route_colors[:len(route_lists)]  # Trim the list to the length of route_lists

        # Plot filtered parking lots
        potential_location = PotentialLocation.PotentialLocation()
        parking_coords = potential_location.filtered_parking_coordinates(G, routes_nodes)
        print(len(parking_coords))


        # Plot the graph and routes
        fig, ax = ox.plot_graph_routes(G, route_lists, route_colors=route_colors, route_linewidth=6, node_size=10, figsize=(12, 12), show=False, close=False)
        #fig, ax = ox.plot_graph(G, figsize=(12, 12), show=False, close=False)
        for y, x in parking_coords:
            ax.scatter(x, y, c='red', s=20, alpha=0.7, zorder=5)  # Increase the size for visibility
        plt.show()

    def location(self, G, routes_nodes):

        # Extract the route lists from the routes dictionary for plotting

        # Plot filtered parking lots
        potential_location = PotentialLocation.PotentialLocation()
        parking_coords = potential_location.filtered_parking_coordinates(G, routes_nodes)
        print(len(parking_coords))


        # Plot the graph and routes
        #fig, ax = ox.plot_graph_routes(G, route_lists, route_colors=route_colors, route_linewidth=6, node_size=10, figsize=(12, 12), show=False, close=False)
        fig, ax = ox.plot_graph(G, figsize=(12, 12), show=False, close=False)
        for y, x in parking_coords:
            ax.scatter(x, y, c='red', s=20, alpha=0.7, zorder=5)  # Increase the size for visibility
        plt.show()
