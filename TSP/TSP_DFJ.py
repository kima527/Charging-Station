import itertools

import gurobipy as gp

from TSP.create_tour import create_tour
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


class TSP_DFJ:

    @staticmethod
    def my_callback(model, where):
        if where == gp.GRB.Callback.MIPSOL:
            x_cb = dict()
            for (i,j) in model._x.keys():
                x_cb[i,j] = model.cbGetSolution(model._x[i,j]) >= 1 -1e-4
            cb_tour = create_tour(x_cb)
            if len(cb_tour) < len(model._cities):
                sum_arcs_in_subtour = gp.LinExpr()
                for (i,j) in model._x.keys():
                    if x_cb[i,j] is True:
                        sum_arcs_in_subtour.add(model._x[i,j])
                model.cbLazy(sum_arcs_in_subtour <= len(cb_tour) - 1)


    def run(self, travel_times: dict[Arc:float],ACTIVATE_CALLBACK=False):
        # create variables
        cities = list(set(itertools.chain(*travel_times.keys())))  # [(1,2),(3,4)]-> [1,2,3,4]
        x = {}
        for i, j in travel_times.keys():
            x[i, j] = model.addVar(lb=0, ub=1, vtype=gp.GRB.BINARY, name=f"x_{i}_{j}")
        model._x = x
        model._cities = cities

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
                if (i, j) in x:
                    city_must_be_left += x[i, j]
            model.addConstr(city_must_be_left == 1, f"{i}_must_be_left")

        for j in cities:
            city_must_be_visited = gp.LinExpr()
            for i in cities:
                if (i, j) in x:
                    city_must_be_visited += x[i, j]
            model.addConstr(city_must_be_visited == 1, f"{j}_must_be_visited")

        # DFJ Constraints
        # Find the power set
        if not ACTIVATE_CALLBACK:
            print("Computing the power sets..",end=" ")
            power_set_cities = list(
                itertools.chain.from_iterable(itertools.combinations(cities, r) for r in range(2, len(cities))))

            print("How many sets?:", len(power_set_cities))

            for sub_set in power_set_cities:
                dfj_constr = gp.LinExpr()
                for i in sub_set:
                    for j in sub_set:
                        if j != i:
                            dfj_constr.add(x[i, j])
                model.addConstr(dfj_constr <= len(sub_set) - 1, name=f"remove_subtour_{sub_set}")
            model.update()
            model.optimize()
        else:
            model.setParam("LazyConstraints",1)
            model.optimize(self.my_callback)

        arcs_used = dict()

        if model.Status == gp.GRB.OPTIMAL:
            for i, j in travel_times.keys():
                arcs_used[i, j] = x[i, j].X >= model.params.IntFeasTol

        elif model.Status == gp.GRB.INFEASIBLE:
            model.computeIIS()
            model.write("iis.ilp")
        return arcs_used

# arcs_used = TSP_DFJ().run(travel_times)
# tour = create_tour(arcs_used)
# print("tour: ", tour)
#
# distance_matrix_berlin_5 = import_tsp_instance("berlin5.tsp")
# arcs_used_berlin5 = TSP_DFJ().run(distance_matrix_berlin_5)
# berlin5_tour = create_tour(arcs_used_berlin5)
# print(f"berlin 5_tour: {berlin5_tour}")
#

berlin52 = import_tsp_instance("berlin52.tsp")
arcs_used_berlin52 = TSP_DFJ().run(berlin52, ACTIVATE_CALLBACK=True)
berlin52_tour = create_tour(arcs_used_berlin52)
print(f"berlin52: {berlin52_tour}")
#
# berlin52 = import_tsp_instance("berlin52.tsp")
# arcs_used_berlin52 = TSP_DFJ().run(berlin52, ACTIVATE_CALLBACK=True)
# berlin52_tour = create_tour(arcs_used_berlin52)
# print(f"berlin52: {berlin52_tour}")
#
# distance_matrix_tsp_225 = import_tsp_instance("tsp225.tsp")
# arcs_used_tsp225 = TSP_DFJ().run(distance_matrix_tsp_225, ACTIVATE_CALLBACK=True)
# tsp225_tour = create_tour(arcs_used_tsp225)
# print(f"tsp225: {tsp225_tour}")

