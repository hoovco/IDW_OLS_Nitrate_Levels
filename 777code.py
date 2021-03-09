#Project 1
#Geography 777
#Corey K. S. Hoover

#importing modules
import json
import csv
import ast
import geopandas as gpd
import descartes
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from osgeo import gdal
from osgeo import ogr
from osgeo import gdalconst
from osgeo import osr
import pprint
from pprint import pprint
import math
import sys
import tkinter
from tkinter import *
import rasterio
from rasterio.plot import show
#https://github.com/perrygeo/python-rasterstats
import rasterstats
from rasterstats import zonal_stats
import types

#running this to fix basestring issues from python 2.7 to 3.xx

try:
   unicode = unicode
except NameError:
   # 'unicode' is undefined, must be Python 3
   str = str
   unicode = str
   bytes = bytes
   basestring = (str,bytes)
else:
   # 'unicode' exists, must be Python 2
   str = str
   unicode = unicode
   bytes = str
   basestring = basestring

#gtg

print ('modules imported')
gdal.AllRegister()
print ('All drivers registered')

#load files
wellsShapefile = 'C:\\777Project1\g777_project1_shapefiles\well_nitrate.shp'
censusShapefile = 'C:\\777Project1\g777_project1_shapefiles\cancer_tracts.shp'
countyShapefile = 'C:\\777Project1\g777_project1_shapefiles\cancer_county.shp'
outputDirectory = 'C:\\777Project1\output'
testFile = '\\test.tiff'
warpRaster = '\\test_warp.tiff'
outputTest = outputDirectory + testFile
rasterWarpOut = outputDirectory + warpRaster
print(testFile)
print(outputDirectory)
print(outputTest)



wellNitrate = str(wellsShapefile)
print(wellNitrate)

#creating interpolation for well nitrate data

power_option = input("enter a k value > 0: ")
smoothing_option = input("enter smoothing variable >= 0")
algorithm_option = 'invdist:power='+power_option+':smoothing='+smoothing_option
print(algorithm_option)

gridOptions = gdal.GridOptions(format='Gtiff', algorithm=algorithm_option, zfield="nitr_ran") 
out = gdal.Grid(outputTest, wellNitrate, options=gridOptions)
print('interpolation complete')
print('reprojecting raster')
print('input file:', outputTest)
print('output file:', rasterWarpOut)

out = None
del out

warpOptions = gdal.WarpOptions(srcSRS='EPSG:4269', dstSRS='EPSG:4269')
print('warp options input')
warp_out = gdal.Warp(rasterWarpOut, outputTest, options=warpOptions)

print('raster reprojected')
print('changing resolution')

#wrapping up loose ends

warp_out = None
del warp_out

#getting stats through rasterstats ---- need to have everything on same EPSG. Pulling file data.

print(outputTest)
print(rasterWarpOut)


# ---------- projection getters ----------

inputTiff = gdal.OpenShared(outputTest, gdal.GA_Update)
inputTiff2 = gdal.OpenShared(rasterWarpOut, gdal.GA_Update)

infoGeoTrans = inputTiff.GetGeoTransform()
infoProj = inputTiff.GetProjection()
infoGeoTrans2 = inputTiff2.GetGeoTransform()
infoProj2 = inputTiff2.GetProjection()

#in order to make cell size small enough to register, divide x and y resoultion by 6
xres_var = infoGeoTrans2[1]
yres_var = infoGeoTrans2[5]
warpOptions = gdal.WarpOptions(xRes= xres_var/6.0, yRes=yres_var/6.0)
warp_out = gdal.Warp(rasterWarpOut, outputTest, options=warpOptions)

infoGeoTrans3 = inputTiff2.GetGeoTransform()

#wrapping up loose ends

warp_out = None
del warp_out


print('---------- Getting Transformation for Raster ----------')
print(infoGeoTrans)
print('---------- Getting Projection for Raster ----------')
print(infoProj)

inputTiff = None

print('---------- Getting Transformation for Warped Raster ----------')
print(infoGeoTrans2)
print('---------- Getting Projection for Warped Raster ----------')
print(infoProj2)

inputTiff2 = None

print('---------- getting resolution changes hopefully -----------')
print(infoGeoTrans3)

print('---------- Raster Closed ----------')

#print(censusShapefile)

driver = ogr.GetDriverByName('ESRI Shapefile')
inputSHP = driver.Open(censusShapefile)
layer = inputSHP.GetLayer()

