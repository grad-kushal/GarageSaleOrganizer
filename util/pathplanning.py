import os

import googlemaps

import numpy as np

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

gmaps = googlemaps.Client(key=os.environ['GOOGLE_API_KEY_GEOCODING'])


def get_distance(e1_coordinates, e2_coordinates):
    print("Query parameters: ", e1_coordinates, e2_coordinates)
    origin = (e1_coordinates[1], e1_coordinates[0])
    destination = (e2_coordinates[1], e2_coordinates[0])
    return (gmaps.distance_matrix(origin, destination, units='metric')['rows'][0]['elements'][0]['distance']['value'],
            gmaps.distance_matrix(origin, destination, units='minutes')['rows'][0]['elements'][0]['duration']['value'])


def get_distance_matrix(coordinates):
    """
    Get the distance matrix
    :param coordinates: the coordinates
    :return: the distance matrix
    """
    print("Query parameters: ", coordinates)
    origins = []
    destinations = []
    for coordinate in coordinates:
        origins.append((coordinate[1], coordinate[0]))
        destinations.append((coordinate[1], coordinate[0]))
    # print("Origins: ", origins)
    # print("Destinations: ", destinations)
    resp = gmaps.distance_matrix(origins, destinations, units='metric', mode='driving')
    # print("Response: ", resp)
    return resp


def normalize(matrix):
    """
    Normalize the matrix
    :param matrix: the matrix
    :return: the normalized matrix
    """
    normalized_matrix = np.array(matrix) / np.max(matrix)

    return normalized_matrix


def create_cost_matrix(distances, durations, distance_weight, duration_weight):
    """
    Create the cost matrix
    :param distances: the distances
    :param durations: the durations
    :param distance_weight: weightage for distance
    :param duration_weight: weightage for duration
    :return: the cost matrix
    """
    # print("Query parameters: ", distances, durations, distance_weight, duration_weight)

    normalized_distances = normalize(distances)
    normalized_durations = normalize(durations)

    cost_matrix = (distance_weight * normalized_distances) + (duration_weight * normalized_durations)

    cost_matrix /= np.max(cost_matrix)

    return cost_matrix


def solve_tsp(matrix, dimension):
    """
    Solve the TSP problem
    :param dimension: the dimension
    :param matrix: the distance matrix
    :return: the solution
    """
    print("Solver Dimension: ", dimension)
    routes = []
    size = len(matrix)
    # for i in range(size):

    manager = pywrapcp.RoutingIndexManager(size, 1, [0], [0])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    dimension_name = dimension
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        9000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(10000)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING)
    search_parameters.time_limit.seconds = 10
    search_parameters.log_search = False

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        route = []
        route_distances = []
        max_route_distance = 0
        total_distance = 0  # Track the total distance
        for vehicle_id in range(1):
            print("Objective: ", solution.ObjectiveValue())
            index = routing.Start(vehicle_id)
            route_distance = 0
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(node)
                next_index = solution.Value(routing.NextVar(index))
                print("Index: ", index)
                print("Next index: ", next_index)
                arc_cost = routing.GetArcCostForVehicle(index, next_index, vehicle_id)
                route_distance += arc_cost
                print(f"Arc Cost: {arc_cost}{'m' if dimension == 'Distance' else 's'}")
                print(matrix[node][manager.IndexToNode(next_index)])
                print(f"Cumulative Cost: {route_distance}{'m' if dimension == 'Distance' else 's'}")
                index = next_index
            route.append(manager.IndexToNode(index))
            route_distances.append(route_distance)
            print(f"Route cost: {route_distance}{'m' if dimension == 'Distance' else 's'}")
            routes.append(route)
    else:
        # print('No solution found.')
        routes.append([])

    return routes
