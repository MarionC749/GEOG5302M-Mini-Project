#Submitted as part of coursework for GEOG5302M: Data Science for Practical Applications
# **Data Collection**

## **Set-up Packages**
"""

pip install folium matplotlib mapclassify palettable descartes pysal contextily matplotlib_scalebar geopandas

!pip install openmeteo-requests
!pip install requests-cache retry-requests numpy pandas

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import geopandas as gpd
import palettable as pltt
from pysal.viz import mapclassify
import numpy as np
import statsmodels.api as sm
import scipy.stats as stats
from matplotlib_scalebar.scalebar import ScaleBar
import mapclassify
import matplotlib.patches as mpatches
import requests
import datetime
import json
import openmeteo_requests
import requests_cache
from retry_requests import retry
import math
from shapely import wkt
from scipy.stats import gaussian_kde
from pysal.explore import esda
from splot.esda import moran_scatterplot, lisa_cluster, plot_local_autocorrelation
from pysal.lib import weights
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW

"""## **Set-up fire data**"""

#Load UK shape file
UKshp = gpd.read_file('LAD_MAY_2024_UK_BFE.shp')
UKshp.info()

#Plot UK map
UKshp.plot()

#Load fire locations data
df_fire = pd.read_csv('fire_archive_M-C61_555109.csv')
df_fire.head()

df_fire.info()

#Create the GeoDataFrame using coordinates of df_fire
fire_loc = gpd.GeoDataFrame(df_fire, geometry=gpd.points_from_xy(df_fire['longitude'], df_fire['latitude']))

#Set the CRS to WGS84 (EPSG:4326), since the coordinates are in lat/lon and this is the standard for GPS coordinates
fire_loc.set_crs('EPSG:4326', inplace=True)

#Reproject to EPSG:27700 (British National Grid) to align with UK map
fire_loc = fire_loc.to_crs('EPSG:27700')

#Check the fire locations and UK boundary maps have the same CRS
print(UKshp.crs)  #Check the CRS of the UK shapefile
print(fire_loc.crs)  #Check the CRS of the fire locations

#Look at the top of the new dataset
fire_loc.head()

#Plot the fire locations data (it should look somewhat like the shape of the UK)
fire_loc.plot()

#Check fire data points align with UK map
#Plot both UK map and fire locations at the same time
def Figure1():
  fig, ax = plt.subplots(1,1, figsize=(10,10), ) #set the figure size
  UKshp.plot(ax = ax, facecolor = 'lightgray') #plot UK map
  fire_loc.plot(ax = ax, color = 'red') #plot fires
  ax.set_axis_off() #remove axes
  fig.suptitle('UK fires') #add a title
  plt.show()

Figure1()

"""## **Set-up land cover data**"""

#Load land cover data
df_land = gpd.read_file('U2018_CLC2018_V2020_20u1.gpkg')
df_land.head()

#Plot the land cover data without differentiating the types (should have map of the UK)
df_land.plot()

#Check dataset info
df_land.info()

#The land cover column named Code_18 should be an integer, as it is the code associated with the land cover type
df_land['Code_18'] = df_land['Code_18'].astype(int)

#Check CRS of data
print(df_land.crs)

#Change land cover data to EPSG:27700 (British National Grid) to align with UK map
df_land = df_land.to_crs('EPSG:27700')
print(df_land.crs)

"""In this land cover dataset, the column Code_18 corresponds to a land cover type code. The dataset containing the land cover legends, corresponding to each code, needs to be loaded and merged with the land cover dataset."""

#Load the legend dataset
#One of the land cover types contains a comma, causing an issue when loading data set, thus it has to be ignored
df_legend = pd.read_csv('CLC_legend.csv', on_bad_lines='skip')
#and the delimiter has to be redefined
df_legend = pd.read_csv('CLC_legend.csv', delimiter=';')
df_legend.head()

#Check dataset info
df_land.info()

#Merge the land cover dataset with its legend using the code columns
df_land_m = df_land.merge(df_legend, how='left', left_on='Code_18', right_on='CLC_CODE')
df_land_m.head()

"""To use the RGB column and be able to map land covers with their corresponding colors, the format of the RGB column needs to be converted."""

