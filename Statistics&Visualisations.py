# **Statistics and Visualization**

"""
Between 2020 and 2023, a total of 2740 fires were recorded across the UK (Figure 1). The average **Fire Radiative Power** was 18.6 MW. The FRP values ranged from a minimum of 2.3 MW to a maximum of 592.7 MW. Notably, 75% of the fires had a FRP below 17.9 MW, indicating the predominance of lower-intensity fires in the dataset with a few exceptionally high FRP values (Figure 2).

Fires occurred in 26 of the 36 **land cover** types present in the UK (Figure 3). The land cover category with the highest number of fire occurrences was 'Industrial or commercial units' while the categories with the fewest fires were 'Construction sites', 'Port areas', 'Fruit trees and berry plantations', 'Salt marshes' and 'Complex cultivation patterns'. Land covers with no fire occurrences were excluded from the study.

The average **elevation** of fire locations was 125.8m, with most fires occurring below 200m. The **annual average temperature** at fire locations was 10.1°C, with little variation across the UK. As expected, southern regions showed higher annual average temperatures than the north. **Annual total precipitation** averaged 1178mm, with higher rainfall observed along the western coastline. **Annual average wind speed** showed little variation across the UK and averaged at 23 km/h (Figure 4).
"""

Figure1()

"""**Figure 1.** Map of the 2740 fire data points that occured between 2020 and 2023."""

#Describe the fire intensity (Fire Radiative Power)
df_project['frp'].describe()

#Plot fires based on fire intensity (frp)
fig, ax = plt.subplots(figsize=(10, 8))

#Set minimum and maximum values of frp for the color scale
#75% of the values are under 17.9 thus we choose 40 as a maximum
vmin = 2
vmax = 40

#Dot color depends on fire intensity
UKshp.plot(ax=ax , color='lightgray')
scatter = ax.scatter(df_project.geometry.x, df_project.geometry.y,
                     c=df_project['frp'], cmap='hot_r', s=50, edgecolor='k', alpha=0.7,
                     vmin=vmin, vmax=vmax)


# Add color bar to represent intensity
plt.colorbar(scatter, label='Fire Radiative Power (MW)')

#Labels and title
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Fire Locations with Intensity')

#Show plot
plt.show()

"""**Figure 2.** Spatial distribution of Fire Radiative Power (MW), the response variable, for fires that occured between 2020 and 2023."""

df_project['Land cover'].value_counts()

Figure3()

"""**Figure 3.** Map of the 36 different land covers present in the UK in 2018."""

#Describe Elevation
df_project['elevation'].describe()

#Describe Annual Average Temperature
df_project['annual_avg_temp'].describe()

#Describe Annual Total Precipitation
df_project['annual_total_precip'].describe()

#Describe Annual Average Wind Speed
df_project['annual_avg_wind_speed'].describe()

#Plot with 4 subplots, showing distribution of the 4 explanatory variables

#Create 2x2 grid of subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 12))

#Plot 1: Elevation
UKshp.plot(ax=axs[0, 0], color='lightgray')
scatter = axs[0, 0].scatter(df_project.geometry.x, df_project.geometry.y,
                            c=df_project['elevation'], cmap='terrain', s=50, edgecolor='k', alpha=0.7)

axs[0, 0].set_xlabel('Longitude')
axs[0, 0].set_ylabel('Latitude')
axs[0, 0].set_title('A) Elevation (m)')
plt.colorbar(scatter, ax=axs[0, 0], label='Elevation (m)')

#Plot 2: Annual Average Temperature
UKshp.plot(ax=axs[0, 1], color='lightgray')
scatter = axs[0, 1].scatter(df_project.geometry.x, df_project.geometry.y,
                             c=df_project['annual_avg_temp'], cmap='hot_r', s=50, edgecolor='k', alpha=0.7)
axs[0, 1].set_xlabel('Longitude')
axs[0, 1].set_ylabel('Latitude')
axs[0, 1].set_title('B) Annual Average Temperature (°C)')
plt.colorbar(scatter, ax=axs[0, 1], label='Annual Average Temperature (°C)')

#Plot 3: Annual Total Precipitation
UKshp.plot(ax=axs[1, 0], color='lightgray')
scatter = axs[1, 0].scatter(df_project.geometry.x, df_project.geometry.y,
                            c=df_project['annual_total_precip'], cmap='winter_r', s=50, edgecolor='k', alpha=0.7)
axs[1, 0].set_xlabel('Longitude')
axs[1, 0].set_ylabel('Latitude')
axs[1, 0].set_title('C) Annual Total Precipitation (mm)')
plt.colorbar(scatter, ax=axs[1, 0], label='Annual Total Precipitation (mm)')

#Plot 4: Annual Average Wind Speed
UKshp.plot(ax=axs[1, 1], color='lightgray')
scatter = axs[1, 1].scatter(df_project.geometry.x, df_project.geometry.y,
                            c=df_project['annual_avg_wind_speed'], cmap='spring', s=50, edgecolor='k', alpha=0.7)
axs[1, 1].set_xlabel('Longitude')
axs[1, 1].set_ylabel('Latitude')
axs[1, 1].set_title('D) Annual Average Wind Speed (km/h)')
plt.colorbar(scatter, ax=axs[1, 1], label='Annual Average Wind Speed (km/h)')

#Adjust layout and show
plt.tight_layout()
plt.show()

"""**Figure 4.** Spatial distribution of the explanatory variables between 2020 and 2023. A) Elevation B) Annual average temperature C) Annual total precipitation D) Annual average wind speed."""
