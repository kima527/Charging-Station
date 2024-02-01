# We run the code in here

from OptModel import model_run
from DataVisualization import visualize_potential_facility_location


if __name__ == '__main__':

    FC = 20  # Fixed charging station installation cost
    VC = 20   # Variable charging station installation cost
    B = 10000  # Budget
    CAP = 8  # Module Cap
    M = 999999  # Very large number

    model_run(FC, VC, B, CAP, M)
    visualize_potential_facility_location()

#TODO
# different scenarios 1, 2, 3 (shortest route, 50/50, 30/30/30)
# lower limit of flow to be served in buget iterations - service level fixed
# play with these two parameters and always fix one
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.disjoint_paths.edge_disjoint_paths.html