print('---------- Shapefile Geospatial Reference ----------')
infoSpatialRef = layer.GetSpatialRef()
#infoProj = inputSHP.GetProjection()

print(infoSpatialRef)
#print(infoProj)

inputSHP = None
print('---------- Shapefile Closed ----------')

#------------ testing plotting and whatnot here ----------------
#opening raster ceated by grid and census shapefile and overlaying them.

shapefile = gpd.read_file(r'C:\777Project1\g777_project1_shapefiles\cancer_tracts.shp')
raster = rasterio.open(r'C:\777Project1\output\test.tiff') #reading raster
#shapefile.plot(linewidth=.5, facecolor='none', edgecolor='red') #options for shapefile
#plt.show() #showing the shapefile
#show(raster) #showing the raster file

#this shows both datasets, but upside down and backwards. going to check transform. probably negatives in the wrong spots.

#issue here: the output TIFF from gdal.Grid() is in EPSG 4965 and the Shapefile is in EPSG 4269. <------------ IMPORTANT
#this could be why zonal stats is throwing an error. need to transform one to match the other.

# ---------- Raster Stats function ----------

#no attribute geotransform ---> fixed using https://github.com/perrygeo/python-rasterstats/issues/173 ----> solved
#getting error here ... need to fix raster geotransform I think 2/17/2021 1728 PE ----> solved
# https://github.com/perrygeo/python-rasterstats/issues/205 ---> "must be greater than 0" issue ----> solved

#stats = zonal_stats(shapefile, 'C:\\777Project1\output\\test_warp.tiff')
#pprint(stats)

#GeoJSON option 1:
stats = zonal_stats(shapefile, 'C:\\777Project1\output\\test_warp.tiff', nodata=0.0, geojson_out=True)
#print(stats)
#print(stats["canrate"])
print(stats[0])
print('---------- literal passed ----------')

#GeoJSON option 2:

#can make this so it just prints the id, cancer rate, as well as stats. Convert to CV, then run regression as the tables are already joined.
#pprint(stats)
#stats type is a list
#print(stats[10]['properties']) # ----> this prints an array of record 10
#print(stats[1])
#for properties in stats['properties']:
#    for GEOID in properties[0]['properties']:
#        print (GEOID)
#stats_dictionary = json.loads(str(stats))
#for properties in stats['properties'].items():
#    print(properties[

#---------- this successfully iterates through each record --------
#for i in range(len(stats)):
#    #print("GEOID:",stats[i]["properties"]["GEOID10"], "Cancer Rate:",stats[i]["properties"]["canrate"], "Mean:",stats[i]["properties"]["mean"])
#    #defining these variables
#    GEOID = stats[i]["properties"]["GEOID10"]
#    canRate = stats[i]["properties"]["canrate"]
#    mean = stats[i]["properties"]["mean"]
#    properties = stats[i]["properties"]

#---------- pass to a csv? ----------
# code idea from patrick bayliss

print('---------- Writing CSV ----------')

#keys = stats[0]['properties'].keys()
with open('C:\\777Project1\output\output.txt', 'w+') as output_file: #encoding='utf8'
    #dict_writer = csv.DictWriter(output_file, keys, fieldnames=headerList)
    #dict_writer = csv.DictWriter(output_file, keys)
    dict_writer = csv.DictWriter(output_file, ["GEOID10", "mean", "canrate"], quoting=csv.QUOTE_NONNUMERIC)
    dict_writer.writeheader()
    for row in stats:
    #    dict_writer.writerow(dict((k, v.encode('utf-8')) if isinstance(v, basestring) else (k,v) for k, v in row['properties'].items()))
    #    dict_writer.writerow(dict((k, v) if isinstance(v, basestring) else (k,v) for k, v in row['properties'].items()))
         outDict={}
         outDict["canrate"] = row['properties']['canrate']
         outDict["mean"] = row['properties']['mean']
         outDict["GEOID10"] = str(row['properties']["GEOID10"])
         dict_writer.writerow(outDict)         
         output_file=None
# issues using basestring here - fix is up top below imports



print('---------- csv successfully written ----------')

print('changing column names')
with open('C:\\777Project1\output\output.txt') as outcsv:
   csv_reader = csv.DictReader(outcsv) 
   dict_from_csv = dict(list(csv_reader)[0]) 
  
    # making a list from the keys of the dict 
   list_of_column_names = list(dict_from_csv.keys()) 

   print("List of column names : ",  
          list_of_column_names)
   outcsv=None

