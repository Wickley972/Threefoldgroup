from datetime import datetime
import io
import zipfile
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.conf import settings
import os
from os import listdir

from django.urls import reverse
from .forms import Csv2ExcelForm, FileFieldForm, Excel2CsvForm, importForm, BtaForm, ExpForm
from django.views.generic.edit import FormView
from .scripts.outils import csv_to_excel, excel_to_csv  # Import your python script
from .scripts import importScript, BtaScript, ExpScript
from werkzeug.utils import secure_filename
from time import sleep
import shutil

def index(request):
    return render(request, 'hcc/index.html')

def export(request):
    return render(request, 'hcc/export.html')

def bta(request):
    return render(request, 'hcc/export/bta.html')

def exp(request):
    return render(request, 'hcc/export/exp.html')

def outils(request):
    return render(request, 'hcc/outils.html')

def csv2excel(request):
    return render(request, 'hcc/outils/csv2excel.html')

def excel2csv(request):
    return render(request, 'hcc/outils/excel2csv.html')

# hcc/tmp sert a mettre les fichiers uploadé par l'utilisateur qui seront traité par la suite
tmpPath = os.path.join(settings.BASE_DIR, 'hcc/tmp')
# le tmp/output sert à mettre les fichiers générer par l'application temporairment avant de les renvoyé a l'utilisateur
outputPath = os.path.join(settings.BASE_DIR, 'hcc/tmp/output')
class importView(FormView):
    form_class = importForm
    template_name = "hcc/import.html"  # Replace with your template.
    success_url = "/"  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        #Formulaire pour les accounting data
        files = form.cleaned_data["firstForm"]
        #Formulaire pour les employee data
        secondForm = form.cleaned_data["secondForm"]
        # Le SAE code Thales ou GTS determine quelle directory choisir (voir Config.py)
        Env_SAECode = form.cleaned_data["sae_code"]
        # La variable ENV est utilisé pour détermine quelle directory choisir (TEST ou PROD) (Voir Config.py) 
        isTestOrProd = form.cleaned_data["env"]
        if Env_SAECode == 'Thales':
            isDebutOrFin = 'D'
        elif Env_SAECode == 'GTS':
            isDebutOrFin = 'F'
        else:
            exit()
        #emp = form.cleaned_data["emp"]
        
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d_%H%M%S")
        myRepo = os.path.join(tmpPath, currentTime)
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        os.mkdir(myRepo)
        accountingDataInputDir = os.path.join(myRepo, "Accountingdata")
        os.mkdir(accountingDataInputDir)
        employeeInputDir = os.path.join(myRepo, "Employee")
        os.mkdir(employeeInputDir)        
        myOutputRepo = os.path.join(myRepo, 'output')
        os.mkdir(myOutputRepo)
        myArchiveFile = os.path.join(myRepo, currentTime)

        for f in files:
            #f = secure_filename(f)
            # save each file to specific directory
            file_path = os.path.join(accountingDataInputDir, f.name)
            file_name = f.name.split('.')[0]
            output_path = os.path.join(myOutputRepo, file_name+'.csv')
            #filesList[f.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Call your script and process the files
        if secondForm:
            file_path = os.path.join(employeeInputDir, secondForm.name)
            file_name = secondForm.name.split('.')[0]
            #filesList[secondForm.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in secondForm.chunks():
                    destination.write(chunk)
        
        #try:
        importScript.main(Env_SAECode, isTestOrProd, isDebutOrFin, myOutputRepo, accountingDataInputDir, employeeInputDir)
        #except Exception as e:
         #   print(f"{f.name} Not processed !!! {e}")
        #allowed_file(list.filename):
        #clear_repo()
        
        shutil.make_archive(
                         myArchiveFile, #where put archive
                         'zip',
                         myOutputRepo, # repo to archive
                         )
        #clear_repo(withArchive=False)

        fileToReturn = open(myArchiveFile+'.zip', 'rb')

        response = FileResponse(fileToReturn)
        return response
    


class csv2excelView(FormView):
    form_class = Csv2ExcelForm
    template_name = "hcc/outils/csv2excel.html"  # Replace with your template.
    success_url = "."  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["firstForm"]       
        delimiter =  form.cleaned_data["delimiter"]
        if delimiter not in [',', ';', '|', '||'] or delimiter == '':
            print("Delimiteur non accepté !")
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d_%H%M%S")
        myRepo = os.path.join(tmpPath, currentTime)
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        os.mkdir(myRepo)
        myOutputRepo = os.path.join(myRepo, 'output')
        os.mkdir(myOutputRepo)
        myArchiveFile = os.path.join(myRepo, currentTime)

        for f in files:
            #f = secure_filename(f)
            # save each file to specific directory
            file_path = os.path.join(myRepo, f.name)
            file_name = f.name.split('.')[0]
            output_path = os.path.join(myOutputRepo, file_name+'.xlsx')
            #filesList[f.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Call your script and process the files
            try:
                csv_to_excel(input_file=file_path , output_file= output_path, sheet_name= file_name, index= False, header= False, delimiter= delimiter)
            except Exception as e:
                print(f"{f.name} Not processed !!! {repr(e)}")
            sleep(1)
        #allowed_file(list.filename):
        #clear_repo()
        
        shutil.make_archive(
                         myArchiveFile, #where put archive
                         'zip',
                         myOutputRepo, # repo to archive
                         )
        #clear_repo(withArchive=False)

        fileToReturn = open(myArchiveFile+'.zip', 'rb')

        response = FileResponse(fileToReturn)
        return response
    
