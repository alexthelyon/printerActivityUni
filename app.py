# app.py
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import numpy as np
from scipy import stats



app = Flask(__name__)

# Read data from Excel file
data = pd.read_excel("PrinterActivity2.xlsx")


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




    return render_template('printer_performance_analysis.html', 
                           plot1=fig1.to_html(include_plotlyjs='cdn'),
                           plot2=fig2.to_html(include_plotlyjs='cdn'), 
                           plot3=fig3.to_html(include_plotlyjs='cdn'), 
                           printer_summary=top_efficient_printers)

if __name__ == '__main__':
    app.run(debug=True)
