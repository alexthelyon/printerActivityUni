# app.py
from flask import Flask, render_template
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Read data from Excel file
data = pd.read_excel("https://github.com/alexthelyon/printerActivityUni/raw/main/PrinterActivity2.xlsx")


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/print_frequency_analysis')
def print_frequency_analysis():
    # Convert 'PrintStartTimestamp' to datetime
    data['PrintStartTimestamp'] = pd.to_datetime(data['PrintStartTimestamp'].apply(lambda x: f"{pd.to_datetime('today').date()} {x}"))

    # Resample data by hour and count print jobs
    print_frequency = data.set_index('PrintStartTimestamp').resample('H').size().reset_index(name='Frequency')

    # Line graph of print frequency over time
    fig = px.line(print_frequency, x='PrintStartTimestamp', y='Frequency', title='Print Frequency Analysis')
    return render_template('print_frequency_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))



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


@app.route('/document_usage_analysis')
def document_usage_analysis():
    # Count of each document printed
    document_counts = data['DocumentID'].value_counts().reset_index()
    document_counts.columns = ['DocumentID', 'Count']

    # Group all documents except the top N most printed as "Others"
    top_n = 10
    top_documents = document_counts.head(top_n)
    other_count = document_counts.iloc[top_n:]['Count'].sum()
    top_documents.loc[top_n] = ['Others', other_count]

    # Create a bar plot
    fig = px.bar(top_documents, x='DocumentID', y='Count', title='Document Usage Analysis - Top {}'.format(top_n))

    return render_template('document_usage_analysis.html', plot=fig.to_html(include_plotlyjs='cdn'))

if __name__ == '__main__':
    app.run(debug=True)
