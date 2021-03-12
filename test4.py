import sys
from getData import getCsvData
from getData import getJsonData
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def vrpDistance():
    print("VRP with distances is running... \n")
    number_order = int(input("Number order? \n"))
    number_vehicles = int(input("Number vehicles? \n"))
    capacities = int(input("Vehicle capacities? \n"))
    max_travel_distance = int(input("Max travel distance(m)? \n"))

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
    elif (str(mode) == 'ls'):
        print("List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n")
    else:
        print("Mode not found \n \n" + "List mode: \n" + "1: VRP with distances. \n" + "2: VRP with times windows. \n")
    
if len(sys.argv) == 2:
    mode = sys.argv[1]
    getMode()
else:
    print("Syntax Error!")
    print("python file.py <mode number>(1 ~ 2)")
