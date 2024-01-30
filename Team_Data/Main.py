# We run the code in here

from OptModel import model_run
from DataVisualization import visualize_potential_facility_location


if __name__ == '__main__':

    FC = 20  # Fixed charging station installation cost
    VC = 5   # Variable charging station installation cost
    B = 10000  # Budget
    CAP = 8  # Module Cap
    M = 999999  # Very large number

    model_run(FC, VC, B, CAP, M)
    visualize_potential_facility_location()

