# app.py
from flask import Flask, render_template, abort
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats
import bleach #For HTML Sanitation and XSS Prevention
import logging #To Log Events



app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

# Define the allowed HTML tags and attributes for sanitization
ALLOWED_TAGS = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul']
ALLOWED_ATTRIBUTES = {'*': ['class'], 'a': ['href', 'title']}


def validate_data(data):
    # Check if the required columns are present
    required_columns = ['PrinterName', 'DocumentID', 'PrintDurationSeconds', 'PrintStartTimestamp']
    if not all(col in data.columns for col in required_columns):
       logging.error("Missing required columns in the Excel data")     
       raise ValueError("Missing required columns in the Excel data")



try:
    data = pd.read_excel("PrinterActivity2.xlsx")
    validate_data(data)
except Exception as e:
    logging.error(f"Error reading or validating Excel data: {e}")    
    print("Error reading Excel file:", e)
    abort(500, "Error reading Excel file")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/printer_performance_analysis')
def printer_performance_analysis():


    # <-------------------- Total Individual Printer Usage --------------------->
    

    printer_duration = data.groupby('PrinterName')['PrintDurationSeconds'].sum().reset_index()
    fig1 = px.bar(printer_duration, x='PrinterName', y='PrintDurationSeconds', title='Individual Printer Usage Analysis')


    # <-------------------- Print Frequency Over Time Line Graph --------------------->
    

    # Convert 'PrintStartTimestamp' to datetime
    data['PrintStartTimestamp'] = pd.to_datetime(data['PrintStartTimestamp'].apply(lambda x: f"{pd.to_datetime('today').date()} {x}"))
    # Resample data by hour and count print jobs
    print_frequency = data.set_index('PrintStartTimestamp').resample('H').size().reset_index(name='Frequency')
    # Line graph of print frequency over time
    fig2 = px.line(print_frequency, x='PrintStartTimestamp', y='Frequency', title='The Frequency Of Prints Analysis')
    

    # <-------------------- Print Frequency Over Time Bar Chart --------------------->
    
    #changed graph to bar.
    fig3 = px.bar(print_frequency, x='PrintStartTimestamp', y='Frequency', title='The Frequency Of Prints Analysis')
  

    # <-------------------- Printer Efficiency --------------------->
    

    printer_summary = data.groupby('PrinterName').agg(total_duration=('PrintDurationSeconds', 'sum'),
    total_prints=('PrinterName', 'count')).reset_index()

    # Calculate average print duration for each printer
    printer_summary['average_duration'] = printer_summary['total_duration'] / printer_summary['total_prints']

    # Calculate efficiency metric: inverse of average duration times total prints
    # Higher efficiency means lower average duration and higher total prints
    printer_summary['efficiency'] = 1 / (printer_summary['average_duration'] * printer_summary['total_prints'])

    # Round the efficiency to the 3rd decimal place
    printer_summary['efficiency'] = printer_summary['efficiency'].round(3)

    # Sort printers by efficiency in descending order
    printer_summary = printer_summary.sort_values(by='efficiency', ascending=False)

    # Select top 10 efficient printers
    top_efficient_printers = printer_summary.head(10)

    # <-------------------- Print Time Outliers Detection --------------------->
    
    # This code helps us find print jobs that took unusually long or short times compared to others.

    # Print Time Outliers Detection
    # Calculate quartiles and IQR
    Q1 = data['PrintDurationSeconds'].quantile(0.25) # The first quartile (25% of the data)
    Q3 = data['PrintDurationSeconds'].quantile(0.75) # The third quartile (75% of the data)
    IQR = Q3 - Q1 # The Interquartile Range (range between Q1 and Q3)

    # Define lower and upper bounds for outliers
    # These are the limits beyond which print durations are considered unusual.
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter the data to select outliers
    outliers = data[(data['PrintDurationSeconds'] < lower_bound) | (data['PrintDurationSeconds'] > upper_bound)]

    # Select the top 10 outliers based on their print duration
    top_outliers = outliers.nlargest(10, 'PrintDurationSeconds')[['DocumentID', 'PrinterName', 'PrintDurationSeconds', 'PrintStartTimestamp']]

    # ------------------------------------------------------------------------------------Sanitize input before rendering in HTML to prevent XSS vulnerabilities
    user_input = "<script>alert('XSS vulnerability')</script>"
    sanitized_input = bleach.clean(user_input, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    logging.info("User input sanitized successfully")

    #Render everything
    return render_template('printer_performance_analysis.html', 
                           plot1=fig1.to_html(include_plotlyjs='cdn'),
                           plot2=fig2.to_html(include_plotlyjs='cdn'), 
                           plot3=fig3.to_html(include_plotlyjs='cdn'), 
                           printer_summary=top_efficient_printers,
                           top_outliers=top_outliers,
                           sanitized_input=sanitized_input)



# Error Handling Below
# Makes better user experience and prevent sensitive information from being exposed in error messages.
@app.errorhandler(404)
def not_found_error(error):
    logging.error("Page not found")
    return render_template('error.html', error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error("Internal Server Error")
    return render_template('error.html', error_message="Internal Server Error"), 500



if __name__ == '__main__':
    app.run(debug=True)
