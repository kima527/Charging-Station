# TODO: Build on Kimas visualize_potential_facility_location() and devise specific parking lots
# Fetch parking data for Munich
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
import geopy.distance
from DataGenerationAndProcessing import get_routes

# Function to check if a parking lot is within 1km of any route

class PotentialLocation:

    def is_parking_near_any_route(self, parking_point, routes_coords):
        for route_line in routes_coords.values():
            # Use geopy to calculate distance
            nearest_point = route_line.interpolate(route_line.project(parking_point))
            distance = geopy.distance.distance((parking_point.y, parking_point.x),
                                               (nearest_point.y, nearest_point.x)).km
            if distance < 0.5:  # 1 km
                return True
        return False


    def filtered_parking_coordinates(self, G, routes_nodes):
        parking = ox.features_from_place("Munich, Germany", tags={'amenity': 'parking'})
        print(f"Total parking lots: {len(parking)}")

        routes_coords = {}
        for route_name, route in routes_nodes.items():
            route_coords = [Point(G.nodes[node]['x'], G.nodes[node]['y']) for node in route]
            routes_coords[route_name] = LineString(route_coords)

        filtered_parking = parking[
            parking.apply(lambda x: self.is_parking_near_any_route(x.geometry.centroid, routes_coords), axis=1)]
        print(f"Filtered parking lots: {len(filtered_parking)}")  # Print filtered parking lots

        # Get the coordinates of filtered parking lots
        filtered_parking_coordinates = [(p.geometry.centroid.y, p.geometry.centroid.x) for p in
                                        filtered_parking.itertuples()]

        return filtered_parking_coordinates


