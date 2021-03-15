'''
    FMM web application
    Author: Can Yang
'''
from flask import Flask
from flask_cors import CORS
import os
import tornado.wsgi
import tornado.httpserver
import time
import optparse
import logging
import shell
import flask
import requests
from flask import jsonify
from glob import glob
from flask import request
from flask import session
import numpy as np
import json
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
"""Run livereload server"""
from livereload import Server
import urllib3
# from Account import showSignUp

app = flask.Flask(__name__,static_url_path='/static')
CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = '/static/inputGPS'
app.config['MAX_CONTENT_PATH'] = 1000000
app.config['CORS_HEADERS'] = 'Content-Type'
app.debug = True

server = Server(app.wsgi_app)

server.watch("templates/*.html")
server.watch("static/css/*.css")
server.watch("static/sass/*.scss")
server.watch("static/script/client/*.js")
server.watch("static/script/*.js")

@app.route('/layout/header.html')
def header():
    return flask.render_template('layout/header.html')
@app.route('/')
def index():
    return flask.render_template('home.html')
@app.route('/booking.html')
def booking():
    return flask.render_template('booking.html')
@app.route('/vrp.html')
def vrp():
    return flask.render_template('vrp.html')
@app.route('/createdata.html')
def createdata():
    return flask.render_template('createdata.html')
@app.route('/get-vehicle.html', methods=['POST'])
def get_vehicle():
    dataDemo = {
        "name": "Xe A",
        "seats": "12",
        "location": [
            {
                "address": "21.0247401,105.7883781", # diem khoi hanh
                "number": 0,
                "type": "start",
                "name": "78 Duy Tan"
            },
            {
                "address": "21.0303347,105.7835052",# diem don 1
                "number": 4,
                "type": "go",
                "name": "Address 1"
            },
            {
                "address": "21.0342386,105.7900572",# diem don 2
                "number": 3,
                "type": "go",
                "name": "Address 2"
            },
            {
                "address": "21.0350735,105.8045825",# diem don 3
                "number": 5,
                "type": "go",
                "name": "Address 3"
            },
            {
                "address": "21.0320000,105.8128000",# diem tra khach
                "number": 0,
                "type": "end",
                "name": "Lotee Center"
            }
        ]
    };
    return formatApi(dataDemo)

@app.route('/load-maps.html', methods=['POST'])
def load_maps():
    # data = {
    #     markers =
    # }
    data = request.form
    search = 'Ha Noi'
    print("------------map------------")
    map = "https://nominatim.openstreetmap.org/search.php?q="+ search +"&polygon_geojson=1&format=jsonv2"
    response = requests.get(map)
    print(response.json())
    # print(data);
    return formatApi([data])
@app.route('/search-maps.html', methods=['POST'])
def search_maps():
    data = request.form
    print("------------search map------------")
    map = "https://nominatim.openstreetmap.org/search.php?q="+ data["name"] +"&polygon_geojson=1&format=jsonv2"
    response = requests.get(map)
    return formatApi(response.json())

@app.route('/get-distance.html', methods=['POST'])
def get_distance():
    data = request.form
    print(data['search'])
    map = "https://routing.openstreetmap.de/routed-bike/route/v1/driving/"+data['search']+"?overview=false&geometries=polyline&steps=true"
    result = requests.get(map)
    data = {
        "result": result.json(),
        "style": {
            "color": "rgb(0, 51, 255)",
            "opacity": 0.5,
            "weight": 5,
            "class": "animate"
        }
    }
    return formatApi(data)

@app.route('/get-distanceMatrix.html', methods=['POST'])
def get_distanceMatrix():
    data = request.form
    matrix = data['matrix']
    # urlApi = "http://127.0.0.1:5000/table/v1/driving/"+ matrix +"?annotations=distance,duration"
    urlApi = "http://router.project-osrm.org/table/v1/driving/" + matrix + '?annotations=distance,duration'
    # print(urlApi)
    headers = {}
    result = requests.get(urlApi, headers=headers)
    # print(result.json());
    return formatApi(result.json())

def print_solution(data, manager, routing, solution):
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        arrTrip = []
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            arrTrip.append(format(manager.IndexToNode(index)))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(arrTrip)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))
@app.route('/orDistance.html', methods=['POST'])
def avr():
    data = request.json
    # print(data['matrixDistance'][18:-1])
    matrix = json.loads(data['matrixDistance'][18:-1])
    n = len(matrix)
    # print(matrix[0][0])
    # print(matrix[0][1])
    # print(matrix[1][0])
    # print(matrix[1][1])
    matrix_data = []
    for x in range(n):
        arr_data = []
        for y in range(n):
            arr_data.append(matrix[x-1][y-1])
        matrix_data.append(arr_data)
    data = {}
    data['distance_matrix'] = matrix_data
    data['num_vehicles'] = 2
    data['depot'] = 0
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(data, manager, routing, solution)
    # return 'a'

@app.route('/get-list-file')
def get_list_file():
    arr = os.listdir("/home/share/web_demo/dial-a-ride-solver/src/web/static/data_didi/total_ride_request")
    return formatApi(arr)


def formatApi(data,status=200):
    json = {
        "status": status,
        "data": data
    }
    return jsonify(json)

# ///////////////// Admmin /////////////////////

@app.route('/admin/layout/header.html')
def admin_layout():
    return flask.render_template('/admin/layout/header.html')
@app.route('/admin')
def admin():
    return flask.render_template('/admin/main_management.html')
@app.route('/admin/vehicle-management.html')
def vehicle_management():
    return flask.render_template('/admin/vehicle_management.html')
@app.route('/admin/trip-management.html')
def trip_management():
    return flask.render_template('/admin/trip_management.html')



# ///////////////// Admmin /////////////////////



@app.route('/showSignUp')
def showSignUp():
    return flask.render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return flask.render_template('userHome.html')
    else:
        return flask.render_template('signin.html')

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return flask.render_template('userHome.html')
    else:
        return flask.render_template('error.html',error = 'Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


server.serve(debug=True,host='0.0.0.0', port=8002) 