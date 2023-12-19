from itertools import tee

Location = int
Arc = tuple[Location,Location]
DistanceMatrix = dict[Arc: float]


def calculate_euclidean_distance(coordinate_first, coordinate_second):
    return (coordinate_first["x_coord"] - coordinate_second["x_coord"]) ** 2 + (
                coordinate_first["y_coord"] - coordinate_second["y_coord"]) ** 2


def import_tsp_instance(instance_name: str) -> DistanceMatrix:
    with open(f"instances/{instance_name}", "r") as infile:
        instance = infile.readlines()
    dict_coordinates = {}
    for line in instance:
        split_line = line.split(" ")
        if split_line[0].isdigit():
            name_location = split_line[0]
            x_coord = float(split_line[1])
            y_coord = float(split_line[2].strip("\n"))
            dict_coordinates[name_location] = {"x_coord": x_coord, "y_coord": y_coord}

    distance_matrix = {}

    for first_location in dict_coordinates:
        coordinate_first = dict_coordinates[first_location]
        for second_location in dict_coordinates:
            if first_location != second_location:
                coordinate_second = dict_coordinates[second_location]
                distance_matrix[first_location,second_location] = calculate_euclidean_distance(coordinate_first,
                                                                                                coordinate_second)

    return distance_matrix

def returnNextPub(variables, tour):
    for key,val in variables.items():
        if key[0] == tour[-1] and abs(val -1) < 1e-6:
            return key[1]

def get_tour(locations, variables):
    tour = [list(variables.keys())[0][0]]
    while len(tour) < len(locations):
        nextPub = returnNextPub(variables, tour)
        if nextPub == tour[0]:
            return tour
        tour.append(nextPub)

    return tour

def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)