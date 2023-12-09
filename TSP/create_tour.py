City = str
Arc = tuple[City, City]


def create_tour(arcs_used: dict[Arc:bool]) -> list[City]:
    if not arcs_used:
        print("no arcs used!")

    successors = {pred: succ for (pred, succ), is_arc_used in arcs_used.items() if is_arc_used}
    cities = list(successors.keys())
    tour = [cities[0]]
    while len(tour) < len(cities):
        last_city = tour[-1]
        successor = successors[last_city]
        if successor == tour[0]:
            break
        tour.append(successor)

    return tour