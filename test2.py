import random
import requests
import time
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import webbrowser
import logging
from datetime import datetime
from getData import getCsvData
from getData import getJsonData

# limit time function
# =========================================================
# import signal
# from contextlib import contextmanager

# class TimeoutException(Exception): pass

# @contextmanager
# def time_limit(seconds):
#     def signal_handler(signum, frame):
#         raise TimeoutException("Timed out!")
#     signal.signal(signal.SIGALRM, signal_handler)
#     signal.alarm(seconds)
#     try:
#         yield
#     finally:
#         signal.alarm(0)
# =========================================================

# Creat Random data orders
# --------------------------------------------------------------------
# so don dat hang
num_orders = 25
print('Order list:(' + str(num_orders) + ' orders)')

# so luong phuong tien
num_vehicles = 5
print('Vehicles:(' + str(num_vehicles) + ')')

# suc chua
vehicle_capacities = 20
print('Capacitie:(' + str(vehicle_capacities) + ' slot)')

# khoang cach di chuyen toi da (m)
max_travel_distance = 20000
print('Max travel distance:(' + str(max_travel_distance) + ' m)')

# vehicle maximum travel distance
vehicle_maximum_travel_distance = 30000  

# maximum time per vehicle
maximum_time_per_vehicle = 300000  

# toa do ben xe
# depot = [21.04232, 105.81245]
depot = [35.0471975,135.7865344]

# duong gioi han: tren - phai - duoi -trai
# limitBor = [21.0416, 105.8562, 20.9907, 105.7465]
limitBor = [43.7742, 142.4490, 43.7062, 142.4067]

#thoi gian hoat dong (24h)
workingTime_start = 9
workingTime_end = 12
workingTime = workingTime_end - workingTime_start

#thoi gian di chuyen chenh lech
time_deviation = 60

#thoi gian cho(+-)
wait_time = 10

# --------------------------------------------------------------------

def solver_stt(status):
    switcher = {
        0: "ROUTING_NOT_SOLVED: Problem not solved yet",
        1: "ROUTING_SUCCESS: Problem solved successfully",
        2: "ROUTING_FAIL: No solution found to the problem",
        3: "OUTING_FAIL_TIMEOUT: Time limit reached before finding a solution",
        4: "ROUTING_NOT_SOLVED: Problem not solved yet"
    }
    return switcher.get(status)
def creatematrixPoint(e,i,t):
    pointList = str(i[1]) + ',' + str(i[0])
    # latEnd = random.uniform(t[0], t[2])
    # lngEnd = random.uniform(t[1], t[3])
    latEnd = '35.0848179'
    lngEnd = '135.7932127'
    pointList = pointList + ';' + str(lngEnd) + ',' + str(latEnd)
    # for x in range(e):
    #     latStart = random.uniform(t[0], t[2])
    #     lngStart = random.uniform(t[1], t[3])
    #     # latEnd = random.uniform(t[0], t[2])
    #     # lngEnd = random.uniform(t[1], t[3])
    #     pointList = pointList + ';' + str(lngStart) + ',' + str(latStart)
        # print(' - ',(x + 1),': Start', str(lngStart) + ',' + str(latStart), ' End: ', str(lngEnd) + ',' + str(latEnd))
    inputPoint = getCsvData(num_orders)
    pointList = pointList + inputPoint
    return pointList
