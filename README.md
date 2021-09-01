# London-Air-Quality
Impact analysis of Covid-19 on London Air Quality

Code Structure

data_mean: This folder contains all the static data of pollutant levels in csv fomat for each borough. The data is present in daily and weekly format for various analysis tasks.
static: This folder contains all the static contents used in the application. Like images, GIFs and javascript codes
templates: This folder is the container of all the HTML files.
			
			layout.html - This page defines the common HTML and CSS layout which is extended to all pages. Like the main navigation bar, background and the title. 
			
			home.html - This is the first page which loads when the user opens the app, It has a GIF representing the changeof AQI for London through the period of analysis and includes a write-up on the analysis done on the effect of COvid-19 on the level of pollution in London. User can also reach this page by clicking on the "Home" button on the Navigation Bar at the top of all the pages.
			
			boroughwise.html - This pages has buttons for all the boroughs of London for which the analysis is aviable. By clicking on any of the borough buttons, user can choose to view a detailed visual represention of the pollutions in a particular borough. This page can be reached by clicking on the "Boroughs" button on the top navigation bar of all the pages.
			
			borough.html - This is a dynamic page generated with details of any particular borough when the user clicks on the button with name of a particular borough in the boroughwise page. This page has a GIF representing the change of AQI for that borough through the period of analysis, table of dates on which each pollutant had the minimum level in that borough, an interactive and animated timeline graph for different pollutants and a group of gauge graphs for each pollutant level on a particular date, with the user having a option to choose a date from a dropdown calendar.
			
			about.html - This page provides background details of the data source, developer, details contacts and framework used by the application.
			
			
app.py: This is the application code written in Python Flask framework which serves the application. The Flask framework runs different function based on the user interactions and button clicks and renders the respective HTML webpage with static or dynamic contents. The program has the below functionalities:
            fetch_min_air_pollutant(borough_name): This function take borough name as input and returns a python dataframe formated in HTML contianing the details of value and date of minimum value for each pollutant.
			plot_line_air_pollutant(borough_name): This function take borough name as input and returns a python plotly interative and animated line chart suited for embedded in webpage to represent the timeline of change of level of each pollutant over the analysis period.
			gauge_plot(borough_name,val_date): This function take borough name and date as input and returns python plotly gauge plots to represent level of each pollutant on a particular date.


App URL: https://londonairquality.herokuapp.com/
Used Heroku PAAS to deploy the application
