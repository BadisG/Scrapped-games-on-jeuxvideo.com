# Scrapped-games-on-jeuxvideo.com
Python script that retrieves interesting information about games from jeuxvideo.com + its CSV file

# 1. games.csv
This file contains all the games's relevant informations (Title + User ratings + Date of release + Console) from [jeuxvideo.com](https://www.jeuxvideo.com/tous-les-jeux/)

It has all the games on this site until 30/07/2024. Here's how it looks like:

<img src="https://github.com/user-attachments/assets/fece0a0f-c55a-44fd-8fff-f684b909bd09" width="500" />

# 2. requirements.txt
You need to install some special packages to be able to run the python scrips, here's the command:
```
pip install -r requirements.txt
```

# 3. scrap.py
```
python scrap.py
```
This is the script used to scrape games and put all the information into a csv.
When you run it, the console will ask you to choose the starting and ending pages.
For example, if you want to scrap between the page 13 and 15, it will look like this:

<img src="https://github.com/user-attachments/assets/092f5152-98e7-4c9a-8ac2-3b4bba73c46c" width="500" />

# 4. plot.py
```
python plot.py
```
This is an optional python script that can be used to visualize games through a scatter plot:
- It will create a file named ```interactive_plot.html```
- It will open that file

# 5. interactive_plot.html
This file can be opened with a browser such as Google Chrome or Firefox, and will look like this:

<img src="https://github.com/user-attachments/assets/df4ec494-c085-47a8-b1fb-213ba67f5e0a" width="700" />

What's interesting about this plot is that you can see which game title is on each dot by hovering your mouse over it.

