# app.py
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import datetime

app = Flask(__name__)

# Read data from Excel file
data = pd.read_excel("PrinterActivity2.xlsx")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def goHome():
    return render_template('index.html')

@app.route('/print_job_duration_analysis')
def print_job_duration_analysis():
    # Boxplot of print durations
    fig = px.line(data, y='PrintDurationSeconds', title='Print Job Duration Analysis')
    return render_template('print_job_duration_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))

@app.route('/printer_performance_analysis')
def printer_performance_analysis():
    # Total print duration for each printer
    printer_duration = data.groupby('PrinterName')['PrintDurationSeconds'].sum().reset_index()
    fig = px.bar(printer_duration, x='PrinterName', y='PrintDurationSeconds', title='Printer Performance Analysis')
    return render_template('printer_performance_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))


@app.route('/print_frequency_analysis.html')
def print_frequency_analysis():
    # Convert 'PrintStartTimestamp' to datetime
    data['PrintStartTimestamp'] = pd.to_datetime(data['PrintStartTimestamp'].apply(lambda x: f"{pd.to_datetime('today').date()} {x}"))
    # Resample data by hour and count print jobs
    print_frequency = data.set_index('PrintStartTimestamp').resample('H').size().reset_index(name='Frequency')

    # Line graph of print frequency over time
    fig = px.line(print_frequency, x='PrintStartTimestamp', y='Frequency', title='Print Frequency Analysis')
    return render_template('print_frequency_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))

if __name__ == '__main__':
    app.run(debug=True)
