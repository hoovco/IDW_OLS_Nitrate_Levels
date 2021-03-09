import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import matplotlib
import matplotlib.pyplot as plt
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
import math
import sys
import rasterio
from rasterio.plot import show
import rasterstats
from rasterstats import zonal_stats
import types

gdal.AllRegister()


#functions ----------


def loadFiles():
    wellsShapefile = 'C:\\777Project1\g777_project1_shapefiles\well_nitrate.shp'
    censusShapefile = 'C:\\777Project1\g777_project1_shapefiles\cancer_tracts.shp'
    countyShapefile = 'C:\\777Project1\g777_project1_shapefiles\cancer_county.shp'
    outputDirectory = 'C:\\777Project1\output'
    testFile = '\\test.tiff'
    warpRaster = '\\test_warp.tiff'
    global outputTest
    outputTest = outputDirectory + testFile
    global rasterWarpOut
    rasterWarpOut = outputDirectory + warpRaster
    global wellNitrate
    wellNitrate = str(wellsShapefile)

def getVariables():
    #convert string to float
    power_option = float(var1.get())
    smoothing_option = float(var2.get())
    #may put this in the main function on click
    return(power_option)
    return(smoothing_option)
    print(power_option)
    print(smoothing_option)

def cancerClick():
    print('cancer button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputCanrate.png"))
    canvas1.create_image(30, 30, anchor=CENTER, image=img)


def residualClick():
    print('residual button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputResidual.png"))
    canvas1.create_image(30, 30, anchor=CENTER, image=img)
    

def meanClick():
    print('mean button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputMean.png"))
    canvas1.create_image(30, 30, anchor=CENTER, image=img)
    

def interpolate():
    print(power_option)
    print(smoothing_option)
    #power_option = str(power_option)
    #smoothing_option = str(smoothing_option)
    algorithm_option = 'invdist:power='+str(power_option)+':smoothing='+str(smoothing_option)
    gridOptions = gdal.GridOptions(format='Gtiff', algorithm=algorithm_option, zfield="nitr_ran")
    out = gdal.Grid(outputTest, wellNitrate, options=gridOptions)
    out = None
    del out

def correctWarp():
    warpOptions = gdal.WarpOptions(srcSRS='EPSG:4269', dstSRS='EPSG:4269')
    warp_out = gdal.Warp(rasterWarpOut, outputTest, options=warpOptions)
    warp_out = None
    del warp_out

def changeResolution():
    inputTiff = gdal.OpenShared(outputTest, gdal.GA_Update)
    inputTiff2 = gdal.OpenShared(rasterWarpOut, gdal.GA_Update)
    #getting geotransform info
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
    warp_out = None
    del warp_out
    inputTiff=None
    inputTiff2=None

def zonalStats():
    shapefile = gpd.read_file(r'C:\777Project1\g777_project1_shapefiles\cancer_tracts.shp')
    raster = rasterio.open(r'C:\777Project1\output\test.tiff')
    global stats
    stats = zonal_stats(shapefile, 'C:\\777Project1\output\\test_warp.tiff', nodata=0.0, geojson_out=True)

def csvOut():
    with open('C:\\777Project1\output\output.txt', 'w+') as output_file:
        dict_writer = csv.DictWriter(output_file, ["GEOID10", "mean", "canrate"], quoting=csv.QUOTE_NONNUMERIC)
        dict_writer.writeheader()
        for row in stats:
            outDict={}
            outDict["canrate"] = row['properties']['canrate']
            outDict["mean"] = row['properties']['mean']
            outDict["GEOID10"] = str(row['properties']["GEOID10"])
            dict_writer.writerow(outDict)         
            output_file=None

def regression():
    #coding the OLS regression
    #reading in the CSV
    global df
    df = pd.read_csv('C:\\777Project1\output\output.txt')
    #variables
    x = df['canrate']
    y = df['mean']
    #establishing x*y and x^2
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
    def y_Prediction():
        return((slope)*(x))+(intercept)

    y_out = y_Prediction()
    #print(y_out)

    #print('error residuals')
    def errorPrediction():
        return (y_out)-(y)
    
    global error
    error = errorPrediction()
    #print(error)

def addResidual():
    df['residual']=error
    df.to_csv('C:\\777Project1\output\output.txt', index=False)

def joinData():
    #bringing in the shapefile to join
    map_shp = gpd.read_file('C:\\777Project1\g777_project1_shapefiles\cancer_tracts.shp')
    map_shp['GEOID10'] = map_shp['GEOID10'].astype(str)
    #bringing in the CSV to join
    dataset = pd.read_csv('C:\\777Project1\output\output.txt',sep=",")
    dataset['GEOID10'] = dataset['GEOID10'].astype(str)
    dataset["mean"] = dataset["mean"].astype('float')
    dataset["residual"] = dataset["residual"].astype('float')
    #defining the merge/ join
    global merged
    merged = map_shp.merge(dataset, how='inner',on="GEOID10")
    merged.drop('geometry',axis=1).to_csv('C:\\777Project1\output\output.txt')
    

def plotMean():
    variable = "mean"
    vmin, vmax = -1, 12
    figure = figure1, ax = plt.subplots(1, figsize=(6, 6))
    ax.set_title('Mean Zonal Values for OLS Nitrate and Cancer Regression', fontsize=8.5) #WTF WHY SO TINY
    #ax.annotate('Negative values indicate an overprediction, where positive values indicate underprediction', xy=(0.1, .08), xycoords='figure fraction',
            #horizontalalignment='right', verticalalignment='top', fontsize=12, color='#555555')
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='gnuplot2', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    figure1.colorbar(sm)
    merged.plot(column=variable, cmap='gnuplot2', linewidth=0.25, ax=ax, edgecolor='0.8')
    #fig1 = plt.fig()
    plt.savefig('C:\\777Project1\output\outputMean.png')
    #plt.show()


def plotCanrate():
    variable = "canrate_y"
    vmin, vmax = 0.0, 0.99
    figure = figure1, ax = plt.subplots(1, figsize=(6, 6))
    ax.set_title('Cancer Rates for OLS Nitrate and Cancer Regression', fontsize=9) #WTF WHY SO TINY
    #ax.annotate('Negative values indicate an overprediction, where positive values indicate underprediction', xy=(0.1, .08), xycoords='figure fraction',
            #horizontalalignment='right', verticalalignment='top', fontsize=12, color='#555555')
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='gnuplot2', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    figure1.colorbar(sm)
    merged.plot(column=variable, cmap='gnuplot2', linewidth=0.25, ax=ax, edgecolor='0.8')
    #fig1 = plt.fig()
    plt.savefig('C:\\777Project1\output\outputCanrate.png')
    #plt.show()


def plotResidual():
    variable = "residual"
    vmin, vmax = -3.5, 3.5
    figure = figure1, ax = plt.subplots(1, figsize=(6, 6))
    ax.set_title('Residual Values for OLS Nitrate and Cancer Regression', fontsize=9) #WTF WHY SO TINY
    #ax.annotate('Negative values indicate an overprediction, where positive values indicate underprediction', xy=(0.1, .08), xycoords='figure fraction',
            #horizontalalignment='right', verticalalignment='top', fontsize=12, color='#555555')
    ax.axis('off')
    sm = plt.cm.ScalarMappable(cmap='gnuplot2', norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])
    figure1.colorbar(sm)
    merged.plot(column=variable, cmap='gnuplot2', linewidth=0.25, ax=ax, edgecolor='0.8')
    #fig1 = plt.fig()
    plt.savefig('C:\\777Project1\output\outputResidual.png')
    #plt.show()

def main():
    global power_option
    power_option = float(var1.get())
    global smoothing_option
    smoothing_option = float(var2.get())
    print(power_option)
    print(smoothing_option)
    loadFiles()
    print('files loaded')
    print('variables obtained')
    interpolate()
    print('interpolation complete')
    correctWarp()
    print('warp corrected')
    changeResolution()
    print('resolution corrected')
    print('calculating zonal statistics')
    zonalStats()
    print('zonal stats complete')
    csvOut()
    print('csv created')
    regression()
    print('regression complete')
    addResidual()
    print('residual added')
    joinData()
    print('data joined')
    plotMean()
    print('mean values plotted')
    plotCanrate()
    print('cancer values plotted')
    plotResidual()
    print('residuals plotted')


#end of functions ---------

#creating GUI interface and button functionality

window = Tk()
window.title("Cancer and Nitrate Spatial Analysis")
menu = Menu(window)
new_item = Menu(menu)
new_item.add_command(label='Save As')
menu.add_cascade(label='File', menu = new_item)
window.config(menu=menu)
window.geometry('920x650')

frame1 = Frame(window, bg = 'white', borderwidth = 2)
frame1.pack()
frame1.grid(row=2, column=1)

frame2 = Frame(window, bg = 'white', borderwidth = 2)
frame2.grid(row=3, column=1)

frame3 = Frame(window, bg = 'white', borderwidth = 2)
frame3.grid(row=4, column=1)

frame4 = Frame(window, bg = 'white', borderwidth = 2)
frame4.grid(row=5, column=1)

canvas1 =Canvas(window, height='500', width='600', bg='white', borderwidth = 3, relief = 'sunken')
canvas1.create_text(50, 50, fill="black",font="Times 14 italic bold",
                        text="Instructions:", justify='left', anchor='w')
canvas1.create_text(50, 68,fill="black",font="Times 12",
                        text= "1. Enter a desired IDW k variable greater than zero", justify='left', anchor='w')
canvas1.create_text(50, 86,fill="black",font="Times 12",
                        text="2. Enter a smoothing variable equal to or greater than zero", justify='left', anchor='w')
canvas1.create_text(50, 104,fill="black",font="Times 12",
                        text="3. Click ""Run IDW and OLS""", justify='left', anchor='w')
canvas1.create_text(50, 122,fill="black",font="Times 12",
                        text="4. When the button becomes acive again, the analysis is complete", justify='left',anchor='w')
canvas1.create_text(50, 140,fill="black",font="Times 12",
                        text="5. Click the ""Plot Values"" buttons to see their respective maps", justify='left',anchor='w')
canvas1.grid(row=1, column=1)
def cancerClick():
    print('cancer button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputCanrate.png"))
    canvas1.create_image(300, 250, anchor=CENTER, image=img)


def residualClick():
    print('residual button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputResidual.png"))
    canvas1.create_image(300, 250, anchor=CENTER, image=img)
    

def meanClick():
    print('mean button clicked')
    global img
    img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\outputMean.png"))
    canvas1.create_image(300, 250, anchor=CENTER, image=img)
#img = ImageTk.PhotoImage(Image.open("C:\\777Project1\output\output.png"))
#canvas1.create_image(30, 30, anchor=CENTER, image=img)

canvas2 =Canvas(window, bg = 'white', height='175', width='300', borderwidth = 3, relief = 'raised')
canvas2.grid(row=1, column=3)
canvas2.create_text(150, 50,fill="darkblue",font="Times 12 italic bold",
                        text="Inverse Distance Weighted (IDW)")
canvas2.create_text(150, 68,fill="darkblue",font="Times 12 italic bold",
                        text= "Ordinary Least Squares")
canvas2.create_text(150, 86,fill="darkblue",font="Times 12 italic bold",
                        text="Nitrate and Cancer Relationship")
canvas2.create_text(150, 104,fill="darkblue",font="Times 10",
                        text="Higher power(k) values and lower smoothing results")
canvas2.create_text(150, 122,fill="darkblue",font="Times 10",
                        text=" in predictions confined closer to points")
canvas2.create_text(150, 140,fill="darkblue",font="Times 10",
                        text="Residuals are + or - based on margin of error")

#this is the sectiuon to define buttons and inputs as well as the functions to call

L1 = Label(frame1, text="IDW k Value > 0: ")
L1.pack(side = LEFT)
L2 = Label(frame2, text="Smoothing Variable >= 0: ")
L2.pack(side = LEFT)

var1 = tk.StringVar()
var2 = tk.StringVar()

k_var = Entry(frame1, bd =5, textvariable = var1)
k_var.pack(side = LEFT)
sm_var = Entry(frame2, bd =5, textvariable = var2)
sm_var.pack(side=LEFT)

#IDWButton = Button(frame3, text="Run IDW and OLS", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3, command=getVariables)
IDWButton = Button(frame3, text="Run IDW and OLS", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3, command=main)
IDWButton.pack(side=LEFT)

plot_button1 = Button(frame4, text = "Plot Mean Nitrate Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3, command=meanClick)
plot_button2 = Button(frame4, text = "Plot Cancer Rate Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3, command=cancerClick)
plot_button3 = Button(frame4, text = "Plot OLS Error Values", bg = 'red', fg = 'white', relief = 'raised', borderwidth = 3, command=residualClick)
plot_button1.pack(side=LEFT)
plot_button2.pack(side=LEFT)
plot_button3.pack(side=LEFT)

window.mainloop()

