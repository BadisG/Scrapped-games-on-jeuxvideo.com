import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import statsmodels.api as sm

# Read the CSV file
data = pd.read_csv('games.csv')

# Filter the data to keep only rows with ratings
data = data.dropna(subset=['User Note'])

# Convert release dates to datetime format
data['Release Date'] = pd.to_datetime(data['Release Date'])

# Filter the data to keep only rows with valid dates
data = data.dropna(subset=['Release Date'])

# Sort the data by release date
data = data.sort_values('Release Date')

# Local regression (LOESS)
lowess = sm.nonparametric.lowess
dates_ordinal = data['Release Date'].apply(lambda date: date.toordinal())
smoothed_values = lowess(data['User Note'], dates_ordinal, frac=0.2)

# Convert the results to a DataFrame for further processing
smoothed_data = pd.DataFrame(smoothed_values, columns=['Release Date', 'Smoothed Note'])
smoothed_data['Release Date'] = smoothed_data['Release Date'].apply(lambda date: pd.Timestamp.fromordinal(int(date)))

# Create the scatter plot
plt.figure(figsize=(10, 6))
scatter = plt.scatter(data['Release Date'], data['User Note'], color='b', label='Individual Ratings')

# Add the smoothed moving average curve
plt.plot(smoothed_data['Release Date'], smoothed_data['Smoothed Note'], color='r', label='Smoothed Ratings (LOESS)')

# Add labels and a title
plt.xlabel('Release Date')
plt.ylabel('Rating')
plt.title('Video Game Ratings by Release Date')
plt.legend()

# Add tooltips to display titles with adjusted opacity
cursor = mplcursors.cursor(scatter, hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(data['Title'].iloc[sel.index]))
cursor.connect("add", lambda sel: sel.annotation.get_bbox_patch().set(facecolor='yellow', alpha=1))

# Show the plot
plt.show()
