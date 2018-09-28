#!/usr/bin/env python3

import urllib.request
import http.cookiejar
import io
import gzip
import json
import numpy as np
import random

def get_opener():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('Accept', 'application/json'),
                         ('Content-Type', 'application/json'),
                         ('X-ESA-API-Key', 'ROBOT')]
    return opener

def sport_list_fetch_data(url_opener):
    print("Fetching sport list")
    f = url_opener.open('https://www.veikkaus.fi/api/v1/sport-games/draws?game-names=SPORT')
    f_info = f.info()
    f_data = f.read()
    if ('Content-Encoding', 'gzip') in f_info.items():
        # response is gzipped
        bi = io.BytesIO(f_data)
        gf = gzip.GzipFile(fileobj=bi, mode='rb')
        f_data = gf.read()
    return f_data

def popularity_fetch_data(url_opener, id):
    print("\nFetching popularity data")
    f = url_opener.open('https://www.veikkaus.fi/api/v1/sport-games/draws/SPORT/' + id + '/popularity')
    f_info = f.info()
    f_data = f.read()
    if ('Content-Encoding', 'gzip') in f_info.items():
        # response is gzipped
        bi = io.BytesIO(f_data)
        gf = gzip.GzipFile(fileobj=bi, mode='rb')
        f_data = gf.read()
    return f_data

def sport_list_fetch():
    opener = get_opener()
    sport_list = sport_list_fetch_data(opener) # bytes object
    sport_list = sport_list.decode() # from bytes to UTF-8 JSON string (python 3 default)
    sl_json = json.loads(sport_list)
    id = 0
    for x in sl_json['draws']:
        if (x['name'] == "Vakio"):
            id = x['id']
            print("Found id: " + id)
            break
    return id

def popularity_fetch(id):
    opener = get_opener()
    game_list = popularity_fetch_data(opener, id) # bytes object
    game_list = game_list.decode() # from bytes to UTF-8 JSON string (python 3 default)
    gl_json = json.loads(game_list)
    popularities = np.empty((13,3))
    for x in gl_json['resultPopularityDTOs']:
        index = int(x['eventId'])
        if (x['home']):
            popularities[index][0] = x['percentage']
        if (x['tie']):
            popularities[index][1] = x['percentage']
        if (x['away']):
            popularities[index][2] = x['percentage']
    print("  HOME  DRAW  AWAY")
    print(popularities)
    return popularities

def calculate_popular(popularities):
    popular = ""
    for x in range (13):
        if (x == 3 or x == 6 or x == 9):
            popular += ' '
        if ((popularities[x][0] > popularities[x][1]) and (popularities[x][0] > popularities[x][2])):
            popular += '1'
        elif ((popularities[x][2] > popularities[x][1]) and (popularities[x][2] > popularities[x][0])):
            popular += '2'
        else:
            popular += 'X'
    return popular

def create_result(popularities):
    result = ""
    random.seed()
    for x in range (13):
        if (x == 3 or x == 6 or x == 9):
            result += ' '
        value = random.randint(1,10000)
        #print(value)
        if (value < popularities[x][0]):
            result += '1'
        elif (value > (popularities[x][0] + popularities[x][1])):
            result += '2'
        else:
            result += 'X'
    return result

def calculate_result(results):
    result = ""
    print("\n1 X 2")
    print("-----")
    for x in range (16):
        if (x == 3 or x == 7 or x == 11):
            result += ' '
            print("")
        else:
            home = 0
            draw = 0
            away = 0
            for y in range (10):
                if (results[y][x] == '1'):
                    home += 1
                if (results[y][x] == 'X'):
                    draw += 1
                if (results[y][x] == '2'):
                    away += 1
            print (str(home) + " " + str(draw) + " " + str(away))
            if (home >= draw and home >= away):
                result += '1'
            elif (draw >= home and draw >= away):
                result += 'X'
            elif (away >= draw and away >= home):
                result += '2'
    return result

def main():
    results = []
    id = sport_list_fetch()
    popularities = popularity_fetch(id)
    print("\nGenerating weighted random results")
    for x in range (10):
        results.append(create_result(popularities))
        print(results[x])
    result = calculate_result(results)
    print("\nThe most popular result is: " + calculate_popular(popularities))
    print("  The calculated result is: " + result)

if __name__ == '__main__':
    main()