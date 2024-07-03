from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    firstForm = MultipleFileField()

from django.utils.safestring import mark_safe


class Csv2ExcelForm(forms.Form):
    firstForm = MultipleFileField(label = "Fichier CSV")
    d_choices = (
    (",", "Virgule : ,"),
    (";", "Point virgule : ;"),
    ("|", "Barre : |"),
    ("||", "Double barre : ||"),
    )
    delimiter = forms.ChoiceField(widget=forms.RadioSelect(), choices=d_choices, initial=(",", "Virgule : ,"))#required=True, default= ',', editable= False, 
 
class Excel2CsvForm(forms.Form):
    firstForm = MultipleFileField(label = "Fichier XLSX")
    d_choices = (
    (",", "Virgule : ,"),
    (";", "Point virgule : ;"),
    ("|", "Barre : |"),
    ("||", "Double barre : ||"),
    )
    delimiter = forms.ChoiceField(widget=forms.RadioSelect(), choices=d_choices, initial=(",", "Virgule : ,"))#required=True, default= ',', editable= False, 
    
class importForm(forms.Form):
    firstForm = MultipleFileField(label = "Télécharger un/ou plusieurs fichiers Accounting Data", required=False)
    secondForm = forms.FileField(label = "Télécharger un seul fichier Employee", required=False)
    SAECode_choices = (
    ("Thales", "Thales"),
    ("GTS", "GTS"),
    )
    sae_code = forms.ChoiceField(widget=forms.RadioSelect(), choices=SAECode_choices, initial=("Thales", "Thales"))#required=True, default= ',', editable= False, 
    env_choices = (
    ("P", "Production"),
    ("T", "Test"),
    )
    env = forms.ChoiceField(widget=forms.RadioSelect(), choices=env_choices, initial=("P", "Prodction"))

    """emp_choices = (
    ("D", "Début"),
    ("F", "Fin"),
    )
    emp = forms.ChoiceField(widget=forms.RadioSelect(), choices=emp_choices, initial=("D", "Début"))"""

class BtaForm(forms.Form):
    firstForm = MultipleFileField(label = "Télécharger un/ou plusieurs fichiers BTA")

class ExpForm(forms.Form):
    firstForm = MultipleFileField(label = "Télécharger un/ou plusieurs fichiers EXP")