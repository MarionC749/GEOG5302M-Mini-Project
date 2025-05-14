#Submitted as part of coursework for GEOG5302M: Data Science for Practical Applications
# **Data Analysis**

### **Part 1: Exploring the data.**

"""
The maximum FRP value seems very high compared to the mean and may be an outlier.
"""

#Plot frp distribution
sns.histplot(df_project['frp'], bins=30)
plt.title('Histogram of Fire Intensity (FRP)')
plt.xlabel('Fire Radiative Power (MW)')
plt.ylabel('Frequency')

#Boxplot frp to spot outliers
sns.boxplot(data=df_project, y='frp')
plt.title('Boxplot for Outlier Detection')
plt.show()

#Show the top 10 rows with the highest 'frp' values
top_10_fires = df_project.nlargest(10, 'frp')
print(top_10_fires)

"""The maximum FRP value corresponds to a major fire which occured on the 24th of July 2022 in Hankley Common, burning 50 acres. Thus, this is not an error and should not be removed for now.

Visualize fire intensity depending on the land cover, then depending on land cover with yearly comparisons.
"""

#Plot fire intensity by land cover type
plt.figure(figsize=(50, 8))
sns.boxplot(data=df_project, x='Land cover', y='frp')
plt.show()

#Plot fire intensity by land cover type for annual comparison

#Get unique years
years = df_project['Year'].unique()

#Create larger figure with vertical subplots
fig, axes = plt.subplots(len(years), 1, figsize=(30, 6 * len(years)))

#Loop through each year and create boxplot for each
for i, year in enumerate(years):
    #Filter data for the specific year
    data_year = df_project[df_project['Year'] == year]

    #Create boxplot for year on its subplot (axes[i])
    sns.boxplot(data=data_year, x='Land cover', y='frp', hue='Land cover', ax=axes[i])

    #Specify titles and labels
    axes[i].set_title(f'Box Plot of Fire Intensity in {year}')
    axes[i].set_xlabel('Land Cover')
    axes[i].set_ylabel('Fire Radiative Power (MW)')

#Adjust layout to avoid overlap
plt.tight_layout()

#Show plot
plt.show()

"""Create dummy variables out of the land cover columns. Converting these to numerical values allows to include them in OLS models in the analysis."""

#Create set of dummies
#Each column of dummy land cover type will be boolean, where True indicates that the row has that specific land type value
dummies = pd.get_dummies(df_project['Land cover'], prefix='Lc_')

#Convert boolean dummy columns to binary (0/1)
dummies = dummies.astype(int)

#Check
dummies.info()

"""Create final analysis dataset, including only numerical values used for analysis."""

#Create final final dataset, including only the numerical values used for analysis

#Drop columns not used in analysis
df_sub1 = df_project[['latitude', 'longitude', 'Year', 'frp', 'elevation', 'annual_avg_temp', 'annual_total_precip', 'annual_avg_wind_speed']]

#Insert the dummy values
df_sub2 = pd.concat([df_sub1, dummies], axis=1)
df_sub2.info()

"""### **Part 2: Investigating the density of fire locations with Kernel Density Estimation (KDE)**

Using the Kernel Density Estimation method allows to map the density of fire occurences. This enables to identify geographic regions with fire occurence clusters.
"""

#Calculate Kernel Density Estimate (KDE) for fire locations

#Get coordinates of the data points
coords = np.array([df_project.geometry.x, df_project.geometry.y])

#Perform KDE
kde = gaussian_kde(coords, bw_method=0.5)
#Create grid to evaluate KDE
#by creating array of 100 spaced points from minimum to maximum for x and y coordinates
x_grid = np.linspace(min(coords[0]), max(coords[0]), 100)
y_grid = np.linspace(min(coords[1]), max(coords[1]), 100)
#and by creating 2D grid by combining the x_grid and y_grid arrays
grid_x, grid_y = np.meshgrid(x_grid, y_grid)