class excel2csvView(FormView):
    form_class = Excel2CsvForm
    template_name = "hcc/outils/excel2csv.html"  # Replace with your template.
    success_url = "."  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["firstForm"]       
        delimiter =  form.cleaned_data["delimiter"]
        if delimiter not in [',', ';', '|', '||'] or delimiter == '':
            print("Delimiteur non accepté !")
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d_%H%M%S")
        myRepo = os.path.join(settings.BASE_DIR, 'hcc/tmp', currentTime)
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        os.mkdir(myRepo)
        myOutputRepo = os.path.join(myRepo, 'output')
        os.mkdir(myOutputRepo)
        myArchiveFile = os.path.join(myRepo, currentTime)

        for f in files:
            #f = secure_filename(f)
            # save each file to specific directory
            file_path = os.path.join(myRepo, f.name)
            file_name = f.name.split('.')[0]
            output_path = os.path.join(myOutputRepo, file_name+'.csv')
            #filesList[f.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Call your script and process the files
            try:
                excel_to_csv(input_file=file_path , output_file= output_path, delimiter= delimiter)
            except Exception as e:
                print(f"{f.name} Not processed !!! {repr(e)}")
            sleep(1)
        #allowed_file(list.filename):
        #clear_repo()
        
        shutil.make_archive(
                         myArchiveFile, #where put archive
                         'zip',
                         myOutputRepo, # repo to archive
                         )
        #clear_repo(withArchive=False)

        fileToReturn = open(myArchiveFile+'.zip', 'rb')

        response = FileResponse(fileToReturn)
        return response
    
class BtaView(FormView):
    form_class = BtaForm
    template_name = "hcc/export/bta.html"  # Replace with your template.
    success_url = "."  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["firstForm"]       
        
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d_%H%M%S")
        myRepo = os.path.join(settings.BASE_DIR, 'hcc/tmp', currentTime)
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        os.mkdir(myRepo)
        myOutputRepo = os.path.join(myRepo, 'output')
        os.mkdir(myOutputRepo)
        myArchiveFile = os.path.join(myRepo, currentTime)

        for f in files:
            #f = secure_filename(f)
            # save each file to specific directory
            file_path = os.path.join(myRepo, f.name)
            file_name = f.name.split('.')[0]
            #output_path = os.path.join(myOutputRepo, file_name+'.csv')
            #filesList[f.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Call your script and process the files
            try:
                BtaScript.main(input_file=file_path , output_repo= myOutputRepo)
            except Exception as e:
                print(f"{f.name} Not processed !!! {repr(e)}")
            sleep(1)
        #allowed_file(list.filename):
        #clear_repo()
        
        shutil.make_archive(
                         myArchiveFile, #where put archive
                         'zip',
                         myOutputRepo, # repo to archive
                         )
        #clear_repo(withArchive=False)

        fileToReturn = open(myArchiveFile+'.zip', 'rb')

        response = FileResponse(fileToReturn)
        return response
    
class ExpView(FormView):
    form_class = ExpForm
    template_name = "hcc/export/exp.html"  # Replace with your template.
    success_url = "."  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        files = form.cleaned_data["firstForm"]       
        
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d_%H%M%S")
        myRepo = os.path.join(settings.BASE_DIR, 'hcc', 'tmp', currentTime)
        if not os.path.exists(tmpPath):
            os.makedirs(tmpPath)
        os.mkdir(myRepo)
        myOutputRepo = os.path.join(myRepo, 'output')
        os.mkdir(myOutputRepo)
        myArchiveFile = os.path.join(myRepo, currentTime)

        for f in files:
            #f = secure_filename(f)
            # save each file to specific directory
            file_path = os.path.join(myRepo, f.name)
            file_name = f.name.split('.')[0]
            #output_path = os.path.join(myOutputRepo, file_name+'.csv')
            #filesList[f.name] = file_path
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # Call your script and process the files
            #try:
            ExpScript.main(input_file=file_path , output_repo= myOutputRepo)
            #except Exception as e:
             #   print(f"{f.name} Not processed !!! {repr(e)}")
            sleep(1)
        #allowed_file(list.filename):
        #clear_repo()
        
        shutil.make_archive(
                         myArchiveFile, #where put archive
                         'zip',
                         myOutputRepo, # repo to archive
                         )
        #clear_repo(withArchive=False)

        fileToReturn = open(myArchiveFile+'.zip', 'rb')

        response = FileResponse(fileToReturn)
        return response
    