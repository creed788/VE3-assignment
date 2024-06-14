from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pandas as pd
from .forms import UploadCSVForm
from .forms import Plots
# from .models import CSVData
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import io
import base64
from pathlib import Path


def sanitize_filename(filename):
    """Remove or replace special characters in filenames."""
    return re.sub(r'[^\w\s-]', '', filename).replace(' ', '_')


def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            # Process the file using pandas
            df = pd.read_csv(fs.path(filename))

            # Data analysis
            first_rows = df.head()
            summary_stats = df.describe()
            missing_values = df.isnull().sum()
            missing_values = missing_values.to_dict()

            # Fill missing data
            for column in df.columns:
                if df[column].dtype in ['float64', 'int64']:
                    df[column].fillna(df[column].mean(), inplace=True)
                else:
                    df[column].fillna(df[column].mode()[0], inplace=True)

            # Generate Histogram
            histograms = []
            for column in df.select_dtypes(include=['float64', 'int64']).columns:
                sanitized_column = sanitize_filename(column)
                plot_path = os.path.join(settings.MEDIA_ROOT, f'{sanitized_column}_hist.png')
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(plot_path), exist_ok=True)
                
                plt.figure()
                sns.histplot(df[column].dropna(), kde=False)
                plt.savefig(plot_path)
                histograms.append(f'{sanitized_column}_hist.png')
                plt.close()   

            return render(request, 'csvapp/results.html', {
                'first_rows': first_rows.to_html(classes='table table-stripped'),
                'summary_stats': summary_stats.to_html(classes='table table-stripped'),
                'missing_values': missing_values,
                'file_url': file_url,
                'histograms': histograms,

            })
    else:
        form = UploadCSVForm()
    return render(request, 'csvapp/upload_csv.html', {'form': form})

  # def get(self, request, csv_data_id):
    #     csv_data = get_object_or_404(CSVData, id=csv_data_id)
    #     df = pd.DataFrame(csv_data.data)
    #     column_choices = [(col, col) for col in df.columns]
    #     form = Plots(column_choices=column_choices)
    #     return render(request, self.template_name, {'form': form, 'csv_data_id': csv_data_id})

class PlotView(View):
    template_name = 'csvapp/plots.html'
    def get(self, request):
        form = Plots()
        return render(request, self.template_name, {'form': form})
  
    def post(self, request):
        fld = '.media'
        files = Path(fld).glob('*.csv')
        latest = max(files, key=lambda f: f.stat().st_mtime)
        df = pd.DataFrame(latest.name)
        column_choices = [(col, col) for col in df.columns]
        form = Plots(request.POST, column_choices=column_choices)

        if form.is_valid():
            scatter_x = form.cleaned_data.get('x')
            scatter_y = form.cleaned_data.get('y')
            include_scatter = form.cleaned_data.get('include_scatter')
            include_histogram = form.cleaned_data.get('include_histogram')
            include_box = form.cleaned_data.get('include_box')

            context = {'form': form}

            if include_scatter and scatter_x and scatter_y:
                context['scatter_plot'] = self.get_scatter_plot(df, scatter_x, scatter_y)
            if include_histogram:
                context['histogram'] = self.get_histogram(df)
            if include_box:
                context['box_plot'] = self.get_box_plot(df)
                return render(request, self.template_name, context)

            return render(request, self.template_name, {'form': form})
        else:
            form = Plots()
        return render(request, self.template_name, {'form': form})

    def get_scatter_plot(self, df, x_col, y_col):
        fig, ax = plt.subplots()
        if x_col in df.columns and y_col in df.columns:
            sns.scatterplot(x=x_col, y=y_col, data=df, ax=ax)
        return self.plot_to_base64(fig)

    def get_histogram(self, df):
        fig, ax = plt.subplots()
        sns.histplot(df.select_dtypes(include=[int, float]).iloc[:, 0], kde=False, ax=ax)
        return self.plot_to_base64(fig)

    def get_box_plot(self, df):
        fig, ax = plt.subplots()
        sns.boxplot(data=df.select_dtypes(include=[int, float]), ax=ax)
        return self.plot_to_base64(fig)

    def plot_to_base64(self, fig):
        buf = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(buf)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)  
        return image_base64
    


# def plot_csv_data(request):
#     directory = 'media/'  # Directory where CSV files are stored
#     plot = None

#     if request.method == 'POST':
#         form = Plots(request.POST, directory=directory)
#         if form.is_valid():
#             # csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
#             # most_recent_csv = max(csv_files, key=lambda f: os.path.getctime(os.path.join(directory, f)))
#             # file_path = os.path.join(directory, most_recent_csv)
            
#             df = pd.read_csv(file_path)
#             x_axis = form.cleaned_data.get('scatter_x')
#             y_axis = form.cleaned_data.get('scatter_y')
            
#             plt.figure()
            
#             if form.cleaned_data.get('include_scatter') and x_axis and y_axis:
#                 df.plot.scatter(x=x_axis, y=y_axis)
                
#             if form.cleaned_data.get('include_histogram') and x_axis:
#                 df[x_axis].plot.hist(alpha=0.5)
                
#             if form.cleaned_data.get('include_box') and x_axis:
#                 df.boxplot(column=[x_axis])
            
#             buf = io.BytesIO()
#             plt.savefig(buf, format='png')
#             buf.seek(0)
#             plot = base64.b64encode(buf.getvalue()).decode('utf-8')
#             plt.close()
#     else:
#         form = Plots(directory=directory)

#     return render(request, 'template.html', {'form': form, 'plot': plot})



           
