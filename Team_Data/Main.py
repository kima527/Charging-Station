# We run the code in here
import warnings
import DataGenerationAndProcessing as data
import DataGenerationAndProcessingExtended as extendedData
import Model
import Visualize
import matplotlib.pyplot as plt

if __name__ == '__main__':
    FC = 21  # Fixed charging station installation cost
    VC = 20  # Variable charging station installation cost
    B = 25000  # Budget
    CAP = 6  # Module Cap
    M = 999999  # Very large number

    # Please uncomment this block to run the Base model
    """
    coords, routes_nodes, routes_length, G = data.get_routes()
    annual_trips = data.get_flows(coords, routes_length)
    Q, K, N_q, f_q, d_k = data.get_parameters(routes_nodes, G, annual_trips)
    base_model = Model.Model(FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, False)
    base_model.run()
    #base_model_visualize = Visualize.Visualize()
    #base_model_visualize.base_model_map(G, routes_nodes)
    """

    # Please uncomment this block to run a Budget Iteration of the Base model
    """
    Iterations = range(6)
    Initial_budget = 10000
    Budget_steps = 1000

    B = Initial_budget
    
    budget_values = []
    objective_values = []
    
    coords, routes_nodes, routes_length, G = data.get_routes()
    annual_trips = data.get_flows(coords, routes_length)
    Q, K, N_q, f_q, d_k = data.get_parameters(routes_nodes, G, annual_trips)
    
    for i in Iterations:
        print("ITERATION", i, "BUDGET", B)
    
        base_model = Model.Model(FC, VC, B, CAP, M, Q, K, N_q, f_q, d_k, coords, routes_nodes, routes_length, G, False)
        objective = base_model.run()
        #base_model_visualize = Visualize.Visualize()
        #base_model_visualize.base_model_map(G, routes_nodes)
    
        
    
        budget_values.append(B / 1000)
        objective_values.append(objective)
    
        B += Budget_steps

    # Plotting the graph
    plt.plot(budget_values, objective_values, marker='o')
    plt.xlabel('Budget in $ Mio')
    plt.ylabel('Flow covered/ 30 min')
    plt.title('Objective Value related to Budget')
    plt.grid(True)
    plt.show()
    """

    # Please uncomment this block to run Extended model

    coords, routes_nodes, routes_length, G = extendedData.get_routesandpaths()
    annual_trips = data.get_flows(coords, routes_length)
    Q, P, K, N_qp, f_q, f_qp, d_k = extendedData.get_parameters_extended(routes_nodes, annual_trips, routes_length, G)
    model = Model.Model(FC, VC, B, CAP, M, Q, K, N_qp, f_qp, d_k, coords, routes_nodes, routes_length, G, True)

    #model_path = Visualize.Visualize()
    #model_path.paths(G, routes_nodes)  # initial visualization of paths on the map

    model.run()

    #after_model = Visualize.Visualize(model.result_locations)
    #after_model.where_to_install(G)  # result location shown on the map


    # Please uncomment this block to run a Budget Iteration of the Extended model
    """
    Iterations = range(25)
    Initial_budget = 31000
    Budget_steps = 1000

    B = Initial_budget

    budget_values = []
    objective_values = []
    gaps = []

    coords, routes_nodes, routes_length, G = extendedData.get_routesandpaths()
    annual_trips = data.get_flows(coords, routes_length)
    Q, P, K, N_qp, f_q, f_qp, d_k = extendedData.get_parameters_extended(routes_nodes, annual_trips, routes_length, G)


    for i in Iterations:
        print("ITERATION", i, "BUDGET", B)

        model = Model.Model(FC, VC, B, CAP, M, Q, K, N_qp, f_qp, d_k, coords, routes_nodes, routes_length, G, True)
        objective, gap = model.run()

        budget_values.append(B / 1000)
        objective_values.append(objective)
        gaps.append(gap)

        B += Budget_steps


    #printing the outputs
    print(budget_values)
    print(objective_values)
    print(gaps)

    # Plotting the graph
    plt.plot(budget_values, objective_values, marker='o')
    plt.xlabel('Budget in $ Mio')
    plt.ylabel('Flow covered/ 30 min')
    plt.title('Objective Value related to Budget')
    plt.grid(True)
    plt.show()
    """