#Create function to convert the 'RGB' (object in format '230-000-077') to hexadecimal color codes '#RRGGBB'
def rgb_to_hex(rgb_string):
    try:
        #Split the string using '-' delimiter and convert to integers
        r, g, b = map(int, rgb_string.split('-'))
        #Convert the integers to hexadecimal format and return it
        return f'#{r:02x}{g:02x}{b:02x}'
    except ValueError:
        #If an error in conversion occurs, return a default gray color
        return '#808080'

#Apply the conversion function to the 'RGB' column
df_land_m['RGB_color'] = df_land_m['RGB'].apply(rgb_to_hex)

#Check dataset
df_land_m.head()

"""The function mapping land covers across the UK will be called in a later section."""

#Plot the land covers with colors based in the RGB_color column
def Figure3():
  fig, ax = plt.subplots(figsize=(10, 10))
  df_land_m.plot(ax=ax, color= df_land_m['RGB_color'])
  ax.set_title('Land Cover Types with RGB Colors', fontsize=16) #Add a title

#Create legend based on the land cover type 'LABEL3' column
#Get the unique land cover types
  unique_types = df_land_m['LABEL3'].unique()

#Create list of patch objects for the legend
  handles = []
  for land_type in unique_types:
    #Get corresponding color for each land cover type
    color = df_land_m[df_land_m['LABEL3'] == land_type]['RGB_color'].iloc[0]
    #Create patch for each land type and its color
    handles.append(mpatches.Patch(color=color, label=land_type))

#Add the legend
  ax.legend(handles=handles, title="Land Cover Type", loc='upper left', bbox_to_anchor=(1.05, 1))

  plt.show()

"""Next, the dataset is cleaned, and the fire locations and corresponding land covers are spatially joined."""

#Clean fire location dataset to keep only columns used for analysis and plotting
fire_loc = fire_loc[['latitude', 'longitude', 'acq_date','frp', 'geometry' ]]
#Clean land cover dataset to keep only columns used for analysis and plotting
df_land_m = df_land_m[['LABEL3','RGB_color','geometry']]

#Spatially join the fire dataset with the land cover dataset, to know in which land cover the fire points fall into
#predicate='within' allows to checks if a point (from fire_loc) is within a polygon (from df_land_m)
df_fires = gpd.sjoin(fire_loc, df_land_m, how='left', predicate='within')

#Check
df_fires.head()

#The acq_date column is in format YYYY-MM-DD, which cannot be used to extract the year
#Convert acq_date to datetime format
df_fires['acq_date'] = pd.to_datetime(df_fires['acq_date'])

#Add a year column based on date column, which will allow to calculate and add annual meteorological data later on
df_fires['Year'] = df_fires['acq_date'].dt.year

#Check the updated dataframe
df_fires.head()

#Check we have 4 years
df_fires['Year'].unique()

#Save new dataset
df_fires.to_csv('df_fires.csv', index=False)

"""## **Elevation data retrieval using Open-Elevation API**"""

#Create function to get elevation data from list of locations (with lat and long)
#Code inspired by the Open Elevation API GitHub documentation

def get_elevation(latitudes, longitudes):
    url = "https://api.open-elevation.com/api/v1/lookup"
    locations = [{"latitude": lat, "longitude": lon} for lat, lon in zip(latitudes, longitudes)] #Create list of coordinates by pairing lat and long (zip function)

    #Send request
    response = requests.post(
        url=url,
        headers={ "Accept": "application/json", "Content-Type": "application/json; charset=utf-8",},
        data=json.dumps({"locations": locations}) )

    #If status code is 200 (i.e. the request was successful), we add the elevation to the results
    if response.status_code == 200:
        result = response.json()
        elevations = [location['elevation'] for location in result['results']]
        return elevations
    else:
        print(f"Error getting elevation data: {response.status_code}") #Print error message if status code is not 200
        return [None] * len(latitudes)

#Create lists out of latitudes and longitudes
latitudes = df_fires['latitude'].tolist()
longitudes = df_fires['longitude'].tolist()

#Get elevations for each fire data point (with pair of latitude and longitude) and add to new column
df_fires['elevation'] = get_elevation(latitudes, longitudes)

#Check dataframe
#Elevation in meters (m)
df_fires.head()

#Save new dataset
df_fires_elevation = df_fires.copy()
df_fires_elevation.to_csv('df_fires_elevation.csv', index=False)

"""## **Weather data retrieval using Open-Meteo API**"""

#Check info
df_fires_elevation.info()

"""The dataset is too big (2741 rows) to access weather API, which has hourly call limits. Thus, the dataset is divided into 28 subets (27 sets of 100 rows and 1 set of 41 rows)."""

