import random
import requests
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import webbrowser

# so don dat hang
num_orders = 10
print('Order list:(' + str(num_orders) + ' orders)')

# so luong phuong tien
num_vehicles = 2
print('Vehicles:(' + str(num_vehicles) + ')')

# suc chua
vehicle_capacities = 20
print('Capacitie:(' + str(vehicle_capacities) + ' slot)')

# khoang cach di chuyen toi da (m)
max_travel_distance = 200000
print('Max travel distance:(' + str(max_travel_distance) + ' m)')

# toa do ben xe
# depot = [21.04232, 105.81245]
depot = [43.7647,142.4046]

# duong gioi han: tren - phai - duoi -trai
# limitBor = [21.0416, 105.8562, 20.9907, 105.7465]
limitBor = [43.7942, 142.4690, 43.7362, 142.3267]


def creatematrixPoint(e,i,t):
    pointList = str(i[1]) + ',' + str(i[0])
    for x in range(e):
        latStart = random.uniform(t[0], t[2])
        lngStart = random.uniform(t[1], t[3])
        latEnd = random.uniform(t[0], t[2])
        lngEnd = random.uniform(t[1], t[3])
        pointList = pointList + ';' + str(lngStart) + ',' + str(latStart) + ';' + str(lngEnd) + ',' + str(latEnd)
        # print(' - ',(x + 1),': Start', str(lngStart) + ',' + str(latStart), ' End: ', str(lngEnd) + ',' + str(latEnd))
    return pointList
def get_distanceMatrix(e,start_time):
    data = e
    # urlApi = "http://router.project-osrm.org/table/v1/driving/" + data + '?annotations=distance,duration'
    urlApi = "http://10.92.200.89:5000/table/v1/driving/" + data + '?annotations=distance,duration'
    # chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    # webbrowser.get(chrome_path).open(urlApi)
    # print(urlApi)
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    result = requests.get(urlApi, headers={}).json()
    # result = requests.get(urlApi)
    # print(result)
    # print('\n')
    print('--------------------')
    print('Time get data API:',"%s seconds" % round((time.time() - start_time),1))
    print('\n')
    print('OR-tools is running...')
    return result
def pickup_delivery(e):
    pickups_deliveries = []
    for x in range(0,e):
        arr_pD = [2*x + 1,2*x +2]
        pickups_deliveries.append(arr_pD)
    # print('\n')
    # print('Pickups deliveries: ',pickups_deliveries)
    return pickups_deliveries
def print_solution(data, manager, routing, assignment):
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        arrTrip = [0]
        time_route = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
            point = int(format(manager.IndexToNode(index)))
            arrTrip.append(point)
            lenArrTrip = len(arrTrip)
            if (lenArrTrip > 1):
                time_route += data['distance_matrix'][arrTrip[lenArrTrip - 2]][arrTrip[lenArrTrip - 1]]
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        # plan_output += 'Load of the route: {}\n'.format(route_load)
        plan_output += ('Time of the route: ' + str(time_route) + ' min')
        print('\n')
        print(arrTrip)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('\n')
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    # return result
def orDistances(e,s,t,u,r,w,z):
    start_or_time = time.time()
    demand = [0]
    capacities = []
    for x in range(1, r + 1):
        demand.append(1)
        demand.append(-1)
    for x in range(1, t + 1):
        capacities.append(z)
    # print('\n')
    # print('Demand: ', demand)
    # print('\n')
    # print('Capacities: ', capacities)

    data = {}
    data['time_matrix'] = w
    data['distance_matrix'] = e
    data['pickups_deliveries'] = s
    data['num_vehicles'] = t
    data['depot'] = 0
    data['demands'] = demand
    data['vehicle_capacities'] = capacities
 
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        u,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery (pickup_index, delivery_index)
        routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
        routing.solver().Add(distance_dimension.CumulVar(pickup_index) <= distance_dimension.CumulVar(delivery_index))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

    assignment = routing.SolveWithParameters(search_parameters)

    if assignment:
        print('Time running OR-tools:',"%s seconds" % round((time.time() - start_or_time),1))
        print('\n')
        print_solution(data, manager, routing, assignment)
        print('\n')


    # return result
def main():
    # thoi gian bat dau chay
    start_time = time.time()

    # tao orders
    order = creatematrixPoint(num_orders,depot,limitBor)

    # lay matran
    matrixApi = get_distanceMatrix(order,start_time)

    # lay matran khoang cach
    matrixDistance = matrixApi['distances']

    # lay matran thoi gian
    matrixTime = matrixApi['durations']

    # Tao pickup_delivery
    pickupDelivery = pickup_delivery(num_orders)

    # chay Or-tool
    orDistances(matrixDistance,pickupDelivery,num_vehicles,max_travel_distance,num_orders,matrixTime,vehicle_capacities)

main()

# # Create the routing index manager.
    # manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
    #                                        data['num_vehicles'], data['depot'])

    # # Create Routing Model.
    # routing = pywrapcp.RoutingModel(manager)


    # # Create and register a transit callback.
    # def time_callback(from_index, to_index):
    #     """Returns the travel time between the two nodes."""
    #     # Convert from routing variable Index to time matrix NodeIndex.
    #     from_node = manager.IndexToNode(from_index)
    #     to_node = manager.IndexToNode(to_index)
    #     return data['time_matrix'][from_node][to_node]

    # transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # # Define cost of each arc.
    # routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # # Add Time Windows constraint.
    # timeW = 'Time'
    # routing.AddDimension(
    #     transit_callback_index,
    #     30,  # allow waiting time
    #     300000,  # maximum time per vehicle
    #     False,  # Don't force start cumul to zero.
    #     timeW)
    # time_dimension = routing.GetDimensionOrDie(timeW)
    # # Add time window constraints for each location except depot.
    # for location_idx, time_window in enumerate(data['time_windows']):
    #     if location_idx == 0:
    #         continue
    #     index = manager.NodeToIndex(location_idx)
    #     time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # # Add time window constraints for each vehicle start node.
    # for vehicle_id in range(data['num_vehicles']):
    #     index = routing.Start(vehicle_id)
    #     time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
    #                                             data['time_windows'][0][1])
    # # Instantiate route start and end times to produce feasible times.
    # for i in range(data['num_vehicles']):
    #     routing.AddVariableMinimizedByFinalizer(
    #         time_dimension.CumulVar(routing.Start(i)))
    #     routing.AddVariableMinimizedByFinalizer(
    #         time_dimension.CumulVar(routing.End(i)))

    # n = []
    # tupleArr = w[0]
    # for x in tupleArr:
    #     tLm = int(x + 30)
    #     bLm = int(x - 30)
    #     if (bLm < 0):
    #         bLm = 0
    #     tupleS = (bLm,tLm)
    #     n.append(tupleS)