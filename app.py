# app.py
from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import numpy as np


app = Flask(__name__)

# Read data from Excel file
data = pd.read_excel("https://github.com/alexthelyon/printerActivityUni/raw/main/PrinterActivity2.xlsx")


@app.route('/')
def index():
    return render_template('index.html')



#@app.route('/print_frequency_analysis')



@app.route('/print_job_duration_analysis')
def print_job_duration_analysis():
    # Histogram of print durations
    fig = px.bar(data, x='PrintDurationSeconds', nbins=20, title='Print Job Duration Analysis')
    return render_template('print_job_duration_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))



@app.route('/printer_performance_analysis')
def printer_performance_analysis():
    # Total print duration for each printer
    printer_duration = data.groupby('PrinterName')['PrintDurationSeconds'].sum().reset_index()
    fig = px.bar(printer_duration, x='PrinterName', y='PrintDurationSeconds', title='Printer Performance Analysis')
    return render_template('printer_performance_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))

def print_frequency_analysis():
    # Convert 'PrintStartTimestamp' to datetime
    data['PrintStartTimestamp'] = pd.to_datetime(data['PrintStartTimestamp'].apply(lambda x: f"{pd.to_datetime('today').date()} {x}"))

    # Resample data by hour and count print jobs
    print_frequency = data.set_index('PrintStartTimestamp').resample('H').size().reset_index(name='Frequency')

    # Line graph of print frequency over time
    fig = px.line(print_frequency, x='PrintStartTimestamp', y='Frequency', title='Print Frequency Analysis')
    return render_template('printer_performance_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))



@app.route('/document_usage_analysis')
def document_usage_analysis():
    # Count the number of times each document is printed
    document_counts = data['DocumentID'].value_counts()

    # Categorize documents based on the number of prints
    bins = [1, 2, 3, 4, np.inf]
    labels = ['Printed Once', 'Printed Twice', 'Printed Thrice', 'Printed Four Times or More']
    document_counts_categorized = pd.cut(document_counts, bins=bins, labels=labels, right=False)

    # Count the documents in each category
    categorized_counts = document_counts_categorized.value_counts()

    # Create a pie chart
    fig = px.pie(names=categorized_counts.index, values=categorized_counts.values, title='Document Usage Analysis')

    return render_template('document_usage_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))



@app.route('/efficient_printers_analysis')
def efficient_printers_analysis():
    # Calculate total print duration and count of prints for each printer
    printer_summary = data.groupby('PrinterName').agg(
        total_duration=('PrintDurationSeconds', 'sum'),
        total_prints=('PrinterName', 'count')
    ).reset_index()

    # Calculate average print duration for each printer
    printer_summary['average_duration'] = printer_summary['total_duration'] / printer_summary['total_prints']

    # Calculate efficiency metric: inverse of average duration times total prints
    # Higher efficiency means lower average duration and higher total prints
    printer_summary['efficiency'] = 1 / (printer_summary['average_duration'] * printer_summary['total_prints'])

    # Sort printers by efficiency and select top 10
    top_efficient_printers = printer_summary.sort_values(by='efficiency', ascending=False).head(10)

    return render_template('efficient_printers_analysis.html', printer_summary=top_efficient_printers)


if __name__ == '__main__':
    app.run(debug=True)