#Divide the dataset into subsets of 100 rows
subs = [df_fires_elevation.iloc[i:i+100] for i in range(0, len(df_fires_elevation), 100)]

#Save each subset into separate CSV files
for idx, subs in enumerate(subs):
    subs.to_csv(f'subset_{idx+1}.csv', index=False)

#Load subsets
subset_1 = pd.read_csv('subset_1.csv')
subset_2 = pd.read_csv('subset_2.csv')
subset_3 = pd.read_csv('subset_3.csv')
subset_4 = pd.read_csv('subset_4.csv')
subset_5 = pd.read_csv('subset_5.csv')
subset_6 = pd.read_csv('subset_6.csv')
subset_7 = pd.read_csv('subset_7.csv')
subset_8 = pd.read_csv('subset_8.csv')
subset_9 = pd.read_csv('subset_9.csv')
subset_10 = pd.read_csv('subset_10.csv')
subset_11 = pd.read_csv('subset_11.csv')
subset_12 = pd.read_csv('subset_12.csv')
subset_13 = pd.read_csv('subset_13.csv')
subset_14 = pd.read_csv('subset_14.csv')
subset_15 = pd.read_csv('subset_15.csv')
subset_16 = pd.read_csv('subset_16.csv')
subset_17 = pd.read_csv('subset_17.csv')
subset_18 = pd.read_csv('subset_18.csv')
subset_19 = pd.read_csv('subset_19.csv')
subset_20 = pd.read_csv('subset_20.csv')
subset_21 = pd.read_csv('subset_21.csv')
subset_22 = pd.read_csv('subset_22.csv')
subset_23 = pd.read_csv('subset_23.csv')
subset_24 = pd.read_csv('subset_24.csv')
subset_25 = pd.read_csv('subset_25.csv')
subset_26 = pd.read_csv('subset_26.csv')
subset_27 = pd.read_csv('subset_27.csv')
subset_28 = pd.read_csv('subset_28.csv')

"""A function to collect meteorological data for each fire data point is created, based on its location and year of occurence. The function first collects daily data for the whole year of occurence, then annual averages/totals are calculated."""

#Code inspired by code provided by Open-Meteo API website

#Set up Open-Meteo API with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

#Define url
url = "https://archive-api.open-meteo.com/v1/archive"

#Define parameters we want to collect:
# - daily mean temperature (2m above ground)
# - daily total precipitation in mm
# - daily maximum wind speed (10m above ground)
# - timezone is UK, GMT 0
params = { "daily": ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"],
           "timezone": "GMT"}

#Create function to fetch weather data for each location and year
def fetch_weather_data(lat, lon, year):

    #Set start and end dates based on the year
    start_date = f"{year}-01-01" #1st of Jan
    end_date = f"{year}-12-31" #31st of Dec

    params["latitude"] = lat
    params["longitude"] = lon
    params["start_date"] = start_date
    params["end_date"] = end_date

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        #Extract daily data from API
        daily = response.Daily()
        daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(1).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(2).ValuesAsNumpy()

        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ),
            "temperature_2m_mean": daily_temperature_2m_mean,
            "precipitation_sum": daily_precipitation_sum,
            "wind_speed_10m_max": daily_wind_speed_10m_max
        }

        daily_dataframe = pd.DataFrame(data=daily_data)

        #Calculate annual means/total
        annual_avg_temp = daily_dataframe["temperature_2m_mean"].mean()
        annual_total_precip = daily_dataframe["precipitation_sum"].sum()
        annual_avg_wind_speed = daily_dataframe["wind_speed_10m_max"].mean()

        return {
            "latitude": lat,
            "longitude": lon,
            "year": year,
            "annual_avg_temp": annual_avg_temp,
            "annual_total_precip": annual_total_precip,
            "annual_avg_wind_speed": annual_avg_wind_speed
        }
    except Exception as e:
        print(f"Error fetching data for {lat}, {lon}, year {year}: {e}")
        return None

"""A function is created to use the previous function on each row of a dataset."""

#Create function to process each subset and fetch its weather data using previous function
def fetch_weather_subset(df, fetch_weather_data):

    #Create list to store results for each row/location
    weather_results = []

    #Iterate through each row in the subset
    for index, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        year = row['Year']

        #Fetch weather data using previous function
        result = fetch_weather_data(lat, lon, year)

        #Add result to the list if it is valid
        if result:
            weather_results.append(result)

    #Convert the results into a new subset
    df_weather = pd.DataFrame(weather_results)

    return df_weather