def get_infoMatrix(e,start_time):

    data = e
    # urlApi = "http://10.92.203.155/table/v1/driving/" + data + '?annotations=distance,duration'
    urlApi = "http://router.project-osrm.org/table/v1/driving/" + data + '?annotations=distance,duration'
    # urlApi = "http://10.92.200.89:5000/table/v1/driving/" + data + '?annotations=distance,duration'
    # print(urlApi)
    result = requests.get(urlApi, headers={}).json()

    # ===============================
    # create time_window
    time_windows = [(0,0),(workingTime * 3600 - (wait_time * 60),workingTime * 3600 + (wait_time * 60))]
    w = result['durations']
    length_time_windows = len(w)
    earliest_timeOrder = 0
    latest_timeOrder = workingTime * 3600
    for x in range(2,num_orders + 1):
        startTimeOrderLimit = int(w[0][x])
        endTimeOrderLimit = int(latest_timeOrder - w[x][2])
        randomStartTimeOrder = int(random.randrange(startTimeOrderLimit, endTimeOrderLimit))
        randomEndTimeOrder = int(randomStartTimeOrder + w[x][2] + (time_deviation * 60))
        time_windows.append((randomStartTimeOrder - (wait_time * 60),randomStartTimeOrder + (wait_time * 60)))
        # time_windows.append((randomEndTimeOrder - (wait_time * 60),randomEndTimeOrder + (wait_time * 60)))
        # time_windows.append((14400 - (wait_time * 60),14400 + (wait_time * 60)))
    result.update({"time_windows":time_windows})
    result.update({"type_input":'Random'})
    # ===============================

    # =================================
    # fix data input
    # fix_input = {'code': 'Ok', 'distances': [[0, 4846, 1382.5, 4592.5, 6448.8, 5771.1, 3606.8, 3780.2, 6122, 3776.3, 1615.7, 1904, 4104.5, 2868.3, 4127.8, 4979.3, 4563.3, 3686.7, 4344.5, 3829.2, 4413.6], [4846, 0, 5574.8, 3400.7, 1712.3, 3483, 4385.2, 1970.1, 3223.7, 1057.1, 4382.1, 5104, 969.5, 2264.2, 3864.2, 4359.2, 2024.4, 5887.2, 4994, 2221.7, 2768.9], [1382.5, 5574.8, 0, 5298.4, 7177.6, 6812.9, 3501.1, 4822, 7163.8, 4505.1, 1390.7, 527.3, 4833.3, 3597.1, 4022.1, 4873.5, 5605.1, 2687.6, 4238.7, 4535.1, 5118.9], [4592.5, 3400.7, 5298.4, 0, 5003.5, 2081.3, 1796.7, 1466, 3019, 2954.4, 4047.8, 4769.7, 2656.3, 2010.7, 1275.7, 958.5, 1377.9, 3142.2, 1593.2, 1179, 633.4], [6468.4, 1731.9, 7197.1, 5023.1, 0, 4194.2, 6007.5, 3592.5, 3440.6, 2679.5, 6004.5, 6726.4, 2591.9, 3886.6, 5486.5, 5981.6, 3646.8, 7509.6, 6616.3, 3844.1, 4391.2], [5771.1, 3483, 6812.9, 2081.3, 4028.1, 0, 3570.1, 1990.8, 937.7, 3448.4, 5562.3, 6284.2, 3360.8, 3189.3, 3049.1, 2505.7, 1458.6, 4689.4, 3140.4, 2277.8, 1952.3], [3486.5, 4385.2, 3501.1, 1796.7, 5988, 3570.1, 0, 2450.4, 3921, 3938.8, 2250.5, 2972.4, 3640.8, 2995.1, 521, 1677.4, 2362.3, 1502.5, 1042.6, 2163.5, 1617.9], [3780.2, 1970.1, 4822, 1466, 3572.9, 1990.8, 2450.4, 0, 2341.7, 1935.5, 3571.4, 4293.4, 1696.3, 1198.5, 1929.4, 2424.4, 783.1, 3952.5, 3059.2, 286.9, 1287.1], [6122, 3223.7, 7163.8, 2936.6, 3274.6, 937.7, 3921, 2341.7, 0, 3189.1, 5913.2, 6635.1, 3101.5, 3540.2, 3400, 3443.4, 1558.7, 5423.6, 4078.2, 2628.7, 2303.2], [3776.3, 1057.1, 4505.1, 2954.4, 2659.9, 3448.4, 3938.8, 1994.4, 3189.1, 0, 3938.7, 4127.9, 273.9, 944.1, 3417.8, 3912.8, 1989.8, 5440.8, 4547.6, 2191.1, 2775.5], [1571.7, 4382.1, 1390.7, 4047.8, 5984.9, 5562.3, 2250.5, 3571.4, 5913.2, 3938.7, 0, 863.3, 3640.6, 2995, 2771.5, 3622.9, 4354.5, 2330.3, 2988.2, 3284.5, 3868.3], [1859.9, 5104, 527.3, 4769.7, 6706.8, 6284.2, 2972.4, 4293.4, 6635.1, 4127.9, 863.3, 0, 4362.5, 3219.9, 3493.4, 4344.8, 5076.4, 2651.6, 3710.1, 4006.4, 4590.2], [4104.5, 969.5, 4833.3, 2656.3, 2572.3, 3360.8, 3640.8, 1696.3, 3101.5, 273.9, 3640.6, 4362.5, 0, 856.8, 3119.8, 3614.8, 1902.1, 5142.8, 4249.6, 1893.1, 2477.5], [2868.3, 2264.2, 3597.1, 2010.7, 3867, 3189.3, 2995.1, 1198.5, 3540.2, 944.1, 2995, 3219.9, 856.8, 0, 2474.1, 2969.1, 1981.5, 4497.2, 3603.9, 1247.4, 1831.8], [4007.5, 3864.2, 4022.1, 1275.7, 5467, 3049.1, 521, 1929.4, 3400, 3417.8, 2771.5, 3493.4, 3119.8, 2474.1, 0, 2198.4, 1841.3, 2023.5, 1563.6, 1642.5, 1096.9], [4858.9, 4359.2, 4873.5, 958.5, 5962, 2505.7, 1677.4, 2424.4, 3443.4, 3912.8, 3622.9, 4344.8, 3614.8, 2969.1, 2234.2, 0, 2336.3, 2183.7, 634.8, 2137.5, 1591.9], [4563.3, 2024.4, 5605.1, 1377.9, 3627.2, 1458.6, 2362.3, 783.1, 1558.7, 1989.8, 4354.5, 5076.4, 1902.1, 1981.5, 1841.3, 2336.3, 0, 3864.9, 2971.1, 1070, 744.5], [3642.6, 5887.2, 2687.6, 3142.2, 7490, 4689.4, 1502.5, 3952.5, 5423.6, 5440.8, 2330.3, 2651.6, 5142.8, 4497.2, 2023.5, 2183.7, 3864.9, 0, 1548.9, 3665.5, 3120.4], [4224.2, 4994, 4238.7, 1593.2, 6596.7, 3140.4, 1042.6, 3059.2, 4078.2, 4547.6, 2988.2, 3710.1, 4249.6, 3603.9, 1563.6, 634.8, 2971.1, 1548.9, 0, 2772.3, 2226.6], [3829.2, 2221.7, 4535.1, 1179, 3824.5, 2277.8, 2163.5, 286.9, 2628.7, 2187.1, 3284.5, 4006.4, 1893.1, 1247.4, 1642.5, 2137.5, 1070, 3665.5, 2772.3, 0, 1000.2], [4413.6, 2768.9, 5118.9, 633.4, 4371.7, 1952.3, 1617.9, 1276.7, 2303.2, 2775.5, 3868.3, 4590.2, 2477.5, 1831.8, 1096.9, 1591.9, 744.5, 3120.4, 2226.6, 1000.2, 0]], 'durations': [[0, 517.7, 165.1, 460.7, 708.5, 588.4, 367.9, 410.9, 648.7, 454.7, 222, 228.6, 449.9, 335.8, 407, 472.8, 483.6, 403.4, 425.1, 403.8, 449.5], [511.1, 0, 548, 298.3, 219.2, 333.6, 377.7, 191.2, 327.4, 159.7, 464, 546.3, 141.8, 234.8, 338.6, 377.6, 198.4, 528.2, 425.3, 204.1, 258.2], [171.8, 554.7, 0, 443.4, 745.5, 581.3, 308.5, 403.8, 641.6, 491.7, 181.8, 72.1, 486.9, 372.8, 347.6, 413.4, 476.5, 308.7, 365.7, 379, 431.9], [456.3, 304.9, 443.3, 0, 495.7, 162.3, 138.8, 122.3, 278.6, 278.3, 357.3, 439.6, 240.6, 179.9, 99.7, 79.3, 114.4, 312.6, 127, 97.5, 54.6], [698.6, 209.3, 735.5, 485.8, 0, 459.5, 565.2, 378.7, 366.3, 354.9, 651.5, 733.8, 337, 422.3, 526.1, 565.1, 385.9, 715.7, 612.8, 391.6, 445.7], [585.1, 339.2, 584.5, 165.6, 450.1, 0, 289.3, 178.4, 116.3, 349.7, 498.5, 580.8, 331.8, 308.8, 250.2, 192.2, 137.5, 425.5, 239.9, 202.3, 165.9], [370.1, 381, 311.7, 142, 571.8, 289.4, 0, 198.4, 348.3, 354.4, 225.7, 308, 316.7, 256, 39.1, 134, 183.2, 180.7, 86.3, 173.6, 123.4], [406.7, 195.9, 406.1, 118.1, 386.7, 177.5, 197.5, 0, 237.8, 206.4, 320.1, 402.4, 174.8, 130.4, 158.4, 197.4, 72.7, 348, 245.1, 23.9, 106.9], [645.4, 337.2, 644.8, 276.2, 363.5, 116.3, 348.3, 238.7, 0, 347.7, 558.8, 641.1, 329.8, 369.1, 309.2, 308.5, 165.1, 529, 356.2, 262.6, 224.9], [448.1, 156.4, 485, 271.6, 354.9, 350.7, 351, 207.7, 344.5, 0, 433.8, 506.1, 44.8, 141.1, 311.9, 350.9, 215.5, 508.9, 398.6, 214.7, 260.4], [222.9, 467.2, 178.4, 360.6, 658, 498.5, 225.7, 321, 558.8, 437.1, 0, 131.9, 399.4, 346.1, 264.8, 330.6, 393.7, 261.2, 282.9, 296.2, 349.1], [229.7, 549.6, 75.4, 443, 740.4, 580.9, 308.1, 403.4, 641.2, 509.4, 138.6, 0, 481.8, 392, 347.2, 413, 476.1, 326.1, 365.3, 378.6, 431.5], [446.5, 141.8, 483.4, 237.2, 340.3, 336.1, 316.6, 173.3, 329.9, 41.6, 399.4, 481.7, 0, 125.4, 277.5, 316.5, 200.9, 474.5, 364.2, 180.3, 226], [334.8, 233.8, 371.7, 176.6, 424.6, 304.5, 256, 127, 364.8, 144.4, 346.2, 394.3, 125.4, 0, 216.9, 255.9, 199.7, 413.9, 303.6, 119.7, 165.4], [409.2, 341.9, 350.8, 102.9, 532.7, 250.3, 39.1, 159.3, 309.2, 315.3, 264.8, 347.1, 277.6, 216.9, 0, 173.1, 144.1, 219.8, 125.4, 134.5, 84.3], [475, 380.9, 416.6, 76, 571.7, 192.2, 140.6, 198.3, 308.5, 354.3, 330.6, 412.9, 316.6, 255.9, 175.7, 0, 190.4, 233.3, 47.7, 173.5, 130.6], [480.3, 201.7, 479.7, 111.1, 392.5, 135.2, 183.2, 73.6, 165.1, 212.2, 393.7, 476, 194.3, 204, 144.1, 190.4, 0, 363.9, 238.1, 97.5, 59.8], [407.6, 534.7, 308.8, 306, 725.5, 422.2, 183.9, 352.1, 532.2, 515.5, 257.9, 329.3, 477.8, 417.1, 223, 230, 367.1, 0, 182.3, 327.3, 307.3], [427.3, 428.6, 368.9, 123.7, 619.4, 239.9, 92.9, 246, 356.2, 402, 282.9, 365.2, 364.3, 303.6, 132, 47.7, 238.1, 185.6, 0, 221.2, 178.3], [402.6, 207.4, 382.2, 94.2, 398.2, 202.3, 173.6, 24.8, 262.6, 217.9, 296.2, 378.5, 186.9, 126.2, 134.5, 173.5, 97.5, 324.1, 221.2, 0, 83], [448.4, 261.5, 435.1, 51.3, 452.3, 166, 123.4, 113.8, 224.9, 270.4, 349.1, 431.4, 232.7, 172, 84.3, 130.6, 59.8, 304.1, 178.3, 89.6, 0]], 'sources': [{'hint': 'p4c8jqmHPI6hAAAAIgAAAAAAAAAAAAAAkmvhQqwKukEAAAAAAAAAAKEAAAAiAAAAAAAAAAAAAABXGAEA6ut8CFjLmwL463wI3MubAgAALxEdsCRh', 'distance': 14.709334, 'location': [142.404586, 43.764568], 'name': ''}, {'hint': '0ZNtgaU5PI4AAAAAEAAAAE4AAABbAAAAAAAAAObEMUFgIVtCYgt-QgAAAAAQAAAATgAAAFsAAABXGAEAZyR9CGNBmwIuKX0IOkKbAgUATwsdsCRh', 'distance': 101.400805, 'location': [142.419047, 43.729251], 'name': '風防林道路線'}, {'hint': 'KpA8jiyQPI4sAAAAEgAAAAAAAAAAAAAAKPRGQlK6mUEAAAAAAAAAACwAAAASAAAAAAAAAAAAAABXGAEAkRd9CJjomwKiF30INumbAgAALxEdsCRh', 'distance': 17.608133, 'location': [142.415761, 43.772056], 'name': '神居旭山通'}, {'hint': 'HZ5tgcudbYFAAAAAwgAAAO8AAAAGAAAAbWatQlJpgUOftZ9DiJwDQUAAAADCAAAA7wAAAAYAAABXGAEAXH99CHp7mwI4gH0ItYObAgMA7wUdsCRh', 'distance': 234.769966, 'location': [142.442332, 43.744122], 'name': '東川旭川線'}, {'hint': 'G3U8jkB1PI6KAAAAVwAAAAAAAAA8AAAAmwXBQj1scEIAAAAAdzQmQooAAABXAAAAAAAAADwAAABXGAEADil9CFMfmwKCKX0IER-bAgAAbwIdsCRh', 'distance': 11.880233, 'location': [142.420238, 43.720531], 'name': ''}, {'hint': 'wZ1tgdWdbYEHAQAALAAAAIcAAAD1AAAAjWSvQxDvZUJ_ajNDV3ujQwcBAAAsAAAAhwAAAPUAAABXGAEA54V9CCo7mwLNjH0IzjqbAgMAjwsdsCRh', 'distance': 142.667466, 'location': [142.444007, 43.727658], 'name': '上4号線'}, {'hint': 'HJ5tgSGebYEMAQAAbAAAAAgDAAAHAAAAQsiyQ8qxDkM7IIFECaEcQQwBAABsAAAACAMAAAcAAABXGAEAmHB9CEStmwJ9dH0IEa2bAgYATwAdsCRh', 'distance': 80.469214, 'location': [142.438552, 43.756868], 'name': '上川東部広域農道'}, {'hint': 'L388jkV_PI4PAAAAWwAAAAAAAADLAAAAM3KNQZuDx0IAAAAALbBhQw8AAABbAAAAAAAAAMsAAABXGAEAXU99CNdsmwK6T30IL22bAgAA_wcdsCRh', 'distance': 12.318768, 'location': [142.430045, 43.740375], 'name': '旭川旭岳温泉線'}, {'hint': 'S388jkx_PI4AAAAAhQAAAAAAAAAAAAAAAAAAAPUvuEIAAAAAAAAAAAAAAACFAAAAAAAAAAAAAABXGAEAxG59CDkrmwJzc30IWCebAgAAPwAdsCRh', 'distance': 146.650421, 'location': [142.438084, 43.723577], 'name': ''}, {'hint': 'Ozw8jkQ8PI4RAAAABAEAAAAAAAAAAAAAaQ0-QSXHNEMAAAAAAAAAABEAAAAEAQAAAAAAAAAAAABXGAEAght9COBfmwKIG30IH2CbAgAA7wUdsCRh', 'distance': 7.016337, 'location': [142.41677, 43.737056], 'name': ''}, {'hint': '2ow8jtuMPI4AAAAAmgAAAEsAAAAAAAAAAAAAAP7vAEL8FHlBAAAAAAAAAABNAAAAJQAAAAAAAABXGAEAqDF9CErMmwLJMn0Iac6bAgIALxEdsCRh', 'distance': 64.662251, 'location': [142.42244, 43.76481], 'name': ''}, {'hint': 'xo88juePPI4nAAAAJwAAAE8AAAAAAAAAIhfcQbEQ1EGkpVtCAAAAACcAAAAnAAAATwAAAAAAAABXGAEAnSZ9CK3gmwJZJn0IsOCbAgEATwAdsCRh', 'distance': 5.484885, 'location': [142.419613, 43.770029], 'name': ''}, {'hint': 'L5RtgQg8PI5kAAAAAwAAAAAAAAA5AAAAJf-KQnmS1T8AAAAAuKMeQmQAAAADAAAAAAAAADkAAABXGAEAkyR9CLJimwIxI30IxGKbAgAAfwsdsCRh', 'distance': 28.594648, 'location': [142.419091, 43.737778], 'name': '風防林道路線'}, {'hint': 'rz88jsI_PI4pAAAAKAAAAAAAAAAAAAAAmLDoQVuT2UEAAAAAAAAAACkAAAAoAAAAAAAAAAAAAABXGAEAJiJ9CE19mwIZIn0ITn2bAgAAjwsdsCRh', 'distance': 1.05339, 'location': [142.41847, 43.744589], 'name': ''}, {'hint': 'HJ5tgSGebYGrAAAAcgAAAOIBAACIAQAAjH5kQyPZFkMERSBEnKgCRKsAAAByAAAA4gEAAIgBAABXGAEAxm59CP-amwJBbn0IBpubAgQATwAdsCRh', 'distance': 10.736169, 'location': [142.438086, 43.752191], 'name': '上川東 部広域農道'}, {'hint': 'w51tgaN8PI5eAAAAGgEAACECAABiAAAAo2_8QoY1u0PyVzVE0sgCQ14AAAAaAQAAIQIAAGIAAABXGAEArI59CAeTmwJGjH0IJ5ObAgMAjwsdsCRh', 'distance': 49.561441, 'location': [142.446252, 43.750151], 'name': '上4号線'}, {'hint': 'GZ5tgTt_PI5jAAAAkwAAAA0AAAAQAAAAK3HdQt1LIkPIQGtBJf-KQWMAAACTAAAADQAAABAAAABXGAEASmh9CG5amwLuYX0IwlqbAgEAjwsdsCRh', 'distance': 131.512622, 'location': [142.436426, 43.735662], 'name': '上川東部広域農道'}, {'hint': 'jIA8jo-API4vAAAAYAAAABEAAAAAAAAADHf8QRZWgEIU6zBBAAAAAC8AAABgAAAAEQAAAAAAAABXGAEAaoV9CPHUmwKEhX0I-dWbAgEALxEdsCRh', 'distance': 29.406767, 'location': [142.443882, 43.767025], 'name': ''}, {'hint': 'w51tgaN8PI6cAAAAeAEAAAYAAADhAQAAS-FQQ5zt-UMQUv5ADwcgRJwAAAB4AQAABgAAAOEBAABXGAEA6ZB9CEmpmwIoh30IzKmbAgEAjwsdsCRh', 'distance': 201.562144, 'location': [142.446825, 43.755849], 'name': '上4号線'}, {'hint': 'MH88jjV_PI6GAAAAlwAAAEQAAAAFAAAAI-syQ1ijSEMcq7RC_p3nQIYAAACXAAAARAAAAAUAAABXGAEAq099CKd2mwJATH0I1XabAgUATwAdsCRh', 'distance': 70.690781, 'location': [142.430123, 43.742887], 'name': '共栄道路線'}, {'hint': 'Hp5tgW1_PI5IAAAA2QAAAGIAAADnAAAANJnBQp74j0NVewJDMLOZQ0gAAADZAAAAYgAAAOcAAABXGAEA6Gp9CIl0mwLzaH0Io3SbAgIAjwsdsCRh', 'distance': 40.472821, 'location': [142.437096, 43.742345], 'name': '上川東部広域農道'}], 'destinations': [{'hint': 'p4c8jqmHPI6hAAAAIgAAAAAAAAAAAAAAkmvhQqwKukEAAAAAAAAAAKEAAAAiAAAAAAAAAAAAAABXGAEA6ut8CFjLmwL463wI3MubAgAALxEdsCRh', 'distance': 14.709334, 'location': [142.404586, 43.764568], 'name': ''}, {'hint': '0ZNtgaU5PI4AAAAAEAAAAE4AAABbAAAAAAAAAObEMUFgIVtCYgt-QgAAAAAQAAAATgAAAFsAAABXGAEAZyR9CGNBmwIuKX0IOkKbAgUATwsdsCRh', 'distance': 101.400805, 'location': [142.419047, 43.729251], 'name': '風防林道 路線'}, {'hint': 'KpA8jiyQPI4sAAAAEgAAAAAAAAAAAAAAKPRGQlK6mUEAAAAAAAAAACwAAAASAAAAAAAAAAAAAABXGAEAkRd9CJjomwKiF30INumbAgAALxEdsCRh', 'distance': 17.608133, 'location': [142.415761, 43.772056], 'name': '神居旭山通'}, {'hint': 'HZ5tgcudbYFAAAAAwgAAAO8AAAAGAAAAbWatQlJpgUOftZ9DiJwDQUAAAADCAAAA7wAAAAYAAABXGAEAXH99CHp7mwI4gH0ItYObAgMA7wUdsCRh', 'distance': 234.769966, 'location': [142.442332, 43.744122], 'name': '東川旭川 線'}, {'hint': 'G3U8jkB1PI6KAAAAVwAAAAAAAAA8AAAAmwXBQj1scEIAAAAAdzQmQooAAABXAAAAAAAAADwAAABXGAEADil9CFMfmwKCKX0IER-bAgAAbwIdsCRh', 'distance': 11.880233, 'location': [142.420238, 43.720531], 'name': ''}, {'hint': 'wZ1tgdWdbYEHAQAALAAAAIcAAAD1AAAAjWSvQxDvZUJ_ajNDV3ujQwcBAAAsAAAAhwAAAPUAAABXGAEA54V9CCo7mwLNjH0IzjqbAgMAjwsdsCRh', 'distance': 142.667466, 'location': [142.444007, 43.727658], 'name': '上4号線'}, {'hint': 'HJ5tgSGebYEMAQAAbAAAAAgDAAAHAAAAQsiyQ8qxDkM7IIFECaEcQQwBAABsAAAACAMAAAcAAABXGAEAmHB9CEStmwJ9dH0IEa2bAgYATwAdsCRh', 'distance': 80.469214, 'location': [142.438552, 43.756868], 'name': '上川東部広域農道'}, {'hint': 'L388jkV_PI4PAAAAWwAAAAAAAADLAAAAM3KNQZuDx0IAAAAALbBhQw8AAABbAAAAAAAAAMsAAABXGAEAXU99CNdsmwK6T30IL22bAgAA_wcdsCRh', 'distance': 12.318768, 'location': [142.430045, 43.740375], 'name': '旭川旭岳温泉線'}, {'hint': 'S388jkx_PI4AAAAAhQAAAAAAAAAAAAAAAAAAAPUvuEIAAAAAAAAAAAAAAACFAAAAAAAAAAAAAABXGAEAxG59CDkrmwJzc30IWCebAgAAPwAdsCRh', 'distance': 146.650421, 'location': [142.438084, 43.723577], 'name': ''}, {'hint': 'Ozw8jkQ8PI4RAAAABAEAAAAAAAAAAAAAaQ0-QSXHNEMAAAAAAAAAABEAAAAEAQAAAAAAAAAAAABXGAEAght9COBfmwKIG30IH2CbAgAA7wUdsCRh', 'distance': 7.016337, 'location': [142.41677, 43.737056], 'name': ''}, {'hint': '2ow8jtuMPI4AAAAAmgAAAEsAAAAAAAAAAAAAAP7vAEL8FHlBAAAAAAAAAABNAAAAJQAAAAAAAABXGAEAqDF9CErMmwLJMn0Iac6bAgIALxEdsCRh', 'distance': 64.662251, 'location': [142.42244, 43.76481], 'name': ''}, {'hint': 'xo88juePPI4nAAAAJwAAAE8AAAAAAAAAIhfcQbEQ1EGkpVtCAAAAACcAAAAnAAAATwAAAAAAAABXGAEAnSZ9CK3gmwJZJn0IsOCbAgEATwAdsCRh', 'distance': 5.484885, 'location': [142.419613, 43.770029], 'name': ''}, {'hint': 'L5RtgQg8PI5kAAAAAwAAAAAAAAA5AAAAJf-KQnmS1T8AAAAAuKMeQmQAAAADAAAAAAAAADkAAABXGAEAkyR9CLJimwIxI30IxGKbAgAAfwsdsCRh', 'distance': 28.594648, 'location': [142.419091, 43.737778], 'name': '風防林道路線'}, {'hint': 'rz88jsI_PI4pAAAAKAAAAAAAAAAAAAAAmLDoQVuT2UEAAAAAAAAAACkAAAAoAAAAAAAAAAAAAABXGAEAJiJ9CE19mwIZIn0ITn2bAgAAjwsdsCRh', 'distance': 1.05339, 'location': [142.41847, 43.744589], 'name': ''}, {'hint': 'HJ5tgSGebYGrAAAAcgAAAOIBAACIAQAAjH5kQyPZFkMERSBEnKgCRKsAAAByAAAA4gEAAIgBAABXGAEAxm59CP-amwJBbn0IBpubAgQATwAdsCRh', 'distance': 10.736169, 'location': [142.438086, 43.752191], 'name': '上川東部広域農道'}, {'hint': 'w51tgaN8PI5eAAAAGgEAACECAABiAAAAo2_8QoY1u0PyVzVE0sgCQ14AAAAaAQAAIQIAAGIAAABXGAEArI59CAeTmwJGjH0IJ5ObAgMAjwsdsCRh', 'distance': 49.561441, 'location': [142.446252, 43.750151], 'name': '上4号線'}, {'hint': 'GZ5tgTt_PI5jAAAAkwAAAA0AAAAQAAAAK3HdQt1LIkPIQGtBJf-KQWMAAACTAAAADQAAABAAAABXGAEASmh9CG5amwLuYX0IwlqbAgEAjwsdsCRh', 'distance': 131.512622, 'location': [142.436426, 43.735662], 'name': '上川東部広域農道'}, {'hint': 'jIA8jo-API4vAAAAYAAAABEAAAAAAAAADHf8QRZWgEIU6zBBAAAAAC8AAABgAAAAEQAAAAAAAABXGAEAaoV9CPHUmwKEhX0I-dWbAgEALxEdsCRh', 'distance': 29.406767, 'location': [142.443882, 43.767025], 'name': ''}, {'hint': 'w51tgaN8PI6cAAAAeAEAAAYAAADhAQAAS-FQQ5zt-UMQUv5ADwcgRJwAAAB4AQAABgAAAOEBAABXGAEA6ZB9CEmpmwIoh30IzKmbAgEAjwsdsCRh', 'distance': 201.562144, 'location': [142.446825, 43.755849], 'name': '上4 号線'}, {'hint': 'MH88jjV_PI6GAAAAlwAAAEQAAAAFAAAAI-syQ1ijSEMcq7RC_p3nQIYAAACXAAAARAAAAAUAAABXGAEAq099CKd2mwJATH0I1XabAgUATwAdsCRh', 'distance': 70.690781, 'location': [142.430123, 43.742887], 'name': '共栄道路線'}, {'hint': 'Hp5tgW1_PI5IAAAA2QAAAGIAAADnAAAANJnBQp74j0NVewJDMLOZQ0gAAADZAAAAYgAAAOcAAABXGAEA6Gp9CIl0mwLzaH0Io3SbAgIAjwsdsCRh', 'distance': 40.472821, 'location': [142.437096, 43.742345], 'name': '上川東部広域農道'}], 'time_windows': [(0, 0), (36711, 37311), (37269, 37869), (40107, 40707), (40612, 41212), (25092, 25692), (25391, 25991), (39045, 39645), (39292, 39892), (37733, 38333), (38176, 38776), (21084, 21684), (21575, 22175), (29450, 30050), (29676, 30276), (13205, 13805), (13405, 14005), (3512, 4112), (3704, 4304)],'type_input':'Fix'}
    # result = fix_input
    # =================================

    # print(result)
    # print('\n')
    print('--------------------')
    print('Time get data API:',"%s seconds" % round((time.time() - start_time),2))
    print('\n')
    print('Input: ')
    return result
