from flask import Flask, render_template, json, jsonify,redirect,session
from flaskext.mysql import MySQL
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
from flask import request as getData
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from routingpy import MapboxValhalla
from flask_cors import CORS, cross_origin
from pprint import pprint
import pandas as pd
import datetime,time
from geopy.geocoders import Nominatim
from essential_generators import DocumentGenerator
from vrp_distance import orDistance
from vrp_distance import print_solution


mysql = MySQL()
app = Flask(__name__)
app.secret_key = '?? :D ??'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '123'
app.config['MYSQL_DATABASE_DB'] = 'web_demo'
app.config['MYSQL_DATABASE_HOST'] = '10.92.200.103'
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
mysql.init_app(app)

# get name address of point
geolocator = Nominatim(user_agent="http")

# get random infomation
gen = DocumentGenerator()


# @app.route('/')
# def main():
#     return render_template('index.html')

# Account ------------------------------------------------------
@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = getData.form['inputEmail']
        _password = getData.form['inputPassword']
        
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin',(_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),_password):
                session['user'] = data[0][0]
                json = {
                    'user' : session['user'],
                    'logged' : True
                }
                return jsonify(json);
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = getData.form['inputName']
        _email = getData.form['inputEmail']
        _password = getData.form['inputPassword']
        _phone = getData.form['inputPhone']
        _birth = getData.form['inputBirth']

        conn = mysql.connect()
        cursor = conn.cursor()

        if _name and _email and _password:
            
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password,_phone,_birth))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully!'})
            else:
                return json.dumps({'error':str(data[0])})
            
            cursor.close() 
            conn.close()
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
        cursor.close() 
        conn.close()
# Account ------------------------------------------------------


