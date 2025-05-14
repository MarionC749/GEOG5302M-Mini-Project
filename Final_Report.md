Submitted as part of coursework for GEOG5302M: Data Science for Practical Applications
# **Data Science Mini Project**

## Investigating Environmental Drivers of Wildfire Intensity in the UK: Spatial Patterns and Influencing Factors

# **Introduction**

In recent years, large wildfires have been occurring in many regions of the world, notably California, the Amazon, Australia and southern Europe. While these areas have always been vulnerable to wildfires, the effects of climate change are amplifying fire risks worldwide, making unlikely regions, such as the UK, more susceptible to these events (Arnell *et al*., 2021).

Wildfires have long-term environmental effects, by disrupting biodiversity, altering landscape quality and triggering soil erosion (Santi and Rengers, 2022). They pose socioeconomic, public health and security issues, due for instance to the destruction of buildings and the release of carbon contributing to air quality deterioration (Wang *et al*., 2018; Knorr *et al*., 2017). While the UK has seen fewer severe wildfires compared to fire-prone regions, recent incidents have demonstrated the growing fire risks in the UK (Belcher *et al*., 2021). For example, the Swinley Forest fire in 2011 damaged 110 hectares of habitat, threatened nearby residential areas and required significant resources from the fire rescue services (Brown *et al*., 2016). Additionally, cases of fires in British peat lands, which are important carbon stores, have raised concerns of positive feedback to climate change (Davies *et al*., 2016; Milne and Brown, 1997).

Understanding fire dynamics, its spatial patterns and driving factors is essential to fire prevention and the development of effective fire management strategies (Elia *et al*., 2018; Curt *et al*., 2016). Most UK wildfires are caused by inadvertent or deliberate human action (Glaves *et al*., 2020), but the conditions necessary for a fire to become established are environmentally determined. Previous studies have found that fire occurrence, duration, spread and intensity are linked to meteorological conditions (solar radiation, air temperature, precipitation, relative humidity and wind speed), as these influence the drying and wetting of vegetation, which is crucial for flammability (Freeborn *et al.*, 2016). Fires are associated with severe drought conditions, characterized by low levels of precipitation and high temperatures. Global warming intensifies these favourable fire weather conditions, increasing fuel availability, and makes them more frequent, thereby lengthening fire seasons (Smith *et al*., 2020). Anthropogenic activities, such as land cover changes, have also been shown to influence fire behaviour by altering vegetation composition, which in turn affects fuel loads, structure and dryness (Hantson *et al*., 2015).

Though contributing factors and spatial distributions of wildfires have been explored in fire-prone regions like the Amazon and Mexico (Ma *et al*., 2022; Román-Cuesta and Martínez-Vilalta, 2006), fewer studies have examined the UK as it is an “emergent risk” there (Perry *et al*., 2022). Since the relationships between drivers and fire occurrence and behaviour can vary by region (Parisien and Moritz, 2009), it is crucial to explore the unique drivers in the UK to inform local fire mitigation strategies.

This study aims to investigate the environmental factors influencing fire intensity across the UK. We address the following specific objectives: (1) report the spatial distribution of fire occurrences and intensity, (2) examine the relationship between fire intensity and meteorological, topographic as well as land cover factors with an OLS, (3) detect any spatial variation in these relationships, using a geographically weighted regression.

# **Data**

In this study, the data was compiled from different sources. Fire data points were collected from the NASA Fire Information for Resource Management System (FIRMS) website, covering fires that occurred in the UK between the 1st of January 2020 and the 31st of December 2023. The data was collected by the Moderate Resolution Imaging Spectroradiometer (MODIS) with a 1km spatial resolution, aboard the Aqua and Terra satellites. This allowed to collect 2740 fire data points with their coordinates, date of occurrence and Fire Radiative Power (FRP in MW). Each fire data point represents the centre of a 1km pixel containing one or more fires, with the location coordinates corresponding to the pixel’s centre. FRP is a measure of the radiant energy emitted by a fire within a pixel. It is related to biomass combustion and is used as a proxy for fire intensity (Li *et al*., 2018). To map the fires across the UK, geospatial data of the local authority district boundaries in the UK (as of May 2024) were downloaded from the Office for National Statistics. UK geospatial land cover dataset from 2018 with a 100m resolution was sourced from the UK Centre for Ecology & Hydrology, to determine the land cover type at each fire location. The elevation at each fire location was obtained based on its coordinates using the public API from the Open Elevation website. Similarly, weather data was retrieved from the Open Meteo website using a public API. The daily average temperature, total precipitation and average wind speed were extracted, and annual averages and totals were calculated based on the fire location and the year of occurrence.