#Evaluate the KDE on the grid
#np.vstack = stacks the 1D arrays together to make a 2D array
#grid_x.ravel() = flattens out the 2D array into 1D
grid_coords = np.vstack([grid_x.ravel(), grid_y.ravel()])
#Get density values
density_values = kde(grid_coords).reshape(grid_x.shape)

#Show mininmum and maximum densities
print(np.min(density_values), np.max(density_values))
#Result: densities are very low

def Figure5():
  #Create plot
  fig, ax = plt.subplots(figsize=(10, 8))
  #Plot UK map
  UKshp.plot(ax=ax, color='lightgray')
  #Plot KDE density contour map, without 0 density values
  contour = ax.contourf(grid_x, grid_y, density_values, cmap='YlOrRd', levels=10, alpha= 0.6)


  plt.colorbar(contour, label='Density')
  plt.title('Fire Density Map')
  plt.show()



"""### **Part 3: Investigating the density of fire intensity, with Kernel Density Estimation (KDE)**

Similarly, using the Kernel Density Estimation method allows to map the density of fire intensity. This enables to identify geographic regions where fire intensities are clustered, to detect spatial patterns.
"""

#Calculate Kernel Density Estimate (KDE) for fire intensity (frp)

#Get coordinates of the data points (x and y from geometry)
coords = np.array([df_project.geometry.x, df_project.geometry.y])
#Get fire intensity (frp)
fire_intensity = df_project['frp']
#Stack the 3 variables(x, y, intensity) to create a 3D array
data = np.vstack([coords[0], coords[1], fire_intensity])

#Perform KDE (3D density estimation with x, y, and fire intensity)
kde_intensity = gaussian_kde(data, bw_method=0.5)
#Create grid to evaluate KDE
x_grid = np.linspace(min(coords[0]), max(coords[0]), 100)
y_grid = np.linspace(min(coords[1]), max(coords[1]), 100)
grid_x, grid_y = np.meshgrid(x_grid, y_grid)

#Fix a fire intensity (FRP) value for the grid (use mean value)
fixed_intensity = np.mean(fire_intensity)

#Create grid coordinates (using fixed intensity value for 3rd dimension)
grid_coords = np.vstack([grid_x.ravel(), grid_y.ravel(), np.full_like(grid_x.ravel(), fixed_intensity)])

#Evaluate the KDE on the grid
density_values_intensity = kde_intensity(grid_coords).reshape(grid_x.shape)

#Show minimum and maximum densities
print(np.min(density_values_intensity), np.max(density_values_intensity))
#Result: densities are very low

def Figure6():
  #Plot spatial intensity distribution
  fig, ax = plt.subplots(figsize=(10, 8))
  #Plot UK map
  UKshp.plot(ax=ax, color='lightgray')
  #Plot KDE density contour map, without 0 density values
  contour = ax.contourf(grid_x, grid_y, density_values_intensity, cmap='YlOrRd', levels=10, alpha= 0.6)

  plt.colorbar(contour, label='Fire Radiative Power (MW) Density')
  plt.title('Fire Intensity Density Map')
  plt.show()

"""### **Part 4: Investigating the relationship between fire intensity and environmental factors, with an OLS model**

We start by investigating the correlations between variables, to detect any multicollinearity.
"""

#Correlation Heatmap
plt.figure(figsize=(20, 20))
correlation_matrix = df_sub2.corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', annot_kws={"size": 8}, fmt=".2f")
plt.title('Correlation Heatmap')
plt.show()

"""None of the correlations are above 0.9 or below -0.9, thus we consider there are no multicollinearities in the data.

Next, we create a **linear regression** to look at the relationship between fire intensity (FRP) and the other variables.

We fit the OLS model.
"""

#Look at the major land cover for fires
df_project['Land cover'].value_counts()
#Result: Industrial or commercial units have the highest number of fires (829)
#Result: Construction sites, Port areas, Fruit trees and berry plantations,
# Salt marshes and Complex cultivation patterns have the lowest number of fires (1)

#OLS Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover, will be the constant
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
ols_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
ols_residuals = ols_model.resid

#OLS regression summary
print(ols_model.summary())

