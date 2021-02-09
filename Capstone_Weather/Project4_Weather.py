#!/usr/bin/env python
# coding: utf-8

# # Project 4: Weather Station Data

# Jake Berberian
# 
# MATH-465: Numerical Analysis
# 
# Data can be found at https://www.wunderground.com/dashboard/pws/KDCWASHI280/table/2020-11-30/2020-11-30/monthly

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings; warnings.filterwarnings('ignore')
from sklearn import linear_model 
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict


# In[2]:


# Set plot styles
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")


# ## Data Import and Clean

# We'll start by reading in our personal weather station (PWS) data located in Glover Park, Washington, D.C. (20007). We're using September data to complement NOAA's available data. September is also an interesting month to study because it is generally considered an autumn month, but recently we've seen the average temperatures rising in the ninth month.

# In[3]:


gp = pd.read_csv("weather_gloverpark.csv")

gp.head()


# In[4]:


gp.tail()


# We see that indeed, September temperatures seem somewhat higher than we would expect. However, before any analysis, we need to do some data cleaning. First, we'll remove any columns that we don't plan on using in our analysis.

# In[5]:


gp = gp.filter(['Date','temp_hi', 'temp_avg', 'temp_lo', 'cum_precip'])
gp.head()


# We really narrowed our dataset. This is okay, because we're only focusing on the temperature and precipitation. For a larger project, we could keep more of the other variables. The next issue that we notice is that our data points all include units. This is good practice when posting data somewhere, but will make analysis impossible, so we'll fix this. Furthermore, to make the dates easier to work with, we can covert them into datetime objects.

# In[6]:


gp[gp.columns[1:]] = (gp[gp.columns[1:]]
                      .replace("F", "", regex = True)
                      .replace("in", "", regex = True))
gp[gp.columns[1:]] = gp[gp.columns[1:]].astype(float)
gp["Date"] = pd.to_datetime(gp["Date"])
gp.head()


# We've cleaned out any characters and coverted all of our columns, sans *Date*, to floats. We're ready to read in some more data and attempt to triangulate. 

# We'll read in our NOAA data which comes from https://www.ncdc.noaa.gov/. It provides us with temperature and precipitation data for most of 2020 up until September. Again, we're using September because that's their most recent complete month. 

# In[7]:


noaa = pd.read_csv("noaa_sept.csv")
noaa.head()


# In[8]:


set(noaa["NAME"])


# We see that we have three separate data sources that we have this data from; all varying distances away from our Glover Park weather station. Our goal is to create a model that gives us weights for each pf these weather stations and render our personal weather station obsolete. However, personal weather stations are fun and can add data to networks (see Weather Undergound), helping to create even stronger weather readings. So while our model may be able to render our station obsolete, that's not the purpose of this project.

# Similar to above, we want to clean the data to ensure we are working with the correct structures. 

# In[9]:


noaa[noaa.columns[3:]] = noaa[noaa.columns[3:]].astype(float)
noaa["DATE"] = pd.to_datetime(noaa["DATE"])


# We now want to clean this data, such that we only include September data and we clean out some of the unnecessary columns. 

# In[10]:


noaa = noaa.drop(["DAPR", "MDPR"], axis = 1)
noaa_sept = noaa[noaa["DATE"].dt.month == 9]
noaa_sept = noaa_sept.rename(columns={"DATE": "Date"})
noaa_sept.head()


# One of the last data clean task before we join our two data sources is to widen our data set. This means that there should be a column for each observsation. In other words, instead of one date taking up three different rows, we will create three *TMAX* columns: one for each location. We'll repeat this process for *TMIN* and *PRCP*. 

# In[11]:


noaa_sept = noaa_sept.pivot(index = "Date", columns = "STATION", values = ["TMAX", "TMIN", "PRCP"])
noaa_sept.head()


# And finally, the end of the arduous data clean process. Due to the `pivot`, we must drop a level off the multilevel dataframe. After this, we'll get repeated columns names, so we'll rename all of out columns. For reference, below is each station and its new corresponding number attached to it:
# 
# - Station 1: Dalecarlia Reservoir
# - Station 2: National Arboretum
# - Station 3: Reagan National Airport

# In[12]:


noaa_sept.columns = noaa_sept.columns.droplevel(0)
noaa_sept.columns = ["TMAX_1", "TMAX_2", "TMAX_3", "TMIN_1", "TMIN_2", "TMIN_3", "PRCP_1", "PRCP_2", "PRCP_3"]
noaa_sept.head()


# It looks like all is in order for as far as data cleaning goes, so now we'll have to join our two tables by date.

# In[13]:


weather = pd.merge(left=gp, right=noaa_sept, how="inner", on="Date")
weather = weather.dropna()
weather.head()


# All looks good here. We had to drop two observations due to NAs, but we're ready for analysis!

# ## Exploratory Data Analysis

# Before we do any regression analysis, we'll take a look at our data and make sure it satisfies any assumptions. We'll first look at how the PWS data is distrbuted.

# In[14]:


plt.hist(weather["temp_hi"], bins = 10)
plt.xlabel("Temperature (F)")
plt.ylabel("count")
plt.title('Daily highs for September 2020') 
plt.show()


