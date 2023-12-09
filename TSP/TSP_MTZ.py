import itertools

import gurobipy as gp

from create_tour import create_tour
from import_TSP import import_tsp_instance

City = str
Arc = tuple[City, City]



travel_times = {
    ("A", "A"): 0, ("A", "B"): 23, ("A", "C"): 13, ("A", "D"): 15, ("A", "E"): 20,
    ("B", "A"): 23, ("B", "B"): 0, ("B", "C"): 6, ("B", "D"): 14, ("B", "E"): 18,
    ("C", "A"): 13, ("C", "B"): 6, ("C", "C"): 0, ("C", "D"): 9, ("C", "E"): 22,
    ("D", "A"): 15, ("D", "B"): 14, ("D", "C"): 9, ("D", "D"): 0, ("D", "E"): 11,
    ("E", "A"): 20, ("E", "B"): 18, ("E", "C"): 22, ("E", "D"): 11, ("E", "E"): 0,
}

model = gp.Model("my_model")


class TSP:

    def run(self, travel_times: dict[Arc:float]):
        # create variables
        cities = list(set(itertools.chain(*travel_times.keys())))  # [(1,2),(3,4)]-> [1,2,3,4]
        x = {}
        b = {}
        for i in cities:
            b[i] = model.addVar(lb=0, vtype=gp.GRB.CONTINUOUS, name=f"b_{i}")
        for i, j in travel_times.keys():
            x[i, j] = model.addVar(lb=0, ub=1, vtype=gp.GRB.BINARY, name=f"x_{i}_{j}")

        # create objective
        obj = gp.LinExpr()
        for (i, j), t in travel_times.items():
            obj.add(x[i, j] * t)
        model.setObjective(obj,sense=gp.GRB.MINIMIZE)
        model.update()

        # create constraints

        for i in cities:
            city_must_be_left = gp.LinExpr()
            for j in cities:
                if i is j:
                    continue
                if (i, j) in x:
                    city_must_be_left += x[i, j]
            model.addConstr(city_must_be_left == 1, f"{i}_must_be_left")

        for j in cities:
            city_must_be_visited = gp.LinExpr()
            for i in cities:
                if i is j:
                    continue
                if (i, j) in x:
                    city_must_be_visited += x[i, j]
            model.addConstr(city_must_be_visited == 1, f"{j}_must_be_visited")

        # first city
        model.addConstr(b[cities[0]] == 1, "first_city")

        for i in cities:
            for j in cities:
                if i is j or j == cities[0]:
                    continue
                mtz_flow = gp.LinExpr(b[i] + 1 - len(cities) * (1 - x[i, j]))
                model.addConstr(mtz_flow <= b[j], name='MTZ Flow')

        model.update()
        model.optimize()
        arcs_used = dict()

        if model.Status == gp.GRB.OPTIMAL:
            for i, j in travel_times.keys():
                arcs_used[i, j] = x[i, j].X >= model.params.IntFeasTol

        elif model.Status == gp.GRB.INFEASIBLE:
            model.computeIIS()
            model.write("iis.ilp")
        return arcs_used

# arcs_used = TSP().run(travel_times)
# tour = create_tour(arcs_used)
# print("tour: ", tour)

# distance_matrix_berlin_5 = import_tsp_instance("berlin5.tsp")
# arcs_used_berlin5 = TSP().run(distance_matrix_berlin_5)
# berlin5_tour = create_tour(arcs_used_berlin5)
# print(f"berlin 5_tour: {berlin5_tour}")

# distance_matrix_berlin_5 = import_tsp_instance("berlin52.tsp")
# arcs_used_berlin5 = TSP().run(distance_matrix_berlin_5)
# berlin5_tour = create_tour(arcs_used_berlin5)
# print(f"berlin 5_tour: {berlin5_tour}")

#
distance_matrix_tsp_225 = import_tsp_instance("tsp225.tsp")
arcs_used_tsp225 = TSP().run(distance_matrix_tsp_225)
tsp225_tour = create_tour(arcs_used_tsp225)
print(f"tsp225: {tsp225_tour}")