"""The Open-Meteo API has a time limit of 500 calls per minute. Thus, during the data collection process, the function was called for each of the 28 subsets individually. For the purpose of this report, only the meteorological data of the 1st subset will be retrieved as an example, to prove the code works. The other 27 subsets were run over several days."""

#Call function with the 1st subset and collect its meteorological data
df_weather_subset_1 = fetch_weather_subset(subset_1, fetch_weather_data)
df_weather_subset_1.head()

#df_weather_subset_2 = fetch_weather_subset(subset_2, fetch_weather_data)
#df_weather_subset_3 = fetch_weather_subset(subset_3, fetch_weather_data)
#df_weather_subset_4 = fetch_weather_subset(subset_4, fetch_weather_data)
#df_weather_subset_5 = fetch_weather_subset(subset_5, fetch_weather_data)
#df_weather_subset_6 = fetch_weather_subset(subset_6, fetch_weather_data)
#df_weather_subset_7 = fetch_weather_subset(subset_7, fetch_weather_data)
#df_weather_subset_8 = fetch_weather_subset(subset_8, fetch_weather_data)
#df_weather_subset_9 = fetch_weather_subset(subset_9, fetch_weather_data)
#df_weather_subset_10 = fetch_weather_subset(subset_10, fetch_weather_data)
#df_weather_subset_11 = fetch_weather_subset(subset_11, fetch_weather_data)
#df_weather_subset_12 = fetch_weather_subset(subset_12, fetch_weather_data)
#df_weather_subset_13 = fetch_weather_subset(subset_13, fetch_weather_data)
#df_weather_subset_14 = fetch_weather_subset(subset_14, fetch_weather_data)
#df_weather_subset_15 = fetch_weather_subset(subset_15, fetch_weather_data)
#df_weather_subset_16 = fetch_weather_subset(subset_16, fetch_weather_data)
#df_weather_subset_17 = fetch_weather_subset(subset_17, fetch_weather_data)
#df_weather_subset_18 = fetch_weather_subset(subset_18, fetch_weather_data)
#df_weather_subset_19 = fetch_weather_subset(subset_19, fetch_weather_data)
#df_weather_subset_20 = fetch_weather_subset(subset_20, fetch_weather_data)
#df_weather_subset_21 = fetch_weather_subset(subset_21, fetch_weather_data)
#df_weather_subset_22 = fetch_weather_subset(subset_22, fetch_weather_data)
#df_weather_subset_23 = fetch_weather_subset(subset_23, fetch_weather_data)
#df_weather_subset_24 = fetch_weather_subset(subset_24, fetch_weather_data)
#df_weather_subset_25 = fetch_weather_subset(subset_25, fetch_weather_data)
#df_weather_subset_26 = fetch_weather_subset(subset_26, fetch_weather_data)
#df_weather_subset_27 = fetch_weather_subset(subset_27, fetch_weather_data)
#df_weather_subset_28 = fetch_weather_subset(subset_28, fetch_weather_data)

"""Once meteorological data was collected for all 28 subsets, the subsets were added to a list and combined back into a single dataset."""

#Once the weather data was retrieved, all 28 subsets were added into a list
#subsets = [df_weather_subset_1, df_weather_subset_2, df_weather_subset_3, df_weather_subset_4, df_weather_subset_5,
           #df_weather_subset_6, df_weather_subset_7, df_weather_subset_8, df_weather_subset_9, df_weather_subset_10,
           #df_weather_subset_11, df_weather_subset_12, df_weather_subset_13, df_weather_subset_14, df_weather_subset_15,
           #df_weather_subset_16, df_weather_subset_17, df_weather_subset_18, df_weather_subset_19, df_weather_subset_20,
           #df_weather_subset_21, df_weather_subset_22, df_weather_subset_23, df_weather_subset_24, df_weather_subset_25,
           #df_weather_subset_26, df_weather_subset_27, df_weather_subset_28]

#And combined into one dataset
# df_combined = pd.concat(subsets, axis=0, ignore_index=True)

#Check, should now have 2741 rows
# df_combined.info()

#Rename year column
# df_combined.rename(columns={'year': 'Year'}, inplace=True)

#Save new dataset
# df_combined.to_csv('df_combined.csv', index=False)
