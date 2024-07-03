from django.urls import path

from . import views

app_name = 'hcc'

urlpatterns = [
    path('', views.index, name='index'),
    #path('import/', views.upload_import_files, name='upload_import_files'),
    #path('bta/', views.upload_bta_files, name='upload_bta_files'),
    path('import/', views.importView.as_view(), name='import_module'),
    path('export/', views.export, name='export_menu'),
    path('export/bta/', views.BtaView.as_view(), name='bta'),
    path('export/exp/', views.ExpView.as_view(), name='exp'),
    path('outils/', views.outils, name='outils_menu'),
    path('outils/csv2excel', views.csv2excelView.as_view(), name='csv2excel'),
    path('outils/excel2csv', views.excel2csvView.as_view(), name='excel2csv'),
]