"""### **Part 5: Spatial analysis of fire intensity, using Moran's I**

We calculate Moran's I value and it's significance to check for spatial autocorrelation of fire intensity (FRP), which would indicate spatial patterns.
"""

#Create new subset for spatial analysis
#Including the fire ID and geometry columns back in
#Excluding unnecessary columns
df_sub3 = pd.concat([df_project, dummies], axis=1)
df_sub3 = df_sub3.drop(columns=['latitude', 'longitude', 'acq_date', 'Land cover', 'RGB_color'])
df_sub3.info()

"""We chose to use the K-nearest neighbours method as we are dealing with point data."""

#Calculate the square root of the number of data points to know the optimized k value
math.sqrt(len(df_sub3))

#Rounding it down to the nearest integer, to get k, the number of neighbors
#Calculate K-nearest neighbours weights
w_k = weights.KNN.from_dataframe(df_sub3, ids = 'ID', k = 52)

#Calculate Moran's I value
mi = esda.Moran(df_sub3['frp'], w_k)
#print the I value to 3 decimal places
print(round(mi.I, 3))

#print the p value to know significance
print(mi.p_sim)

"""Moran's I is 0.095 and is statistically significant at the 0.01 level, suggesting the presence of a slight positive spatial autocorrelation. Thus, the analysis can be furthered with a Geographically Weighted Regression.

"""

#Create Moran's I scatterplot, to spot outliers
moran_scatterplot(mi)

#Calculate LISA clusters
lisa = esda.Moran_Local(df_sub3['frp'], w_k)

def Figure7():
  lisa_cluster(lisa, df_sub3)

"""### **Part 6: Geographically Weighted Regression of fires**"""

df_sub4 = df_sub3.copy() #Create new dataset for GWR
df_sub4['geometry'] = df_sub4.geometry.centroid #calculate the centroid
df_sub4['x'] = df_sub4.geometry.x #extract x
df_sub4['y'] = df_sub4.geometry.y #extract y

#Define independent variables
#omit Lc_Industrial or commercial units to use it as reference category as it is the most common land cover
X = df_sub4[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]

#Define dependent variable
Y = df_sub4['frp']

#Create a list of coordinates (g_coords)
g_coords = list(zip(df_sub4.x, df_sub4.y))

#Convert X to numpy array
g_X = np.asarray(X)

#Convert Y to numpy array (reshaped as column vector)
g_y = np.asarray(Y).reshape((-1, 1))

#The code to search for the optimized bandwidth indicates a 'Matrix is singular' error
#gwr_selector = Sel_BW(g_coords, g_y, g_X, fixed=True, spherical=True)
#bw = gwr_selector.search()

#Thus the ideal bandwdith was manually searched for
#2740, the total number of data points was the optimized number for bw


#Create the GWR model with bandwidth
gwr = GWR(g_coords, g_y, g_X, bw=2740)

#Fit the model
gwr_results = gwr.fit()

#View the results
print(gwr_results.summary())

"""Extract the relationships' coefficients to map them."""

#Extract local regression coefficients for Year (X1) and add it to dataset
df_sub4['GWR_coef_Year'] = gwr_results.params[:,1]
#Extract local regression coefficients for elevation (X4) and add it to dataset
df_sub4['GWR_coef_precip'] = gwr_results.params[:,4]
#Extract local regression coefficients for annual average temperature (X3) and add it to dataset
df_sub4['GWR_coef_Temperature'] = gwr_results.params[:,3]
#Extract local regression coefficients for annual average wind speed (X5) and add it to dataset
df_sub4['GWR_coef_Wind'] = gwr_results.params[:,5]