| Variable                 | Unit           | Description                                                                 | Source               |
|--------------------------|----------------|-----------------------------------------------------------------------------|----------------------|
| latitude                 | Degrees °      | Latitude of centre of 1km fire pixel. Not necessarily the actual location of fire as one or more fires can be detected within the 1km pixel. | NASA FIRMS           |
| longitude                | Degrees °      | Longitude of centre of 1km fire pixel. Not necessarily the actual location of fire as one or more fires can be detected within the 1km pixel. | NASA FIRMS           |
| acq_date                 |                | Date of MODIS acquisition.                                                   | NASA FIRMS           |
| Year                     |                | Year fire occurred based on acq_date.                                        | NASA FIRMS           |
| frp                      | Megawatts (MW) | Fire Radiative Power. The rate of radiative energy emission per time unit from all fires within a pixel. | NASA FIRMS           |
| geometry                 |                | Point geographic location, represented by a pair of coordinates made from the latitude and longitude columns. |                      |
| Land cover               |                | Land cover type in the fire location, in 2018.                               | UKCEH                |
| RGB_color                |                | RGB color code to map land covers.                                          | UKCEH                |
| elevation                | Meters (m)     | Elevation of fire location.                                                  | Open-Elevation API   |
| annual_avg_temp          | Celsius °C     | Annual average temperature in fire location, 2 meters above ground.         | Open-Meteo API       |
| annual_total_precip      | mm             | Sum of annual precipitation (including rain, showers, and snowfall) in fire location. | Open-Meteo API       |
| annual_avg_wind_speed    | Km/h           | Annual average of maximum wind speed and gusts on a day, 10 meters above ground, in fire location. | Open-Meteo API       |
| ID                       |                | ID of individual fires.                                                     |                      |

**Table 1.** Sources and description of variables in the final dataset (df_project).

The response variable of this study is FRP. The 31 explanatory variables of the study include three categories: topography (elevation), meteorology (temperature, precipitation, wind speed) and land cover (27 types) (Table 1). Topography has been shown to influence fire distribution, as the probability of fire occurrence decreases in high elevations (Wood *et al*., 2011). Weather conditions are important determinants of fire intensity by affecting the availability and flammability of fuels, i.e. vegetation. Temperature affects the combustibility of vegetation, as high temperatures increase the likelihood of ignition. Precipitation influences the moisture level of vegetation, with high precipitation reducing flammability (Fares *et al*., 2017; Živanović *et al*., 2020; Westerling, 2008). Wind affects fuel moisture and is linked to fire behaviour by providing additional oxygen to flames and accelerating combustion by pushing fire towards new fuel sources, encouraging its propagation (Beer, 1991). Meteorological data was summarized annually to capture overall climate conditions that influence fire intensity, as vegetation content and amount depend on preceding weather conditions (Perry *et al*., 2022). Additionally, land cover is a predictor of fire intensity as it determines fuel availability depending on the vegetation type (Pereira *et al*., 2014). These explanatory variables have been commonly used before to study fire occurrence, distribution, spread and intensity (Ma *et al*., 2022; Salavati *et al*. 2022; Freeborn *et al*., 2016).

![Unknown1](https://github.com/user-attachments/assets/165bda19-13c0-47dd-abbd-f67645451e2a)

**Figure 1.** Map of the 2740 fire data points that occured between 2020 and 2023.

# **Statistics and Visualization**

Between 2020 and 2023, a total of 2740 fires were recorded across the UK (Figure 1). The average **Fire Radiative Power** was 18.6 MW. The FRP values ranged from a minimum of 2.3 MW to a maximum of 592.7 MW. Notably, 75% of the fires had a FRP below 17.9 MW, indicating the predominance of lower-intensity fires in the dataset with a few exceptionally high FRP values (Figure 2).

Fires occurred in 26 of the 36 **land cover** types present in the UK (Figure 3). The land cover category with the highest number of fire occurrences was 'Industrial or commercial units' while the categories with the fewest fires were 'Construction sites', 'Port areas', 'Fruit trees and berry plantations', 'Salt marshes' and 'Complex cultivation patterns'. Land covers with no fire occurrences were excluded from the study.

The average **elevation** of fire locations was 125.8m, with most fires occurring below 200m. The **annual average temperature** at fire locations was 10.1°C, with little variation across the UK. As expected, southern regions showed higher annual average temperatures than the north. **Annual total precipitation** averaged 1178mm, with higher rainfall observed along the western coastline. **Annual average wind speed** showed little variation across the UK and averaged at 23 km/h (Figure 4).

![Unknown-2](https://github.com/user-attachments/assets/1e5f1087-fe29-4a45-a111-d9fd1f877b59)

**Figure 2.** Spatial distribution of Fire Radiative Power (MW), the response variable, for fires that occured between 2020 and 2023.

![Unknown-3](https://github.com/user-attachments/assets/8348929d-7006-4212-af62-f9608e459502)

**Figure 3.** Map of the 36 different land covers present in the UK in 2018.

![Unknown-4](https://github.com/user-attachments/assets/f7cff7ae-7fc8-41d7-af7d-0e49c331a0b5)

**Figure 4.** Spatial distribution of the explanatory variables between 2020 and 2023. A) Elevation B) Annual average temperature C) Annual total precipitation D) Annual average wind speed.




