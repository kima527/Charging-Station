# We run the code in here

from XXOptModel import model_run
from DataVisualization import visualize_potential_facility_location
import DataGenerationAndProcessing as data
import DataGenerationAndProcessingExtended as extendedData
import Model


if __name__ == '__main__':

    FC = 20  # Fixed charging station installation cost
    VC = 20   # Variable charging station installation cost
    B = 10000  # Budget
    CAP = 8  # Module Cap
    M = 999999  # Very large number

    # Please uncomment this block to run the Base model

    # coords, routes_nodes, routes_length, G = data.get_routes()
    # annual_trips = data.get_flows(coords, routes_length)
    # Q, K, N_q, f_q, d_k = data.get_parameters(routes_nodes, G, annual_trips)
    # base_model = Model.Model(FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, False)
    # base_model.run()


    # Please uncomment this block to run extended model

    coords, routes_nodes, routes_length, G = extendedData.get_routesandpaths()
    annual_trips = data.get_flows(coords, routes_length)
    Q, P, K, N_qp, f_q, f_qp, d_k = extendedData.get_parameters_extended(routes_nodes, annual_trips)
    extend_model = Model.Model(FC, VC, B, CAP, M, Q, K, N_qp, f_qp, d_k, coords, routes_nodes, routes_length, G, True)
    extend_model.run()




#TODO
# different scenarios 1, 2, 3 (shortest route, 50/50, 30/30/30)
# lower limit of flow to be served in buget iterations - service level fixed
# play with these two parameters and always fix one
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.disjoint_paths.edge_disjoint_paths.html