#Extract local regression coefficients for Lc_Industrial or commercial units (X0) and add it to dataset
df_sub4['X0_coef'] = gwr_results.params[:,0]
#Extract local regression coefficients for Lc__Coniferous forest (X9) and add it to dataset
df_sub4['X9_coef'] = gwr_results.params[:,9]
#Extract local regression coefficients for Lc__Mixed forest (X19) and add it to dataset
df_sub4['X19_coef'] = gwr_results.params[:,19]
#Extract local regression coefficients for Lc__Moors and heathland (X20) and add it to dataset
df_sub4['X20_coef'] = gwr_results.params[:,20]
#Extract local regression coefficients for Lc__Natural grasslands (X21) and add it to dataset
df_sub4['X21_coef'] = gwr_results.params[:,21]
#Extract local regression coefficients for Lc__Transitional woodland-shrub (X30) and add it to dataset
df_sub4['X30_coef'] = gwr_results.params[:,30]

#Check
df_sub4.head()

"""Map out the different distributions of the relationship coefficients between FRP and the explanatory variables.

Map for Year variable.
"""

def Figure8():
  #Create plot for Year coefficient
  fig, ax = plt.subplots(1)
  df_sub4.plot(ax = ax, column = 'GWR_coef_Year', cmap = 'coolwarm',legend = True)
  plt.title('Local Coefficients for Year')
  ax.set_axis_off()
  plt.show()

"""Maps of the meteorological variables."""

def Figure9():
  #Create plots of coefficients of meteorological variables
  #Create a 1x3 grid of subplots (1 rows, 3 columns)
  fig, axs = plt.subplots(1, 3, figsize=(15, 6))

  #Create list of the coefficients column and titles for the 3 plots
  coeff_columns = ['GWR_coef_precip', 'GWR_coef_Temperature', 'GWR_coef_Wind',]

  titles = [
    'A) Local Coefficients \n of Total Annual Precipitation',
    'B) Local Coefficients \n of Annual Average Temperature',
    'C) Local Coefficients \n of Annual Average Wind Speed']

  #Loop through each subplot and plot map
  for i, (col, title) in enumerate(zip(coeff_columns, titles)):

      #Acess specific axis for each plot
      ax = axs[i]

      #Create plot on the specific axis
      df_sub4.plot(ax=ax, column=col, cmap='coolwarm', legend=True)
      ax.set_title(title, fontsize=12)
      ax.set_axis_off()

      #Adjust legend size to prevent it from overlapping
      leg = ax.get_legend()
      if leg:
          leg.set_bbox_to_anchor((1.05, 0.5))  #Move legend outside plot
          leg.set_fontsize(8)

  #Adjust layout to prevent overlap of subplots and titles
  plt.subplots_adjust(hspace=0.4, wspace=0.4)

  #Show all 3 plots in a single figure
  plt.show()

"""Maps of the land cover variables."""

def Figure10():
  # Create a 2x3 grid of subplots (2 rows, 3 columns)
  fig, axs = plt.subplots(2, 3, figsize=(15, 18))

  #Create list of the coefficients column and titles for the 6 plots
  coeff_columns = ['X0_coef', 'X9_coef', 'X19_coef',
                 'X20_coef', 'X21_coef', 'X30_coef']
  titles = [
    'A) Local Coefficients \n Industrial or commercial units',
    'B) Local Coefficients \n Coniferous forest',
    'C) Local Coefficients \n Mixed forest',
    'D) Local Coefficients \n Moors and heathland',
    'E) Local Coefficients \n Natural grasslands',
    'F) Local Coefficients \n Transitional woodland-shrub'
  ]

  #Loop through each subplot and plot map
  for i, (col, title) in enumerate(zip(coeff_columns, titles)):
      #Get row and column index for the current subplot
      row, col_idx = divmod(i, 3)

      ax = axs[row, col_idx]  #Access specific axis from the grid

      #Create plot on the specific axis
      df_sub4.plot(ax=ax, column=col, cmap='coolwarm', legend=True)
      ax.set_title(title, fontsize=10)
      ax.set_axis_off()

      #Adjust legend size to prevent it from overlapping
      leg = ax.get_legend()
      if leg:
          leg.set_bbox_to_anchor((1.05, 0.5))  #Move legend outside plot
          leg.set_fontsize(8)

  #Adjust layout to prevent overlap of subplots and titles
  plt.subplots_adjust(hspace=0.4, wspace=0.4)

  #Show all 6 plots in a single figure
  plt.show()