# We can see that the daily high temperature does not seem to have any distinct shape or skew. We'll further inverstigate by looking at the daily lows and averages.

# In[15]:


plt.hist(weather["temp_lo"], bins = 10)
plt.xlabel("Temperature (F)")
plt.ylabel("count")
plt.title('Daily lows for September 2020') 
plt.show()


# From above, we see that the daily lows take a somewhat similar shape, but has stronger tails. This is interesting as September is not always considered to be a month of extremes, but it seems that there have been some pretty low daily lows and some relatively high daily maximum temperatures. 

# ## Regression and Analysis

# Our response variable will be our PWS daily high temperatures, with our predictors being each of the three stations daily highs. After choosing these variables, our first step is to split our data into training and testing sets.  We will set aside 75% of our data for training the model, and the other 25% for testing the accuracy. This split is rather high, but with n = 28, we need to spend more of our data on training our model and making it less susceptible to outliers. 

# In[16]:


X_train, X_test, y_train, y_test = train_test_split(weather[["TMAX_1", "TMAX_2", "TMAX_3"]], weather["temp_hi"], test_size=0.25, random_state = 51)
X_train.shape, y_train.shape


# In[17]:


X_test.shape, y_test.shape


# Now that we're all set, we'll first attempt this regression using the maximum daily temperature.

# In[18]:


lm = linear_model.LinearRegression()
weather_lm = lm.fit(X_train, y_train)


# In[19]:


weather_lm.intercept_, weather_lm.coef_


# Thus, our estimated regression function is $\widehat{temp\_hi} = -5.29024 + 0.10998TMAX\_1 - 0.317634TMAX\_2 + 1.14581TMAX\_3$

# In[20]:


weather_lm.score(X_test, y_test)


# Furthermore, our corresponding $R^2$ value is 92.94%. In other words, 92.94% of the variance in our PWS data can be explained by our estimated regression function using the other three weather stations. This is pretty good, however it's important to remember that we don't have a ton of data to go off of.

# In[21]:


predictions = lm.predict(X_test)


# In[22]:


plt.scatter(y_test, predictions)
plt.plot([65,95], [65,95], color = "black")
plt.xlabel("True Value")
plt.ylabel("Predicted Value")
plt.title("Fit vs. Actual Scatterplot")
plt.show()


# Our predicted values seem to be pretty good. Ideally, we want them to follow the line $y = x$. It looks like there are a few observations that stray from this point but for the most part, our predicted values seem to be very solid. We'll check out the residuals next.

# In[23]:


sns.residplot(x=predictions, y=y_test, color="b")


# Our residuals, while scarce, look pretty good. There is definitely no inherent pattern to them, which indicates that our model is a pretty good fit to the data.

# ## Cross-Validation

# Cross-validation is to make sure our model is as finely tuned as possible. Rather than splitting the data, we can perform corssvalidation with k folds. We want the $R^2$ values to be as high as possible. We'll use a for loop to see the optimal number of folds we should use for cross-validation.

# In[24]:


for i in range(2, 12):
    cv = cross_val_score(weather_lm, weather[["TMAX_1", "TMAX_2", "TMAX_3"]], weather["temp_hi"], cv=i)
    print("K: ", i, ", Score: ", cv[i-1], sep = "")


# It seems that using k = 4 folds is the optimal amount. We'll make predictions using `cv = 4`. Doing this estimates the accuracy of our linear regresion model by splitting the data, fitting a model, and computing the score four consecutive times. Each time it does this with different splits.

# In[25]:


predictions = cross_val_predict(weather_lm, weather[["TMAX_1", "TMAX_2", "TMAX_3"]], weather["temp_hi"], cv = 4)
plt.scatter(weather["temp_hi"], predictions)
plt.plot([65,95], [65,95], color = "black")
plt.xlabel("True Value")
plt.ylabel("Predicted Value")
plt.title("Fit vs. Actual Scatterplot")
plt.show()


# The cross validation method allows us to use four times the number of points than before, since we used `cv = 4`. Again, we see that our model looks really solid. Our $R^2$ most likely benefits from the increase in data points, but they're still very concentrated around $y = x$, with no obvious outliers. 

# In[26]:


sns.residplot(x=predictions, y=weather["temp_hi"], color="b")


# Again, our residual vs. fit plot shows no obvious pattern, so again it seems that our predictions using cross-validation are good as well. 

# ## Further Steps

# - Importing more data
#     * Alternatively, figuring out a way to scrape both sites would be great. But seemingly very, very difficult for free in the case of Weather Underground and impossible for NOAA.
# - Using other techniques on our data
#     * Machine learning implementations may be overkill, but something like PCA with a larger dataset would be interesting.
# - Building out a precipitation collector
#     * See the difference in rainfall between different locations in DC
# - Finding other cities to do this in
# - Figuring out how phone predict weather at your given location

# ## Sources

# "Global Daily Summaries." *National Centers for Environmental Information*, NOAA National Centers for Environmental Information, 1988. gov.noaa.ncdc:C01318. 
# 
# 
# Massaron, Luca, and Alberto Boschetti. *Regression Analysis with Python: Learn the Art of Regression Analysis with Python*. Packt Publishing Ltd., 2016. 