# **Results**

## **Kernel Density Estimation Analyses**

The Kernel Density Estimation (KDE) of fire counts showed densities are very low, indicating there were few fire events in the UK between 2020 and 2023 and that these were geographically dispersed. However, two regions can be identified as higher fire occurence density clusters: the Bannau Brycheiniog National Park near Cardiff and the Lincolnshire region (Figure 5).

![Unknown-5](https://github.com/user-attachments/assets/934e74c2-f656-46dd-b1d4-90f807ba8a2f)

**Figure 5.** Kernel density map of fire counts in the UK between 2020 and 2023.

Similarly, fire intensity densities were also low, indicating that concentrated areas of high fire intensity are rare and that the distribution of fire intensity is spread out. Two regions can be identified as fire intensity clusters on the KDE map: the Bannau Brycheiniog National Park near Cardiff and the Lincolnshire region (Figure 6).

![Unknown-6](https://github.com/user-attachments/assets/11831b2d-5c77-4027-805a-8a2e2b980ff2)

**Figure 6.** Kernel density map of Fire Radiative Power (MW) of fires occuring in the UK between 2020 and 2023.

## **OLS Analysis**

To examine the global relationships between fire intensity (FRP) and environmental variables, an OLS regression was first performed. The model only explained 5.5% of the variation in FRP, suggesting the chosen explanatory variables do not sufficiently account for variation in FRP.

The year of occurrence was significantly positively associated with FRP (OLS, coef= 1.3093, t= 2.237, p= 0.025), indicating that fire intensity increased over time. Elevation had no significant effect on fire intensity (OLS, coef= -0.0015, t= -0.170, p= 0.865).

The total annual precipitation in the year of the fire showed a significant negative relationship with FRP (OLS, coef= -0.0042, t= -3.018, p= 0.003), implying that lower rainfall is linked to higher fire intensity. The two other meteorological variables, annual average temperature (OLS, coef= 1.6955, t= 1.757, p= 0.079) and annual average wind speed (OLS, coef= 0.0401, t= 0.114, p= 0.909), had no significant effect on fire intensity.

Seven land cover types were significantly related to FRP at the 0.05 level. The land cover type ‘Industrial or commercial units’ had a strong negative relationship with FRP (OLS, coef= -2648.6225, t= -2.239, p= 0.025), suggesting fires occurring in this land cover tend to have lower intensity. On the other hand, ‘Coniferous forest’ (OLS, coef= 32.8222, t= 7.833, p< 0.01), ‘Mixed forest’ (OLS, coef= 12.4741, t= 2.223, p= 0.026), ‘Moors and heathland’ (OLS, coef= 18.1766, t= 6.068, p<0.01), ‘Natural grassland’ (OLS, coef= 22.5498, t= 6.610, p<0.01), ‘Peat bogs’ (OLS, coef= 28.2036, t= 8.891, p<0.01), and ‘Transitional woodland-shrub’ (OLS, coef= 20.7834, t= 3.493, p<0.01), were all land cover types positively associated with FRP. This indicates that fires occurring in these land types have a higher FRP.

## **Moran's I Analysis**

The Moran's I value was 0.095 and was statistically significant (p<0.01), indicating a positive spatial autocorrelation of FRP. The positive Moran’s I value suggests areas with high FRP fires tended to be surrounded by areas with high FRP fires, and similarly, areas with low FRP fires tended to be surrounded by areas with low FRP fires. However, a Moran's I value of 0.095 indicated a very weak spatial clustering, as it is not close to 1.

The LISA cluster map (Figure 7) shows a weak positive spatial autocorrelation of fire intensity with a majority of clusters being non-significant. In the south of England, large areas of Low-Low clusters are observed, i.e. fires with low FRP are surrounded by low FRP fires. In contrast, Northern Ireland and Northern Scotland mainly show High-High clusters, i.e. areas with high FRP fires are in proximity of high FRP fires.

![Unknown-7](https://github.com/user-attachments/assets/fcdef8a1-b03a-4125-9f42-1fe9608790c6)

**Figure 7.** Lisa cluster map of the FRP of fires.
The different cluster types are as follows:
*	HH : High-high (red): high values surrounded by high values
*	HL : High-low (orange): high values surrounded by low values
*	LH : Low-high (light blue): low values surrounded by high values
*	LL : Low-low (dark blue): low values surrounded by low values
*	ns : non-significant (grey) spatial autocorrelation

## **Geographical Weighted Regression (GWR) Analysis**

As Moran’s I analysis suggested a slight spatial autocorrelation in fire radiative power (FRP), a Geographic Weighted Regression was conducted. Unlike the global regression model, which assumes uniform relationships between independent and explanatory variables across the entire study area, the GWR model allows the relationship coefficients to vary spatially, allowing to detect local trends.

The GWR model had a higher adjusted R-squared (0.067) compared to the global regression model (0.055), and a lower residual sum of squares, indicating it was better at explaining variation in FRP and provided a more appropriate fit by accounting for local variations in the data. However, the model still only explained 6.7% of the variation in fire intensity, suggesting again that the chosen explanatory variables may not be the most appropriate to capture variation in FRP.

The relationship between Year and FRP was slightly stronger in the North of Scotland, where FRP increased faster over time compared to other regions, but generally showed a consistent positive relationship across the UK (OLS coef= 1.309, GWR mean coef= 0.703) (Figure 8).

![Unknown-8](https://github.com/user-attachments/assets/012b30af-1d80-4311-9755-79d959bd7330)

**Figure 8.** Spatial distribution of the GWR model coefficients, presenting the relationship between Year and FRP.

## **Meteorological effects**

The effect of total annual precipitation on FRP remained consistently negative across space, as indicated by the GWR mean coefficient of -0.004, which closely matched the global coefficient. The negative relationship was very slightly more pronounced in the south of the UK (England and Wales) where lower rainfall contributed to slightly higher fire intensity than in the north (Northern Ireland and Scotland) (Figure 9).

Annual average temperature and wind speed were statistically non-significant in the OLS and showed low coefficient standard deviations in the GWR, confirming they have little to no influence on FRP, even if there seemed to be some spatial patterns (Figure 9).

![Unknown-9](https://github.com/user-attachments/assets/8e94374d-a77b-4fea-958b-dd05b20184b7)

**Figure 9.** Spatial distribution of the GWR model coefficients, presenting the relationship between meteorological variables and FRP.

## **Land cover effects**

The negative relationship between the ‘Industrial or commercial units’ and FRP was highly variable across space. The GWR analysis showed a broad range of coefficients, from -5338.731 to -644.625. The negative relationship was particularly strong in the north of Scotland, compared to the more moderate negative effects in the south of the UK (Figure 10).

For ‘Coniferous forest’ (OLS coef= 32.822, GWR mean coef= 28.278) and ‘Transitional woodland-shrub’ (OLS coef= 20.783, GWR mean coef= 16.461) land covers, the relationship with FRP was positive and consistent across the UK. However, the strength of the relationship was slightly weaker on the west coast of the UK and Northern Ireland (Figure 10).

The ‘Moors and heathland’ (OLS coef= 18.177, GWR mean coef= 17.102) and the ‘Natural grasslands’ (OLS coef= 22.550, GWR mean coef= 21.005) land covers also exhibited consistent positive relationships with FRP across the UK. FRP was slightly stronger in the south of the UK but generally remained similar across the study area (Figure 10).

On the contrary, the relationship between the ‘Mixed forest’ (OLS coef= 12.474, GWR mean coef= 17.102) land cover changed spatially, as FRP was stronger on the west coast of the UK and Northern Ireland (Figure 10).

The land covers that were statistically non-significant in the OLS displayed low coefficient standard deviations in the GWR, confirming that any potential spatial variation in their effects on FRP is minimal.

![Unknown-10](https://github.com/user-attachments/assets/ad97e42e-e907-431f-8661-ec749536d6db)

**Figure 10.** Spatial distribution of the GWR model coefficients of the significant land covers and FRP. A) Industrial or commercial units, B) Coniferous forest, C) Mixed forest, D) Moors and heathland, E) Natural grasslands, F) Transitional woodland-shrub.

