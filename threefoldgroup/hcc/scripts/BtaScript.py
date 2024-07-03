import csv
from os import listdir, path, unlink, mkdir, system, name
import shutil
from datetime import datetime
from time import sleep
import json

# GLOBAL VARIABLES
VAL_1 = 'Company Hierarchy'
#VAL_2 = 'Thales'
PRODUCTION_DIRECTORY = 'p06084973s3r'
TEST_DIRECTORY = 't060849864ks'
ENCODING = 'utf-8-sig'

# WRITE DATA
def write_bta_data(output_file_name, input_file_name):
    myDict = {}
    invoiceSet = set()
    lines = list()
    with open(input_file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=';')
        next(reader, None)
        for row in reader:
            #Récuperation de la data selon les fichiers specs
            c1 = "SpringboardBTA"
            c2 = ""
            c3 = ""
            c4 = row[41]
            c5 = row[164]
            #c5 = '107481R'
            #c6 = "f" 
            #c7 = str(int(row[149])) # C'etait un entrier 
            c7 = str(row[149])

            c8 = row[24]
            c9 = row[21]
            #c10 = 0
            #c11 = "f"
            c12 = row[30]
            c13 = row[109] + " | Related to " + row[238]
            #c14 = "f"
            c15 = row[60]
            c16 = row[5] + ' ' + row[6] 
            c17 = "1"
            if row[17] == '':
                c18 = 0
            else:
                c18 = float(row[17])
            c19 = c18
            #c20 = row[120]
            if row[120] == '':
                c20 = 0
            else:
                c20 = float(row[120])
            c21 = "VATTax"
            c22 = row[119]
            c23 = ""
            c24 = row[62]
            c25 = row[166]
            c26 = row[42]
            c27 = row[43]
            c28 = row[44].replace('&&', '-')
            c29 = row[41]
            c30 = row[4]
            c31 = row[238]
            c32 = ""
            c33 = ""
            c34 = ""
            #tmp_line = '"'+c1+'","'+c2+'","'+c3+'","'+c4+'","'+c5+'","'+c6+'","'+c7+'","'+c8+'","'+c9+'","'+c10+'","'+c11+'","'+c12+'","'+c13+'","'+c14+'","'+c15+'","'+c16+'","'+c17+'","'+str(c18)+'","'+c19+'","'+c20+'","'+c21+'","'+c22+'","'+c23+'","'+c24+'","'+c25+'","'+c26+'","'+c27+'","'+c28+'","'+c29+'","'+c30+'","'+c31+'","'+c32+'","'+c33+'","'+c34+'"'
            #tmp_line = tmp_line.replace('""', '')
            #
            #testC = c15
            #
            myTempData = {
                        "InvoiceSource": c1,
                        "InvoicePCardInfo": c2,
                        "InvoicePCardReference": c3,
                        "PurchasingUnit": c4,
                        #"SupplierID": c5,
                        #"InvoiceType": c6,
                        #"InvoiceNumber": c7, # c'est la clé primaire pas besoin de repetition
                        "InvoiceDate": c8,
                        "InvoiceCurrencyCode": c9,
                        "InvoiceNetAmount": c19, # c18 au lieu de c10 pour commencer avec le premier montant
                        "InvoiceTaxAmount": c20, # c20 au lieu de c11 pour commencer avec le premier montant
                        "InvoiceGrossAmount": c12,
                        "InvoiceDescription": c13,
                        #"LineType": c14,
                        #"LineNumber": c15, # c'est la clé secondaire pas besoin de repetition
                        "LineDescription": c16,
                        "LineQuantity": c17,
                        "LineUnitPrice": c18,
                        "LineNetAmount": c19,
                        "LineTaxAmount": c20,
                        "LineTaxType": c21,
                        "LineTaxCode": c22,
                        "PCardMatchStatus": c23,
                        "LineCTA": c24,
                        #"LineGLAccount": c25,
                        "LineAccountingType": c26,
                        "LineAccountingCode": c27,
                        "LineSubAccountingCode": c28,
                        "LineGUD": c29,
                        "LineSerialNumber": c30,
                        "OrderNumber": c31,
                        "OrderLineNumber": c32,
                        "WarrantyNum": c33,
                        "ReceiptDate": c34,
                    }
            if c7 in myDict.keys():
                myDict[c7]["InvoiceNetAmount"] = myDict[c7]["InvoiceNetAmount"] + c19
                myDict[c7]["InvoiceTaxAmount"] = myDict[c7]["InvoiceTaxAmount"] + c20
                if c15 not in myDict[c7]['data']:
                    myDict[c7]['data'][c15] = myTempData
                #if "SupplierID" not in myDict[c7]['data'][c15] and row[162] == 'Company':
                #    myDict[c7]['data'][c15]["SupplierID"] = c5
                else:
                    #Il faut mettre a jour le LineUnitPrice et le LineNetAmount pour qu'il contient le dernier c18 et c19
                    myDict[c7]['data'][c15]["LineUnitPrice"] = c18
                    myDict[c7]['data'][c15]["LineNetAmount"] = c19                
            else:
                myDict[c7] = {
                    "InvoiceNetAmount": c19,
                    "InvoiceTaxAmount": c20,
                    "data": {
                        c15: myTempData
                    }
                }
            #Apres avoir analysé les fichiers output de concur avec notre code on a remarqué
            #Que la colonne 163 avait un impacte sur s'il faut mettre ou non le LineGLAccount et SupplierID
            if "LineGLAccount" not in myDict[c7]['data'][c15] and row[162] == 'Company':
                myDict[c7]['data'][c15]["LineGLAccount"] = c25
            else:
                if row[162] == 'Company':
                    myDict[c7]['data'][c15]["LineGLAccount"] = c25
                else:
                    myDict[c7]['data'][c15]["LineGLAccount"] = ""
            if "SupplierID" not in myDict[c7]['data'][c15] and row[162] == 'Company':
                myDict[c7]['data'][c15]["SupplierID"] = c5
            else:
                if row[162] == 'Company':
                    myDict[c7]['data'][c15]["SupplierID"] = c5
                else:
                    myDict[c7]['data'][c15]["SupplierID"] = ""
            
    static_line = '"InvoiceSource","InvoicePCardInfo","InvoicePCardReference","PurchasingUnit","SupplierID","InvoiceType","InvoiceNumber","InvoiceDate","InvoiceCurrencyCode","InvoiceNetAmount","InvoiceTaxAmount","InvoiceGrossAmount","InvoiceDescription","LineType","LineNumber","LineDescription","LineQuantity","LineUnitPrice","LineNetAmount","LineTaxAmount","LineTaxType","LineTaxCode","PCardMatchStatus","LineCTA","LineGLAccount","LineAccountingType","LineAccountingCode","LineSubAccountingCode","LineGUD","LineSerialNumber","OrderNumber","OrderLineNumber","WarrantyNum","ReceiptDate"'
    i = 0
    for invoice in myDict:
        myDict[invoice]["InvoiceNetAmount"] = str("{:.2f}".format(myDict[invoice]["InvoiceNetAmount"]))#.rstrip('0').rstrip('.')
        myDict[invoice]["InvoiceTaxAmount"] = str("{:.2f}".format(myDict[invoice]["InvoiceTaxAmount"]))
        for d in myDict[invoice]["data"]:
            if myDict[invoice]["data"][d]["InvoiceNetAmount"] >= 0:
                myDict[invoice]["data"][d]["InvoiceType"] = 'Invoice'
            else:
                myDict[invoice]["data"][d]["InvoiceType"] = 'CreditMemo'
            if myDict[invoice]["data"][d]["LineUnitPrice"] >= 0:
                myDict[invoice]["data"][d]["LineType"] = 'Debit'
            else:
                myDict[invoice]["data"][d]["LineType"] = 'Credit'
        
            myDict[invoice]["data"][d]["LineUnitPrice"] = str("{:.2f}".format(myDict[invoice]["data"][d]["LineUnitPrice"]))#.rstrip('0').rstrip('.')
            myDict[invoice]["data"][d]["LineNetAmount"] = str("{:.2f}".format(myDict[invoice]["data"][d]["LineNetAmount"]))#.rstrip('0').rstrip('.')        
            myDict[invoice]["data"][d]["LineTaxAmount"] = str("{:.2f}".format(myDict[invoice]["data"][d]["LineTaxAmount"])) 
        
    with open("myJson.json", "w") as fp:
        json.dump(myDict,fp, indent=4) 
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        output_file.write(static_line+'\n')            
        #for invoice in sorted(myDict, key=str):
        for invoice in myDict:
            #for d in sorted(myDict[invoice]["data"], key=str):
            for d in myDict[invoice]["data"]:
                l = '"'+myDict[invoice]["data"][d]["InvoiceSource"]+ '","' +myDict[invoice]["data"][d]["InvoicePCardInfo"]+ '","' +myDict[invoice]["data"][d]["InvoicePCardReference"]+ '","' +myDict[invoice]["data"][d]["PurchasingUnit"]+ '","' +myDict[invoice]["data"][d]["SupplierID"]+ '","' +myDict[invoice]["data"][d]["InvoiceType"]+ '","' +invoice+ '","' +myDict[invoice]["data"][d]["InvoiceDate"]+ '","' +myDict[invoice]["data"][d]["InvoiceCurrencyCode"]+ '","' +myDict[invoice]["InvoiceNetAmount"]+ '","' +myDict[invoice]["InvoiceTaxAmount"]+ '","' +myDict[invoice]["data"][d]["InvoiceGrossAmount"]+ '","' +myDict[invoice]["data"][d]["InvoiceDescription"]+ '","' +myDict[invoice]["data"][d]["LineType"]+ '","' +d+ '","' +myDict[invoice]["data"][d]["LineDescription"]+ '","' +myDict[invoice]["data"][d]["LineQuantity"]+ '","' +myDict[invoice]["data"][d]["LineUnitPrice"]+ '","' +myDict[invoice]["data"][d]["LineNetAmount"]+ '","' +myDict[invoice]["data"][d]["LineTaxAmount"]+ '","' +myDict[invoice]["data"][d]["LineTaxType"]+ '","' +myDict[invoice]["data"][d]["LineTaxCode"]+ '","' +myDict[invoice]["data"][d]["PCardMatchStatus"]+ '","' +myDict[invoice]["data"][d]["LineCTA"]+ '","' +myDict[invoice]["data"][d]["LineGLAccount"]+ '","' +myDict[invoice]["data"][d]["LineAccountingType"]+ '","' +myDict[invoice]["data"][d]["LineAccountingCode"]+ '","' +myDict[invoice]["data"][d]["LineSubAccountingCode"]+ '","' +myDict[invoice]["data"][d]["LineGUD"]+ '","' +myDict[invoice]["data"][d]["LineSerialNumber"]+ '","' +myDict[invoice]["data"][d]["OrderNumber"]+ '","' +myDict[invoice]["data"][d]["OrderLineNumber"]+ '","' +myDict[invoice]["data"][d]["WarrantyNum"]+ '","' +myDict[invoice]["data"][d]["ReceiptDate"]+'"'
                output_file.write(l+'\n')

