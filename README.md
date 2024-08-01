# Scrapped-games-on-jeuxvideo.com
Retrieves interesting information about games from [jeuxvideo.com](https://www.jeuxvideo.com/tous-les-jeux/)

# 1. games.csv
This file contains all the games's relevant informations (Title + User Ratings + Number of Ratings + Date of Release + Console)

It contains all the games on this site until 8/1/2024. Here's what it looks like:

<img src="https://github.com/user-attachments/assets/361565d4-c0f3-4863-a71a-26e1dd3ee272" width="500" />

# 2. requirements.txt
You need to install some special packages to be able to run the python scrips, here's the command:
```
pip install -r requirements.txt
```

# 3. Install playwright
You must execute this command before you can use playwrigt on a python script:
```
playwright install
```

# 4. scrap.py
```
python scrap.py
```
- This is the script used to scrap the games and put all the information into a CSV file.
- When you run it, the console will ask you to choose the start and end pages. 
- For example, if you want to scrape between pages 13 and 15, it will look like this: 

<img src="https://github.com/user-attachments/assets/092f5152-98e7-4c9a-8ac2-3b4bba73c46c" width="500" />

# 5. plot.py
```
python plot.py
```
This is an optional python script that can be used to visualize games through a scatter plot:
- It will create a file named ```interactive_plot.html```
- It will open that file

# 6. interactive_plot.html
This file can be opened with a browser such as Google Chrome or Firefox, and will look like this:


<img src="https://github.com/user-attachments/assets/e0d9b11e-fe3f-4284-a7b2-e2cd965b69b7" width="700" />

- You'll be able to see which game is on each point by hovering your mouse over it.
- If you feel there are too many points, you can filter a little by using a slider that will activate a threshold based on the number of user ratings.

# 7. Limitations
- **Incomplete date:**

Some games don't have the exact date format [(month/day/year)](https://www.jeuxvideo.com/jeux/super-nintendo-snes/00004222-secret-of-evermore.htm) and only have a (month/year) or a [year](https://www.jeuxvideo.com/jeux/jeu-59021/) format.
When this happens, the script makes an approximation and will guess a complete date format based on the information available to it. The guess is completely random and therefore has the advantage of producing a uniform distribution.

- **No date at all:**

From page 1740 onwards, all games with User Ranking have no date. There are exactly 1628 of such games and unfortunately they won't be included in the plot unless we have to retrieve their dates manually....