# **Discussion**

Overall, fires in the UK were generally of low intensity, with rare occurrences of high-intensity fires. This is consistent with reports indicating that 99% of fires in England are small, covering under 1 hectare and half under 5𝑚2 (Forestry Commission, 2023). The UK’s temperate climate, which is not typically associated with wildfires, may explain this trend (McMorrow 2011). Fire intensity exhibited weak positive spatial autocorrelation, indicating a largely random distribution across the UK. Low FRP fire clusters were observed in England, whereas high fire clusters were seen in Northern Ireland and northern Scotland. These patterns may reflect higher urban density and better fire management resources in England, compared to more vegetated, rural and isolated areas in the north (Pateman, 2011).

Over the four years, fire intensity increased, especially in Scotland, possibly due to the growing impact of climate change on conditions favourable to fire intensity (Arnell *et al*., 2021). However, this study could be expanded by including more years for a long-term analysis and time series evaluation. This analysis was limited to four years due to restrictions on the number of API calls within a given timeframe.

As expected, lower total annual precipitation was associated with increased fire intensity, as reduced moisture in fuels promotes higher fire intensities (Freeborn *et al*., 2016). This was particularly evident in the south of the UK. While wet years allow fuel to build up, the UK’s typically high moisture levels mean that fire intensity only rises when precipitation is low enough to dry out the fuels (McMorrow 2011). Annual average temperature and wind speed did not appear to affect fire intensity, contrary to previous studies’ findings (Ma *et al*., 2022; Liu *et al*., 2010; Perry *et al*., 2021). Elevation was also found to have no effect on fire intensity, contrary to findings by Ma *et al*. (2022) and Monjarás-Vega *et al*. (2020). This could be explained by the UK’s unique climate, causing the drivers of fire intensity to differ, or by the limited four-year dataset, which may not have captured enough variation in meteorological and topographic conditions.

