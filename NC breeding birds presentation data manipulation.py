#!/usr/bin/env python
# coding: utf-8

# # Find out how the bird population in NC has changed over time #
# 

# In[68]:


#imports
import pandas as pd
import numpy as np


# In[45]:


bird_names_file = 'birbs.csv' #file path

nc_birbs = pd.read_csv(bird_names_file)
nc_birbs.head()


# ## Find the net flux of birds through time##
# ### Story Point 4 ###
# #### Species lost and gained through time ####

# In[46]:


#Find the net flux of birds through time
#Species lost and gained through time
birds = nc_birbs.copy()


# In[47]:


birds.index = birds['Species List']
birds.drop('Species List', axis=1, inplace=True)
birds.drop(['Route Count','Total Species','Total individuals'], inplace=True)
birds.head()


# In[48]:


def start_year(bird, years, name):
    """This function takes a single bird's data and returns the name of the bird and the first year it was
    seen in the data"""
    for yr in range(len(bird)):
        year = years[yr]
        if bird[yr] != 0:
            break
    return [name, year]


# In[49]:


def last_year(bird,years,name):
    """This function takes a single bird's data and returns the name of the bird and the first year it was
    missing from the data"""
    for yr in reversed(range(len(bird))):
        year = years[yr]
        if bird[yr] != 0:
            break
    return [name, int(year)+1]


# In[50]:


def last_list(df):
    """Takes the birds dataframe and for each species finds when it was last seen in the bird count"""
    end_df = pd.DataFrame(columns=['Species', 'Year'])
    birds = df.index
    years = df.columns
    for bird in birds:
        row = pd.DataFrame(last_year(df.loc[bird],df.columns,bird)).transpose()
        row.columns = ['Species','Year']
        end_df = pd.concat([end_df,row])
    lost = end_df[end_df.Year != 2019] #only return those species that have dissapeared
    return lost


# In[51]:


def start_list(df):
    """Takes the birds dataframe and for each species finds when it was first seen in the bird count"""
    start_df = pd.DataFrame(columns=['Species', 'Year'])
    birds = df.index
    years = df.columns
    for bird in birds:
        row = pd.DataFrame(start_year(df.loc[bird],df.columns,bird)).transpose()
        row.columns = ['Species','Year']
        start_df = pd.concat([start_df,row])
    introduced = start_df[start_df.Year != '1966'] #do not include those that were present at the start of the data
    return introduced
        


# In[52]:


species_introduced = start_list(birds).reset_index(drop=True)
species_lost = last_list(birds).reset_index(drop=True)
species_lost.head()


# ##### output for tableau #####

# In[53]:


#output for tableau
species_introduced.to_csv('introduced.csv')
species_lost.to_csv('lost.csv')


# #### New and lost species count through time and net flux ####

# In[54]:


#New and lost species count through time and net flux
count_intro = species_introduced.groupby('Year').count()
count_lost = species_lost.groupby('Year').count()

years = birds.columns #list all years for for loop

#add all years to the dataframe that didn't lose or gain species
for yr in years:
    if yr not in count_intro.index:
        count_intro = pd.concat([count_intro, pd.DataFrame({'Species': 0}, index = [yr])])
for yr in years.astype(int):
    if yr not in count_lost.index:
        count_lost = pd.concat([count_lost, pd.DataFrame({'Species': 0}, index = [yr])])

count_intro.columns = ['Introduced']
count_lost.columns = ['Lost']
count_intro.index = count_intro.index.astype(int)

flux = count_intro.merge(count_lost, left_index=True, right_index=True).sort_index()
flux['Net Change'] = flux.Introduced - flux.Lost
flux.head()


# ##### output for tableau #####

# In[55]:


#output for tableau
flux.to_csv('bird_flux.csv')


# ## Create Tidy Data for Tableau ##
# ### Story Point 1 and 2 ###

# In[56]:


#Create Tidy Data for Tableau

breeding = nc_birbs.transpose()
breeding.reset_index(inplace=True)
breeding.iloc[0,0] = 'Year'
breeding.columns = breeding.iloc[0]
breeding = breeding.iloc[1:]
breeding.drop('Route Count', axis=1, inplace=True)
breeding.head()


# In[65]:


#melt bird columns to make each row an observation of a single species count in a single year
output = pd.melt(breeding, id_vars=['Year', 'Total Species','Total individuals'])


# ##### output for tableau #####

# In[50]:


#output for tableau
output.to_csv('nc_breeding_birds_66_18.csv')


# ## Find the average top 10 species for each group of years

# In[66]:


#Find the average top 10 species for each group of years
#make year datetime index and turn numeric columns into int type
output.Year = pd.to_datetime(output.Year)
output.index = output.Year
output.drop('Year', axis=1, inplace=True)
output.columns = ['tot_spec','tot_inds','species','birdcount']
cols = output.columns.drop('species')
output[cols] = output[cols].apply(pd.to_numeric,errors='coerce')
output.head()


# In[128]:


#empty dataframe to input the ranks through the years
master = pd.DataFrame(columns=['species','tot_spec','tot_inds','birdcount','rank'])
master


# In[129]:


def avg_yrs(df, start, end, top):
    """This function takes the output df over a range of years and finds the average most populous species the top
    numeric value for 'top' is included"""
    dfyrs = df.loc[str(start):str(end),:]
    yrdf = dfyrs.groupby('species').mean().sort_values('birdcount', ascending=False).reset_index().iloc[:top,:]
    yrdf['rank'] = range(1,top+1)
    yrdf['years'] = start
    return yrdf


# In[130]:


#Year groups defined by 10 equally spaced intervals
start = np.linspace(1966,2019, 10)
srt = [int(yr) for yr in start][:-1] #start leaves out end point
end = [int(yr)-1 for yr in start[1:]] #end leaves out start point


# In[134]:


for s,e in zip(srt,end):
    df = avg_yrs(output,s,e,5)
    master = pd.concat([master,df],sort=False)
master.head()


# ##### Save to Output #####

# In[67]:


#save to output
master.to_csv('grouped.csv')


# In[ ]:




