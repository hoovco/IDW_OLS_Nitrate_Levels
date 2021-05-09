# IDW_OLS_Nitrate_Levels
This is an application written in Python with GDAL dependence to process raster and point data into a model of nitrate levels and cancer rates at the census tract level in Wisconsin.

This can be modified using your own point data as well as shapefiles. It uses GDAL grid as an interpolation method, and then uses rasterstats to derive zonal statistics. Finally it uses ordinary least squares regression to discuss residual errors in prediciton. 
