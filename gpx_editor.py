from xml.dom.minidom import parse, parseString
import pandas as pd
import geopy.distance
import numpy as np


# functions to calculate the (estimate of) speed as a function of slope s
def v_pos(s, k=0.2, v_norm=40):
    return v_norm/(1+k*s)
def v_neg(s, l=15, v_norm=40):
    return v_norm + l*np.sqrt(-s)


def add_speed(name, v_kmh, begin_date, folder_from="", folder_to=""):
    FORMAT = "%Y-%m-%dT%H:%M:%SZ"   # the format for the date
    FILE_NAME = name

    # one second
    delta = pd.Timedelta(10**9)
    # the speed at which the ride is done
    v_norm = v_kmh/3.6
    
    # extract the xml data from the gpx and all trackpoints
    xml = parse(folder_from + FILE_NAME+".gpx")
    trackpoints = xml.getElementsByTagName("trkpt")

    # add the start time to the first point
    node = trackpoints[0]              # get the first trackpoint
    newEle = xml.createElement("time") # create a new element to hold the time
    newText= xml.createTextNode(begin_date.strftime(FORMAT))      # create node with the date
    newEle.appendChild(newText);       # add this node to the new element
    node.appendChild(newEle)           # add the time element to the trackpoint

    time = begin_date
    height = float(node.childNodes[1].childNodes[0].nodeValue)

    for i in range(1, len(trackpoints)):
        node = trackpoints[i]              # get the first trackpoint
        newEle = xml.createElement("time") # create a new element to hold the time

        # calculate the distance between this point and the previous
        point0 = trackpoints[i-1]
        point1 = trackpoints[i]
        # extract coordinates
        coord0 = (float(point0.getAttributeNode("lat").nodeValue), float(point0.getAttributeNode("lon").nodeValue))
        coord1 = (float(point1.getAttributeNode("lat").nodeValue), float(point1.getAttributeNode("lon").nodeValue))
        height0 = float(point0.childNodes[1].childNodes[0].nodeValue)
        height1 = float(point1.childNodes[1].childNodes[0].nodeValue)
        # get the distance in meter
        dist = geopy.distance.geodesic(coord0, coord1).m
        delta_h = height1-height0
        slope = 100*delta_h/dist    # calculate slope in % (multiply by 100)

        # calculate the time between this point and the previous and the time at this point
        speed = v_norm
        if delta_h <= 0:
            speed = v_neg(slope, v_norm=v_norm)
        else:
            speed = v_pos(slope, v_norm=v_norm)

        seconds = dist/speed
        time += seconds*delta

        newText= xml.createTextNode(time.strftime(FORMAT))      # create node with the date
        newEle.appendChild(newText);       # add this node to the new element
        node.appendChild(newEle)           # add the time element to the trackpoint


    with open(folder_to + FILE_NAME+"-with-time.gpx", "w") as file:
        print(xml.toprettyxml(), file=file)