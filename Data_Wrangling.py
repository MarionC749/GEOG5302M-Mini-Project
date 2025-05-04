# **Data Wrangling**
"""
We now have the df_combined dataset (containing the meteorogical data) and the df_fires_elevation data (containing the fire and elevation data). The 2 datasets are merged.
"""

#Load the combined dataset
df_combined = pd.read_csv('df_combined.csv')
df_combined.info()

"""As expected all columns contain 2741 rows."""

#Load df_fires_elevation
df_fires_elevation = pd.read_csv('df_fires_elevation.csv')
df_fires_elevation.info()

"""The two datasets are merged together based on fire coordinates and year."""

#Merge the df_combined with the df_fires_elevation dataset, using the coordinates and the year
df_project = pd.merge(df_fires_elevation, df_combined, on=['latitude', 'longitude','Year'], how='inner')
#Check, should have 2741 rows
df_project.info()

"""There are more rows than expected, as there should be 2741. We need to check for NAs."""

#Check for NAs
df_project.isna().sum()

"""One row has NAs as it wasn't assigned a land cover type. We choose to remove it."""

df_project = df_project.dropna()
df_project.info()

"""There are still 6 more rows than expected, we check for duplicates as the merge function may have created some, and delete them."""

#Check for duplicates and show them
duplicated_rows = df_project[df_project.duplicated()]
print(duplicated_rows)

#Drop the duplicated rows
df_project = df_project.drop_duplicates()
df_project.info()

"""We now have 2740 rows, as expected."""

#Drop the index_right column which isn't necessary
df_project = df_project.drop('index_right', axis=1)

#Rename column
df_project.rename(columns={'LABEL3': 'Land cover'}, inplace=True)

#Add an identifier column
df_project['ID'] = df_project.index

#Check top of dataset
df_project.head()

#Save the final complete dataset
df_project.to_csv('df_project.csv', index=False)

#Load final dataset
df_project = pd.read_csv('df_project.csv')

"""Make sure the geometry column is of class 'geometry'."""

#Convert 'geometry' column from WKT string to shape geometries
df_project['geometry'] = df_project['geometry'].apply(wkt.loads)
df_project['geometry'].info()

#Convert the DataFrame to a GeoDataFrame
df_project = gpd.GeoDataFrame(df_project, geometry='geometry')
df_project.info()

#Make sure dataset CRS is on UK grid
df_project.set_crs('EPSG:27700', inplace=True)
print(df_project.crs)

"""We now have the final df_project dataset which will be used for analysis."""