#lets hard code a least squares regression cause I'm a loooooserrrr


df = pd.read_csv('C:\\777Project1\output\output.txt')
x = df['canrate']
y = df['mean']
xy = x*y
xsquare = x*x

#Sigma Values
sigmax = x.sum(axis=0)
sigmay = y.sum(axis=0)
sigmaxy = xy.sum(axis=0)
sigmaxsquare = xsquare.sum(axis=0)

#N value

N = df.shape[0]
TrueN = N-1 #returns the count of points counting for the headers

#calculate slope of regression line m

slope = ((TrueN*sigmaxy)-(sigmax*sigmay))/((TrueN*sigmaxsquare)-(sigmax*sigmax))

#calculate intercept b

intercept = (sigmay-(slope*sigmax))/TrueN

print( '---------- TEST MATH ----------')

print('The equation of our line is: y = ',slope,'x +',intercept)

print('Y value predicitons')

def y_Prediction():
   return((slope)*(x))+(intercept)

y_out = y_Prediction()
print(y_out)

print('error residuals')

def errorPrediction():
   return (y_out)-(y)
error = errorPrediction()
print(error)

print ('---------- END OF TEST MATH -----------')

#adding the column value with header to the CSV

df['residual']=error
df.to_csv('C:\\777Project1\output\output.txt', index=False)


### assign header columns 
##headerList = ['CensusID', 'cancerrate', 'metricmin', 'metricmax', 'metricmean', 'metriccount'] 
##  
### open CSV file and assign header 
##with open('C:\\777Project1\output\output.csv', 'w') as file: 
##    dw = csv.DictWriter(file, delimiter=',',  
##                        fieldnames=headerList) 
##    dw.writeheader() 
##  
### display csv file 
##fileContent = pd.read_csv('C:\\777Project1\output\output.csv') 
##print(fileContent) 


#need to iterate over this to print this list ----> CSV


# ---------- Spatial Regression ----------

#linear regression - can hardcode this or use scikit-learn

#establishing variables

#OLS regression
#data from zonal stats written to CSV.
#need to join zonal stats output
#need to run regression
#need to plot and represent regression with legend

data = pd.read_csv('C:\\777Project1\output\output.txt',sep=",")

#Then finished with base analysis

# ---------- Plotting to maps ----------#

#merge dataset and shapefile

#def plotMean():

map_shp = gpd.read_file('C:\\777Project1\g777_project1_shapefiles\cancer_tracts.shp')
map_shp['GEOID10'] = map_shp['GEOID10'].astype(str)
dataset = pd.read_csv('C:\\777Project1\output\output.txt',sep=",")
dataset['GEOID10'] = dataset['GEOID10'].astype(str)
dataset["mean"] = dataset["mean"].astype('float')
dataset["residual"] = dataset["residual"].astype('float')
merged = map_shp.merge(dataset, how='inner',on="GEOID10")
#merged = map_shp.merge(dataset, on='GEOID10')
merged.drop('geometry',axis=1).to_csv('C:\\777Project1\output\output.txt')
#merged = merged[['GEOID10', 'canrate', 'mean']]
#max and min should be coded here for this
variable = "residual"
vmin, vmax = -3.5, 3.5
#plot for cancer

# create figure and axes for Matplotlib
fig, ax = plt.subplots(1, figsize=(30, 10))
# remove the axis
ax.axis('off')
sm = plt.cm.ScalarMappable(cmap='gnuplot2', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm.set_array([])
fig.colorbar(sm)
##
merged.plot(column=variable, cmap='gnuplot2', linewidth=0.8, ax=ax, edgecolor='0.8')
plt.show()
###once again maxmin here
##
print(merged)
nulls = merged.isnull().sum(axis = 0)
print(nulls)

# ---------- start of new map function ----------




#plot for linear regression

# ---------- GUI Interface ----------

#need to create spaces to print results to
#need to take input for power value
#need to create dialogue to save output as

#creating GUI interface
#window = Tk()
#window.title("Cancer and Nitrate Spatial Analysis")
#plot_button1 = Button(master = window, command = plotMean, height = 2, width = 10, text = "Plot Mean Values")
#plot_button2 = Button(master = window, command = plotCancer, height = 2, width = 10, text = "Plot Cancer Rate Values")
#plot_button3 = Button(master = window, command = plotOLS, height = 2, width = 10, text = "Plot OLS Error Values")
#window.geometry('800x600')
#plot_button.pack()
#window.mainloop()