"""## **Part 7: Checking OLS assumptions and Trying data transformations.**

For the purpose of this project, an OLS model was used for analysis of the data, to demonstrate use of taught statistical techniques on the course. However, when checking the assumptions of the model, it appears the data violates the assumptions.

The ordinary least squares (OLS) regression has the following assumptions:
* Linearity
* Homoscedasticity
* Normality of residuals
* No multicollinearity (this was checked earlier)
* No autocorrelation

1) Check **linearity**, using total annual precipitation as an example environmental variable.
"""

#Add constant (constant) to the feature matrix
X_with_intercept = sm.add_constant(X)

#Predicted values from the OLS model using the updated X
y_pred_ols = ols_model.predict(X_with_intercept)

#Check Linearity

# Scatter plot of observed vs predicted values
plt.scatter(df_sub2['frp'], df_sub2['annual_total_precip'], label='Observed', color='blue')
plt.plot(df_sub2['frp'], y_pred_ols, label='Fitted line (OLS)', color='red')
plt.xlabel("Fire Radiative Power (MW)")
plt.ylabel("Annual Total Precipitation (mm)")
plt.title("Observed vs Predicted: Fire Intensity vs Annual Total Precipitation (OLS)")
plt.legend()
plt.show()

"""Result: The linearity assumption is violated.

2) Check **homoscedasticity** with a Residuals vs Fitted values plot.
"""

#Plot residuals vs fitted value

# Residuals vs predicted values
plt.scatter(y_pred_ols, ols_residuals)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals vs Predicted Values (OLS)')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.show()