def pickup_delivery(e):
    pickups_deliveries = []
    for x in range(0,e):
        arr_pD = [x + 2,1]
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
        time_dimension = routing.GetDimensionOrDie('Time')
        total_time = 0
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += '[{0}]L({1}),T({2},{3})->'.format(node_index, route_load, assignment.Min(time_var), assignment.Max(time_var))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
            point = int(format(manager.IndexToNode(index)))
            arrTrip.append(point)
            lenArrTrip = len(arrTrip)
            if (lenArrTrip > 1):
                time_route += data['distance_matrix'][arrTrip[lenArrTrip - 2]][arrTrip[lenArrTrip - 1]]
        plan_output += '{0} L({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        # plan_output += 'Load of the route: {}\n'.format(route_load)
        plan_output += ('Time of the route: ' + str(int(time_route)) + ' s')
        print(arrTrip)
        print(plan_output)
        print('\n')
        total_distance += route_distance
        total_load += route_load
        logging.info('   ---Trip ' + str(vehicle_id) + ':' + str(plan_output))
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    # return result
def runOrTools(e,s,t,u,r,w,z,c,v):
    
    # Time start OR-Tools
    start_or_time = time.time()

    #======================================================================
    # create demand data
    demand = [0,0]
    for x in range(1, r + 1):
        # dm = random.randrange(1,3)
        demand.append(1)
        # demand.append(-1)
    print(demand)

    # create capacities data    
    capacities = []
    for x in range(1, t + 1):
        capacities.append(z)
    print(capacities)
    data = {}
    data['time_matrix'] = w
    data['distance_matrix'] = e
    # data['pickups_deliveries'] = s
    data['num_vehicles'] = t
    # data['depot'] = 0
    data['demands'] = demand
    data['vehicle_capacities'] = capacities
    data['time_windows'] = c
    data['starts'] = [0,0,0,0,0]
    data['ends'] = [1,1,1,1,1]
    print(c)
    # print(s)
    #======================================================================

    print('\n')
    print('Or-tool is running...')
    print('\n')

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'],data['starts'],data['ends'])
    # manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]
    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    timeW = 'Time'
    routing.AddDimension(
        transit_callback_index,
        wait_time * 60,  # allow waiting time
        maximum_time_per_vehicle,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        timeW)
    time_dimension = routing.GetDimensionOrDie(timeW)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        vehicle_maximum_travel_distance,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(1000)

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

    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                data['time_windows'][0][1])

    # Instantiate route start and end times to produce feasible times.
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))

    # Define Transportation Requests.
    # for request in data['pickups_deliveries']:
    #     pickup_index = manager.NodeToIndex(request[0])
    #     delivery_index = manager.NodeToIndex(request[1])
    #     routing.AddPickupAndDelivery(pickup_index, delivery_index)
    #     routing.solver().Add(
    #         routing.VehicleVar(pickup_index) == routing.VehicleVar(
    #             delivery_index))
    #     routing.solver().Add(
    #         time_dimension.CumulVar(pickup_index) <=
    #         time_dimension.CumulVar(delivery_index))

    # for request in data['pickups_deliveries']:
    #     pickup_index = manager.NodeToIndex(request[0])
    #     delivery_index = manager.NodeToIndex(request[1])
    #     routing.AddPickupAndDelivery (pickup_index, delivery_index)
    #     routing.solver().Add(routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
    #     routing.solver().Add(distance_dimension.CumulVar(pickup_index) <= distance_dimension.CumulVar(delivery_index))

    #==============================================================
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = 30
    assignment = routing.SolveWithParameters(search_parameters)
    #==============================================================


    #======================================================================
    # print(assignment)
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logging.basicConfig(filename="or-tool.log", level=logging.INFO)
    timeRunningOr = 'Time running OR-tools: ' + str("%s seconds" % round((time.time() - start_or_time),2))
    print(timeRunningOr)
    print('\n')       
    solverStatus = routing.status()
    solverStatus = solver_stt(solverStatus)
    print("Solver status:", solverStatus)
    print('\n')       
    if assignment:
        logging.info((str(dt_string) + '//Type input: ' + v + ' ,Order: ' + str(num_orders) + ', Vehicles: ' + str(num_vehicles) + ',' + str(timeRunningOr)))
        # logging.info(str(data['pickups_deliveries']))
        logging.info(str(data['demands']))
        logging.info(str(solverStatus))
        print_solution(data, manager, routing, assignment)
        print('\n')       
    else:
        timeRunningOr = 'OR-tools: ' + solverStatus
        logging.info((str(dt_string) + '//Type input: ' + v + ' ,Order: ' + str(num_orders) + ', Vehicles: ' + str(num_vehicles) + ',' + str(timeRunningOr)))
        logging.info(str(solverStatus))
    #======================================================================

    # return result
def main():
    # thoi gian bat dau chay
    start_time = time.time()

    # tao orders
    order = creatematrixPoint(num_orders,depot,limitBor)

    # lay ma tran
    matrixApi = get_infoMatrix(order,start_time)

    # lay matran khoang cach
    matrixDistance = matrixApi['distances']

    # lay matran thoi gian
    matrixTime = matrixApi['durations']
    # print(matrixTime)

    # lay timeWindows
    timeWindows = matrixApi['time_windows']
    # print(timeWindows)

    type_input = matrixApi['type_input']

    # Tao pickup_delivery
    pickupDelivery = pickup_delivery(num_orders)

    # chay Or-tool
    runOrTools(matrixDistance,pickupDelivery,num_vehicles,max_travel_distance,num_orders,matrixTime,vehicle_capacities,timeWindows,type_input)


    # try:
    #     with time_limit(10):
    #         runOrTools(matrixDistance,pickupDelivery,num_vehicles,max_travel_distance,num_orders,matrixTime,vehicle_capacities)
    # except TimeoutException as e:
    #     print("Timed out!")

main()

# for x in range(1000):
    # main()


