# We run the code in here

import DataGenerationAndProcessing as data
import DataGenerationAndProcessingExtended as extendedData
import Model
import Visualize

if __name__ == '__main__':

    FC = 21  # Fixed charging station installation cost
    VC = 20   # Variable charging station installation cost
    B = 3000  # Budget
    CAP = 4 # Module Cap
    M = 999999  # Very large number

    # Please uncomment this block to run the Base model
    #
    # coords, routes_nodes, routes_length, G = data.get_routes()
    # annual_trips = data.get_flows(coords, routes_length)
    # Q, K, N_q, f_q, d_k = data.get_parameters(routes_nodes, G, annual_trips)
    # base_model = Model.Model(FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, False)
    # base_model.run()
    # base_model_visualize = Visualize.Visualize()
    # base_model_visualize.base_model_map(G, routes_nodes)


    # Please uncomment this block to run extended model

    coords, routes_nodes, routes_length, G = extendedData.get_routesandpaths()
    annual_trips = data.get_flows(coords, routes_length)
    Q, P, K, N_qp, f_q, f_qp, d_k = extendedData.get_parameters_extended(routes_nodes, annual_trips)
    model = Model.Model(FC, VC, B, CAP, M, Q, K, N_qp, f_qp, d_k, coords, routes_nodes, routes_length, G, True)

    model_path = Visualize.Visualize()
    odel_path.paths(G, routes_nodes) # initial visualization of paths on the map

    model.run()

    after_model = Visualize.Visualize(model.result_locations)
    after_model.where_to_install(G) # result location shown on the map






#TODO
# different scenarios 1, 2, 3 (shortest route, 50/50, 30/30/30)
# lower limit of flow to be served in buget iterations - service level fixed
# play with these two parameters and always fix one
# https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.disjoint_paths.edge_disjoint_paths.html