"""Result: The Residuals VS Fitted values plot does not show random scatter, thus homoscedasticity seems to be violated.

3) We check the **normality** assumption with a Q-Q plot and a Shapiro test.
"""

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(ols_residuals, line ='45')
plt.title("Q-Q Plot of OLS Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(ols_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: The FRP data is not normally distributed, thus we try transforming the data with :
* log transformation
* square-root transformation
* Box-Cox transformation

**Log Transformation:**
"""

#Create new column with log transformation of frp
df_sub2['log_transformed_frp'] = np.log(df_sub2['frp'] + 1)  #Add +1 to avoid log(0) issues

#OLS Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['log_transformed_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
log_ols_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
log_residuals = log_ols_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(log_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(log_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: The log trasnformation did not normalise the data.

**Square-root Transformation:**
"""

#Create new column with sqrt transfromation of frp
df_sub2['sqrt_transformed_frp'] = np.sqrt(df_sub2['frp'])

#OSL Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['sqrt_transformed_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
sqrt_ols_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
sqrt_residuals = sqrt_ols_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(sqrt_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(sqrt_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: Transforming the data with a square-root transformation does not help normalise the data.

**Box-Cox Transformation**

The Box-Cox method allows to convert non-normal data into normal data. It helps to find the best power, lambda (λ),to transform the data to a normal distribution.
"""

#Apply Box-Cox transformation to the 'frp' column
transformed_data, lambda_ = stats.boxcox(df_sub2['frp'])

#Create new column with Box-Cox transformation of frp
df_sub2['box_cox_frp'] = transformed_data

#Show lambda value
print(f"Optimal Box-Cox Lambda: {lambda_}")

"""The lambda value is negative which indicates a negative power transformation. The dependent variable (FRP) should be transformed as y**(−0.47).


"""

#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['box_cox_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
box_cox_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
box_cox_residuals = box_cox_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(box_cox_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Add constant (constant) to the feature matrix
X_with_intercept = sm.add_constant(X)

#Predicted values from the OLS model using the updated X
y_pred_box_cox = box_cox_model.predict(X_with_intercept)

#Plot residuals vs fitted value

# Residuals vs predicted values
plt.scatter(y_pred_ols, box_cox_residuals)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals vs Predicted Values (OLS)')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(box_cox_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""The Box-Cox transformation helped bring the data closer to a normal distribution and addressed the issue of homoscedasticity. However, the data still does not follow a normal distribution."""

#Checking for over dispersion
#Calculate variance and mean of FRP
var_frp = df_project['frp'].var()
mean_frp = df_project['frp'].mean()
print(var_frp)
print(mean_frp)

"""**Conclusion:**
* all three asumption (linearity, homoscedasticty and normality) are violated
* there is no high multicollinearity (seen in heatmap)
* the data seems right skewed (seen in FRP histogram)
* the data is overdispersed as the variance (1007.3) is much higher than the mean (18.6)

Therefore, an OLS regression model is not appropriate to analyse the data.

Other statistical tests should be used to test the relationship between fire intensity (FRP) and environmental variables.
"""



"""## **Part 7: Checking OLS assumptions and Trying data transformations.**

For the purpose of this project, an OLS model was used for analysis of the data, to demonstrate use of taught statistical techniques on the course. However, when checking the assumptions of the model, it appears the data violates the assumptions.

The ordinary least squares (OLS) regression has the following assumptions:
* Linearity
* Homoscedasticity
* Normality of residuals
* No multicollinearity (this was checked earlier)
* No autocorrelation

1) Check **linearity**, using total annual precipitation as an example environmental variable.
"""

#Add constant (constant) to the feature matrix
X_with_intercept = sm.add_constant(X)

#Predicted values from the OLS model using the updated X
y_pred_ols = ols_model.predict(X_with_intercept)

#Check Linearity

# Scatter plot of observed vs predicted values
plt.scatter(df_sub2['frp'], df_sub2['annual_total_precip'], label='Observed', color='blue')
plt.plot(df_sub2['frp'], y_pred_ols, label='Fitted line (OLS)', color='red')
plt.xlabel("Fire Radiative Power (MW)")
plt.ylabel("Annual Total Precipitation (mm)")
plt.title("Observed vs Predicted: Fire Intensity vs Annual Total Precipitation (OLS)")
plt.legend()
plt.show()

"""Result: The linearity assumption is violated.

2) Check **homoscedasticity** with a Residuals vs Fitted values plot.
"""

#Plot residuals vs fitted value

# Residuals vs predicted values
plt.scatter(y_pred_ols, ols_residuals)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals vs Predicted Values (OLS)')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.show()

"""Result: The Residuals VS Fitted values plot does not show random scatter, thus homoscedasticity seems to be violated.

3) We check the **normality** assumption with a Q-Q plot and a Shapiro test.
"""

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(ols_residuals, line ='45')
plt.title("Q-Q Plot of OLS Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(ols_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: The FRP data is not normally distributed, thus we try transforming the data with :
* log transformation
* square-root transformation
* Box-Cox transformation

**Log Transformation:**
"""

#Create new column with log transformation of frp
df_sub2['log_transformed_frp'] = np.log(df_sub2['frp'] + 1)  #Add +1 to avoid log(0) issues

#OLS Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['log_transformed_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
log_ols_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
log_residuals = log_ols_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(log_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(log_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: The log trasnformation did not normalise the data.

**Square-root Transformation:**
"""

#Create new column with sqrt transfromation of frp
df_sub2['sqrt_transformed_frp'] = np.sqrt(df_sub2['frp'])

#OSL Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['sqrt_transformed_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
sqrt_ols_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
sqrt_residuals = sqrt_ols_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(sqrt_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(sqrt_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""Result: Transforming the data with a square-root transformation does not help normalise the data.

**Box-Cox Transformation**

The Box-Cox method allows to convert non-normal data into normal data. It helps to find the best power, lambda (λ),to transform the data to a normal distribution.
"""

#Apply Box-Cox transformation to the 'frp' column
transformed_data, lambda_ = stats.boxcox(df_sub2['frp'])

#Create new column with Box-Cox transformation of frp
df_sub2['box_cox_frp'] = transformed_data

#Show lambda value
print(f"Optimal Box-Cox Lambda: {lambda_}")

"""The lambda value is negative which indicates a negative power transformation. The dependent variable (FRP) should be transformed as y**(−0.47).


"""

#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['box_cox_frp']

# Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit OLS model
box_cox_model = sm.OLS(y, X).fit()

#Get residuals from the fitted model
box_cox_residuals = box_cox_model.resid

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(box_cox_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

#Add constant (constant) to the feature matrix
X_with_intercept = sm.add_constant(X)

#Predicted values from the OLS model using the updated X
y_pred_box_cox = box_cox_model.predict(X_with_intercept)

#Plot residuals vs fitted value

# Residuals vs predicted values
plt.scatter(y_pred_ols, box_cox_residuals)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals vs Predicted Values (OLS)')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.show()

#Shapiro Test
stat, p_value = stats.shapiro(box_cox_residuals)

print(f"Shapiro-Wilk Test: stat={stat}, p-value={p_value}")

"""The Box-Cox transformation helped bring the data closer to a normal distribution and addressed the issue of homoscedasticity. However, the data still does not follow a normal distribution."""

#Checking for over dispersion
#Calculate variance and mean of FRP
var_frp = df_project['frp'].var()
mean_frp = df_project['frp'].mean()
print(var_frp)
print(mean_frp)

"""**Conclusion:**
* all three asumption (linearity, homoscedasticty and normality) are violated
* there is no high multicollinearity (seen in heatmap)
* the data seems right skewed (seen in FRP histogram)
* the data is overdispersed as the variance (1007.3) is much higher than the mean (18.6)

Therefore, an OLS regression model is not appropriate to analyse the data.

Other statistical tests should be used to test the relationship between fire intensity (FRP) and environmental variables.

## **Part 8: Extra Analysis Attempt**

In this part of the analysis, we attempt to fit a Gamma Regression Model, as an OLS regression was shown not to be appropriate.
"""

#Gamma Regression model
#Define independent and dependent variables
#omit Industrial or commercial units because it is the most common land cover, will be the constant
X = df_sub2[['Year',
             'elevation',
             'annual_avg_temp',
             'annual_total_precip',
             'annual_avg_wind_speed',
             'Lc__Airports',
             'Lc__Broad-leaved forest',
             'Lc__Complex cultivation patterns',
             'Lc__Coniferous forest',
             'Lc__Construction sites',
             'Lc__Continuous urban fabric',
             'Lc__Discontinuous urban fabric',
             'Lc__Dump sites',
             'Lc__Fruit trees and berry plantations',
             'Lc__Green urban areas',
             'Lc__Inland marshes',
             'Lc__Land principally occupied by agriculture, with significant areas of natural vegetation',
             'Lc__Mineral extraction sites',
             'Lc__Mixed forest',
             'Lc__Moors and heathland',
             'Lc__Natural grasslands',
             'Lc__Non-irrigated arable land',
             'Lc__Pastures', 'Lc__Peat bogs',
             'Lc__Port areas',
             'Lc__Road and rail networks and associated land',
             'Lc__Salt marshes',
             'Lc__Sparsely vegetated areas',
             'Lc__Sport and leisure facilities',
             'Lc__Transitional woodland-shrub',
             'Lc__Water bodies']]
y = df_sub2['frp']

#Add a constant (intercept) to the independent variable
X = sm.add_constant(X)

#Fit Gamma regression model with log link
gamma_model = sm.GLM(y, X, family=sm.families.Gamma(link=sm.families.links.log())).fit()

#Get residuals from the fitted model
gamma_residuals = gamma_model.resid_response

#Gamma regression model summary
print(gamma_model.summary())

"""**Diagnostic Plots of model**"""

# Plot residuals
plt.figure(figsize=(10, 6))
plt.scatter(y, gamma_residuals, alpha=0.7)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Observed FRP')
plt.ylabel('Residuals')
plt.title('Residuals vs Observed FRP')
plt.show()

#Q-Q Plot
plt.figure(figsize=(8, 6))
sm.qqplot(gamma_residuals, line ='45')
plt.title("Q-Q Plot of Residuals")
plt.show()

"""The diagnostic plots show the assumptions of normality and homoscedastic are violated. Thus the gamma regression model is not appropriate for analysis either.
"""
