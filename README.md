# PL-Standings-Dashboard
An interactive Dash web application to visualize the Premier League standings for the current and previous seasons.

The application retrieves the standings data from the [SportsDB API](https://www.thesportsdb.com/free_sports_api). Data is retrieved for the current season and the last nine seasons. Dash is then used to create an interactive web application that allows the user to visualize this data for a selected season. The application includes an interactive Dash standings table, an interactive Plotly bar chart, and an interactive Plotly scatter plot where users can select the axes to plot.

Here’s a preview of how the web application looks:

![example](https://github.com/user-attachments/assets/797809d1-69db-450f-9c25-2d433cedbdca)

## Technologies

This project is built using the following technologies:  

- **[Dash](https://dash.plotly.com/) (v2.14.2)**
- **[Plotly](https://plotly.com/python/) (v5.24.1)** 
- **[Pandas](https://pandas.pydata.org/) (v2.2.3)** 
- **[Requests](https://docs.python-requests.org/en/latest/) (v2.32.3)**  
- **Python Standard Libraries** – Includes `json`, `logging`, `datetime`, and `os.path`.  

## How to Run

### 1. Install Dependencies

First, install the required dependencies:
```
pip install -r requirements.txt
```

### 2. Run the Application

Then, run the Dash application with the following command:
```
python3 app.py
```

### 3. Open in Browser

Finally, open your web browser and go to the provided address:
```
Dash is running on http://127.0.0.1:8050
```