Land cover types impacted fire intensity, which is consistent with previous studies (Cano-Crespo *et al*., 2022). The ‘Industrial or commercial units’ areas were associated with low-intensity fires, likely due to the limited vegetation and fuel availability of this urban land cover type. This relationship was stronger in the north than in the south of the UK.

Coniferous forest, mixed forest, moors and heathland, natural grassland, peat bogs and transitional woodland-shrub were all land covers linked to higher fire intensity. Thus, as anticipated, land covers with more vegetation tend to burn more intensely than those with less vegetation, such as urban or agricultural areas, which were not associated with fire intensity (Yang *et al*., 2023; Avila-Flores *et al*., 2010). Some slight north-south and west-east variations in the positive relationships between these six land covers and fire intensity were observed. These could be due to climatic gradients or regional differences in firefighting management (Moreira *et al*., 2009).

This study has several limitations that require further investigation. The fire data collected did not distinguish between wildfires, industrial incidents or fires prescribed for land management purposes, which could have affected the analysis. A more suitable statistical analysis should also be conducted, as the assumptions of the OLS were violated, even after transformations, making the results inaccurate. For instance, the data could have been analyzed on a grid rather than a point basis, to perform a geographically weighted Poisson regression. The explanatory variables selected in this analysis accounted for little variation in fire intensity. Thus, future work should explore relationships with other environmental factors such as forest fragmentation, above-ground vegetation carbon density, tree cover, or anthropogenic factors such as population density, road density, and proximity to roads (Ma *et al*., 2022; Monjarás-Vega *et al*., 2020). Human-related factors may play an important role in fire intensity, as UK fires are generally ignited by human action and rarely by natural causes (Glaves *et al*., 2020). Other aspects of fire behaviour, such as fire counts, size, and duration, could also be investigated alongside fire intensity for a more comprehensive understanding.

# **Conclusion**

This study found that fires in the UK generally exhibit low intensity, with rare-high intensity events. Fire intensity was weakly spatially autocorrelated, with lower-intensity fire clusters in England and higher-intensity clusters in northern regions. Lower precipitation was linked to higher fire intensity, while elevation, temperature and wind speed had no impact. Land cover played a significant role in fire intensity, with vegetated areas showing higher intensity and industrial areas lower intensity. Despite these insights, the study’s limitations, short timeframe, lack of fire type differentiation and choice of statistical methods, highlight the need for further investigation. Future research should explore additional environmental and anthropogenic variables and examine other aspects of fire behaviour.
"""