def main(input_file , output_repo):
    #parent_dir = './OUTPUT/'
    # GET FILES LIST
    #bta_files_list = listdir('./INPUT/BTA')
    #clear()
    #print("\n\n_______ Execution " + str(datetime.now())+'_______\n')
    # CLEAR OUTPUT FOLDER
    #print("***** Netoyage du repertoire OUTPUT *****")
    #clear_output_repo()
    #print("\n***** Processing ****")
    #for file_name in bta_files_list:
        #print("- "+file_name)
        
    print("  - Remplacement du séparateur")
    print(input_file)
    with open(input_file, 'r', encoding=ENCODING) as file:
        data = file.read()
        data = data.replace('||', ';')
    with open(input_file, 'w', encoding=ENCODING) as file:
        file.write(data)
        
        # INIT
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%Y%m%d%H%M%S")
        #currentTime = 'TEST'
        ###
        #currentTime = 'TEST'
        ###
        # GET ENTITY FROM FILENAME
        #output_folder = parent_dir + entity + '/'
    #output_folder = parent_dir +  '/'
        #mkdir(output_folder)
        # WRITE DATA
        #print("  - Traitement de données")
    bta_file_name = 'extract_prod_SpringboardBTA_oktopay_' + currentTime +'_010101.csv'
    print(path.join(output_repo, bta_file_name))
    print(input_file)
    write_bta_data(path.join(output_repo, bta_file_name), input_file)

        # DIVISION PAR ENTITY (DERNIERE COLUMN)

if __name__=='__main__':
    main()