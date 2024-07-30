import pandas as pd
import plotly.express as px
import webbrowser

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

# Create the scatter plot using Plotly
scatter = px.scatter(data, x='Release Date', y='User Note', hover_name='Title', hover_data={'Release Date': False, 'User Note': False})

# Update layout
scatter.update_layout(
    title={'text': 'Video Game Ratings by Release Date', 'x': 0.5},
    xaxis_title='Release Date',
    yaxis_title='Rating',
    font=dict(
        size=18  # Set the font size for the entire plot
    ),
    hoverlabel=dict(
        font_size=16,  # Set the font size for hover text
        bgcolor='yellow'  # Set the background color for hover text
    )
)

# Save the interactive plot as an HTML file
file_path = 'interactive_plot.html'
scatter.write_html(file_path)

# Open the interactive plot in the web browser
webbrowser.open(file_path)
