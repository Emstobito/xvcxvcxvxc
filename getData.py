import csv
import json 
import codecs

def getCsvData(num_orders):
    inputData = []
    with open('input.csv','rt')as f:
        data = csv.reader(f)
        for row in data:
            inputData.append(row)
    lenInputData = len(inputData)
    lngIndex = inputData[0].index("longitude")
    latIndex = inputData[0].index("latitude")
    strGetApi = ''
    for x in range(1,num_orders):
        strGetApi = strGetApi + ';' +inputData[x][lngIndex] + ',' + inputData[x][latIndex]
    return strGetApi

def getJsonData():
    inputJson = json.load(codecs.open('input.json', 'r', 'utf-8-sig')) 
    # print(inputJson['center'])
    # print(inputJson['vehicles'])