# Booking -------------------------------------------------------
@app.route('/booking',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def booking():
    _id_user = getData.form['user_id']
    _name = getData.form['nameBooking']
    _phone = getData.form['phoneBooking']
    _pickup_point_start = getData.form['pickup_point_start']
    _address_start = getData.form['address_start']
    _pickup_point_end = getData.form['pickup_point_end']
    _address_end = getData.form['address_end']
    _chair_type = getData.form['chair_type']
    _quantity = getData.form['quantity']
    _start_date = getData.form['start_date']
    _start_time = getData.form['start_time']
    _stop_date = getData.form['stop_date']
    _stop_time = getData.form['stop_time']

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.callproc('sp_createBooking',(_id_user,_name,_phone,_pickup_point_start,_address_start,_pickup_point_end,_address_end,_chair_type,_quantity,_start_date,_start_time,_stop_date,_stop_time))
    data = cursor.fetchall()
    if len(data) is 0:
        conn.commit()
        return formatApi({'message':'Booking created successfully!'}, 200)
    else:
        return formatApi({'error':str(data[0])}, 400)
    cursor.close() 
    conn.close()
@app.route('/booking-data-didi',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def booking_data_didi():
    _name_file = getData.form['name_file']
    _number_record = getData.form['number_record']
    df = pd.read_csv('./static/data_didi/total_ride_request/'+_name_file, delimiter = "\t")
    for x in range(0,int(_number_record)):
        dg = df.iloc[x].to_numpy()
        dh = dg[0].split(',')
        _id_user = 1 #default
        _name = gen.name()
        _phone = gen.phone()
        _pickup_point_start = geolocator.reverse(dh[4]+","+dh[3])
        _address_start = dh[4]+","+dh[3]
        _pickup_point_end = geolocator.reverse(dh[4]+","+dh[3])
        _address_end = dh[6]+","+dh[5]
        _chair_type = 1 #default
        _quantity = 1 #default
        _start_date = cvTime(dh[1])
        _start_time = cvTime(dh[1], '%H:%M')
        _stop_date = cvTime(dh[2])
        _stop_time = cvTime(dh[2], '%H:%M')
        record = (_id_user,_name,_phone,_pickup_point_start,_address_start,_pickup_point_end,_address_end,_chair_type,_quantity,_start_date,_start_time,_stop_date,_stop_time)
        _id = insert_varibles_into_table("sp_createBooking", record)
    return formatApi({'message':'Booking data DIDI successfully!'}, 200)
   
@app.route('/booking-array',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def bookingArray():
    dataInput = getData.form
    databooking = json.loads(dataInput['databooking'])
    for item in databooking:
        _id_user = 1 #default
        _name = gen.name()
        _phone = gen.phone()
        _pickup_point_start = geolocator.reverse(item['address_start'])
        _address_start = item['address_start']
        _pickup_point_end = geolocator.reverse(item['address_end'])
        _address_end = item['address_end']
        _chair_type = 0 #default
        _quantity = 1 #default
        _start_date = item['start_date']
        _start_time = item['start_time']
        _stop_date = item['stop_date']
        _stop_time = item['stop_time']
        insert_varibles_into_table('sp_createBooking',(_id_user,_name,_phone,_pickup_point_start,_address_start,_pickup_point_end,_address_end,_chair_type,_quantity,_start_date,_start_time,_stop_date,_stop_time))
    return formatApi({'message':'Booking created successfully!'}, 200)

@app.route('/destroy-booking',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def destroyBooking():
    order_trip = delete_data_into_table("order_trip", (), "true")
    trip = delete_data_into_table("trip", (), "true")
    point_running = delete_data_into_table("point_running", (), "true")
    if order_trip == trip == point_running == "true":
       return formatApi({'message':'Delete booking successfully!'}, 200)
    else: 
       return formatApi({'message':'Error!'}, 500)

@app.route('/get-all-booking',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getAllBooking():
    user_id = 1;
    sql_get_booking = """SELECT * FROM `order_trip` WHERE `user_id` = %s AND `trip_id` IS NUll""";
    records = select_data_into_table(sql_get_booking, user_id, "true")
    data = []
    if len(records) > 0:
        startLat = float(records[0][6].split(",")[0]) - 0.02
        startLng = float(records[0][6].split(",")[1]) - 0.02
        strMatrixData = str(startLng) + "," + str(startLat)
        startPointName = geolocator.reverse(str(startLat) + "," + str(startLng));
        startPoint = str(startLat) +","+ str(startLng);
        dataAllPoint = [{
            "point_name": str(startPointName),
            "point": str(startPoint),
            "type": "start"
        }]
        for item in records:
            strMatrixData = strMatrixData + ";" + ','.join(item[6].split(",")[::-1]) + ";" + ','.join(item[8].split(",")[::-1]);
            data.append({
                "id": item[0],
                "user_id": item[1],
                "trip_id": item[2],
                "name": item[3],
                "phone": item[4],
                "pickup_point_start": item[5],
                "address_start": item[6],
                "pickup_point_end": item[7],
                "address_end": item[8],
                "chair_type": item[9],
                "quantity": item[10],
                "start_date": item[11],
                "start_time": item[12],
                "stop_date": item[13],
                "stop_time": item[14],
            })
            dataAllPoint.append({
                "id": item[0],
                "name": item[3],
                "point_name": item[5],
                "point": item[6],
                "type": "up"
            })
            dataAllPoint.append({
                "id": item[0],
                "name": item[3],
                "point_name": item[7],
                "point": item[8],
                "type": "down"
            })
        return formatApi({
                'data': data,
                'dataAllPoint': dataAllPoint,
                'strMatrixData': strMatrixData,
                'message': "Get data success!"
            }, 200)
    else: 
        return formatApi({
                'data': [],
                'dataAllPoint': [],
                'strMatrixData': [],
                'message': "No data!"
            }, 200)


# Booking -------------------------------------------------------
# Trip ----------------------------------------------------------

@app.route('/save_trip',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def save_trip(): 
    dataTripCv = json.loads(getData.form['dataTripCv'])["dataTripCv"]
    for trip in dataTripCv:
        if len(trip) > 2:
            vl_car_id = 1
            vl_blank_seats = 10
            vl_seated = 10
            vl_name_start_point = trip[0]['point_name']
            vl_start_point = trip[0]['point']
            vl_name_stop_point = trip[len(trip) - 1]['point_name']
            vl_stop_point = trip[len(trip) - 1]['point']
            vl_note = ""
            record = (vl_car_id, vl_blank_seats,vl_seated,vl_name_start_point,vl_start_point,vl_name_stop_point,vl_stop_point,vl_note)
            trip_id = insert_varibles_into_table('sp_createTrip', record)
            for point in trip:
                if point['type'] != 'start':
                    vl_p_name = point['point_name'],
                    vl_p_address = point['point'],
                    vl_p_pick_up = 1 if point['type'] == 'up'  else 0,
                    vl_p_drop = 1 if point['type'] == 'down' else 0,
                    vl_trip_id = trip_id,
                    vl_id = point['id'],
                    record = (vl_p_name, vl_p_address, vl_p_pick_up, vl_p_drop, vl_trip_id)
                    insert_varibles_into_table('sp_createPointRunning',  record)
                    insert_varibles_into_table('sp_updateOrderTrip',  (vl_id,vl_trip_id))
    return formatApi({ 'message': "Save trip success!" }, 200)
    
@app.route('/get_trip',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_trip():
    _trip_id = getData.form['trip_id'];
    if _trip_id == '': 
        sql_select_item_trip = """SELECT `id` FROM `trip` ORDER BY id DESC LIMIT 1"""
        _trip_id = select_data_into_table(sql_select_item_trip, (), "true")[0]
    result = select_data_into_table('sp_getDetailTrip', (_trip_id,), "false")
    trips_data = []
    # print(cursor.execute("select *, MAX(p_pick_up) from point_running where point_running.trip_id = 1 GROUP BY point_running.p_address"))
    for trips in result:
        result_p = select_data_into_table('sp_getPoint', (_trip_id,), "false")
        points_data = []
        point_start = {
            'name': trips[3],
            'address': trips[4],
            'pick_up_number': 0,
            'drop_number': 0,
            'type': 'start'
        }
        points_data.append(point_start)
        for points in result_p:
            point_data = {
                    'name': points[0],
                    'address': points[1],
                    'pick_up_number': points[2],
                    'drop_number': points[3],
                    'type': "go"
                    }
            points_data.append(point_data)
        point_stop = {
            'name': trips[5],
            'address': trips[6],
            'pick_up_number': 0,
            'drop_number': 0,
            'type': 'stop'
        }
        points_data.append(point_stop)
        result_order = select_data_into_table('sp_getOrder', (), "false")
        list_orders = []
        for orders in result_order:
            list_orders.append(orders[0])
        trips_data = {
                'id': trips[0],
                'car_id': trips[1],
                'blank_seats': trips[2],
                'seated': trips[3],
                'name_start_point': trips[4],
                'start_point': trips[5],
                'name_stop_point': trips[6],
                'stop_point': trips[7],
                'list_point': points_data
        }

    return formatApi(trips_data)

@app.route('/get_all_trip',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_all_trip():
    trip_data = [];
    result = select_data_into_table("getAllTrips", (), "false")
    for trip in result:
        trip_data.append({
            "id": trip[0],
            "car_id": trip[1],
            "blank_seats": trip[2],
            "seated": trip[3],
            "name_start_point": trip[4],
            "start_point": trip[5],
            "name_stop_point": trip[6],
            "stop_point": trip[7],
            "note": trip[8] ,
        })
    return formatApi({
        'data': trip_data,
        'message': "Get data success!"
        }, 200)


# Trip ----------------------------------------------------------

@app.route('/get_name_address',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_name_address():
    coordinates = getData.form['coordinates']
    name_address = geolocator.reverse(coordinates)
    return formatApi({
            'name_address': str(name_address),
            'message':'Booking data DIDI successfully!'
        }, 200)


@app.route('/orDistances', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def orDistances():
    dataInput = getData.form
    result = orDistance(dataInput)
    return formatApi(result)

# function helper -----------------------------------------------

def formatApi(data,status=200):
    json = {
        "status": status,
        "data": data
    }
    return jsonify(json);
def insert_varibles_into_table(insert_query, record):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        cursor.callproc(insert_query, record)
        connection.commit()
        cursor.execute('SELECT last_insert_id()')
        return cursor.fetchone()[0]
    except Exception as fail:
        print("Failed to insert into MySQL table {}".format(fail))
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
def select_data_into_table(select_query, record, isExecute):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        # if isFirstRecord == "true": 
        if isExecute == "true":
            cursor.execute(select_query, record)
            records = cursor.fetchall()
            return records
        else: 
            cursor.callproc(select_query, record)
            records = cursor.fetchall()
            return records
                
    except Exception as fail:
        print("Failed to insert into MySQL table {}".format(fail))
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
def delete_data_into_table(delete_table, record, isDeleteAll):
    try:
        connection = mysql.connect()
        cursor = connection.cursor()
        if isDeleteAll == "true":
            sql_destroy = ("DELETE from "+delete_table);
            cursor.execute(sql_destroy)
            connection.commit()
            return "true"
        else: 
            cursor.execute(delete_table, record)
            connection.commit()
            return "true"
    except Exception as fail:
        print("Failed to insert into MySQL table {}".format(fail))
    finally:
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
def cvTime(value, formatVl = '%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.fromtimestamp(int(value)).strftime(formatVl)
# function helper -----------------------------------------------
if __name__ == "__main__":
    print('a')
    app.run(host='0.0.0.0',port=8003)
