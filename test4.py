import sys
import time
import os
from alive_progress import alive_bar,show_bars, show_spinners, showtime
from getData import getCsvData
from getData import getJsonData
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

os.system('cls' if os.name == 'nt' else 'clear')
# argparse
def compute():
    for i in range(100):
        time.sleep(.01)  # process items
        if i == 99:
            time.sleep(3)
        yield  # insert this and you're done!

with alive_bar(100) as bar:
    for i in compute():
        bar()

def is_int(val):
    try:
        num = int(val)
    except ValueError:
        return False
    return True

def is_float(val):
    try:
        num = float(val)
    except ValueError:
        return False
    return True

def getNumberOrder(r):
    if r == False:
        print('Type error!Enter a number!')
    number_order = input("Number order?(int) \n")
    check_input = is_int(number_order)
    return int(number_order) if check_input else getNumberOrder(False)

def getNumberVehicles(r):
    if r == False:
        print('Type error!Enter a number!')
    number_vehicles = input("Number vehicles?(int) \n")
    check_input = is_int(number_vehicles)
    return int(number_vehicles) if check_input else getNumberVehicles(False)

def getCapacities(r):
    if r == False:
        print('Type error!Enter a number!')
    capacities = input("Vehicle capacities?(int) \n")
    check_input = is_int(capacities)
    return int(capacities) if check_input else getCapacities(False)

def getMaxTravelDistance(r):
    if r == False:
        print('Type error!Enter a number!')
    max_travel_distance = input("Max travel distance(m)?(int) \n")
    check_input = is_int(max_travel_distance)
    return int(max_travel_distance) if check_input else getMaxTravelDistance(False)

def get_infoMatrix(e,start_time):
    data = e
    # urlApi = "http://10.92.203.155/table/v1/driving/" + data + '?annotations=distance,duration'
    urlApi = "http://router.project-osrm.org/table/v1/driving/" + data + '?annotations=distance,duration'
    # urlApi = "http://10.92.200.89:5000/table/v1/driving/" + data + '?annotations=distance,duration'
    # print(urlApi)
    result = requests.get(urlApi, headers={}).json()

def vrpDistance():
    print("VRP with distances is running... \n")
    number_order = getNumberOrder(True)
    number_vehicles = getNumberVehicles(True)
    capacities = getCapacities(True)
    max_travel_distance = getMaxTravelDistance(True)

    print("\nSetting: \nNumber order: " 
        + str(number_order) + "\n" 
        + "Number vehicles: " 
        + str(number_vehicles) + "\n" 
        + "Vehicle capacities: " 
        + str(capacities) + "\n" 
        + "Max travel distance(m): " 
        + str(max_travel_distance) 
        + "\n \n" 
        + "Or-tools is running...")
    
    strGetApi = getCsvData(number_order)
    print(strGetApi)

def vrpTimesWindow():
    print("VRP with times windows is running... \n")

def get_mode_name(mode):
    modeName = {
        1: "VRP with distances",
        2: "VRP with times windows",
    }
    return modeName.get(int(mode))

def getMode():
    if str.isdigit(mode):
        if int(mode) <= 2 and int(mode) > 0:
            mode_name = get_mode_name(mode)
            print("Mode",mode,":", mode_name,"\n")
            if int(mode) == 1:
                vrpDistance()
            elif int(mode) == 2:
                vrpTimesWindow()
        else:
            mode_name = "Mode not found \n \n" + "List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n"
            print(mode, mode_name,"\n")
    elif (str(mode) == '--help' or str(mode) == '-h'):
        print("List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n")
    else:
        print("Mode not found \n \n" + "List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n")

def solver_stt(status):
    switcher = {
        0: "ROUTING_NOT_SOLVED: Problem not solved yet",
        1: "ROUTING_SUCCESS: Problem solved successfully",
        2: "ROUTING_FAIL: No solution found to the problem",
        3: "OUTING_FAIL_TIMEOUT: Time limit reached before finding a solution",
        4: "ROUTING_NOT_SOLVED: Problem not solved yet"
    }
    return switcher.get(status)

# def orDistances():

if len(sys.argv) == 2:
    mode = sys.argv[1]
    getMode()
else:
    print("Syntax Error!")
    print("python file.py <mode number>(1 ~ 2) \n" + "List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n")
    
