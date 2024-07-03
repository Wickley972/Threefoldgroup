import csv
from os import listdir, path, unlink, mkdir, system, name, remove, makedirs
import shutil
from datetime import datetime
from time import sleep
import json
from . import extractBySae
from .hccLibrary import clear

# GLOBAL VARIABLES
VAL_1 = 'Company Hierarchy'
#VAL_2 = 'Thales'
PRODUCTION_DIRECTORY = 'p06084973s3r'
TEST_DIRECTORY = 't060849864ks'
ENCODING = 'utf-8-sig'

CANADA_ENTITY = ['2016', '337', '558', '1209', '1241', '1719', '1694', '1316']

# GET DATA
def get_exp_data(output_file_name, input_file_name):
    myJson = {}
    invoiceSet = set()
    lines = list()
    i = 0
    with open(input_file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=';')
        next(reader, None)
        i = 0
        for row in reader:
            #On récuperre la data selon les specs
            """if row[186] != '5267':                
                continue
            else:
                print("i exist")"""
            """if row[166] == "GENCA": 
                if row[60] == '':
                    print(row[18])"""

            c1 = "SpringboardEXP"
            c2 = ""
            c3 = ""
            c4 = row[41] #fichiers 2023 ne marche pas avec colone 42
            #c4 = row[266]
            #c5 = row[164]#c5 = '107481R'#c5 = row[281]
            c7 = row[19]
            #c7 = str(int(row[149]))#c7 = row[186]#c8 = row[25]
            c9 = row[21]
            #c9 = row[177]
            c12 = float(row[31]) if row[31] != '' else 0.00
            c13 = "Related to " + row[19]
            c15 = row[60]
            c16 = row[5] + ' ' + row[6] # ca ne marche pas en 2023
            c17 = "1"
            c21 = "VATTax"
            c23 = ""
            c24 = row[62]
            c25 = row[166]
            c26 = row[42]
            c27 = row[43].replace('&&', '-').replace('N/A', '')
            c28 = row[44].replace('&&', '-').replace('N/A', '')
            c29 = row[41]
            c30 = row[4]
            c31 = row[19]                
            c34 = row[63]            
            #On a pas récuperer toutes les collones pour deux raison:
            # - Il existe des cas spéciaux par exemple : si l'entité est canadienne
            #   alors la colonne peut changer
            # - Il existe des collones qui sont le résultat d'un calcul de somme ou 
            #   une valeur qui dépent du total à la fin 
            if row[41] in CANADA_ENTITY:   
                # Il ne doit pas avoir de Genca dans les entiry de CANADA
                if row[166] == "GENCA":
                    print("Erreur GENCA dans CANADA")
                    exit()                
                if row[225] == '':
                    c20 = float(row[120]) if row[120] != '' else 0.0
                else:
                    c20 = float(row[230]) if row[230] != '' else 0.0
                c5 = row[281]   
                c8 = row[25]
                c33 = row[278]
                c32 = ""
                c22 = row[225]
                c18 = float(row[121]) if row[121] != '' else 0
                c19 = c18
                c11 = float(row[229]) if row[229] != '' else 0.0
                c10 = float(row[17]) if row[17] != '' else 0.0
            else:
                #Il existe deux cas 
                if row[166] == "GENCA":
                    #print(2)            
                    c4 = row[266]
                    c5 = row[4]
                    c18 = float(row[168])
                    if c7 == '': c7 = row[186] 
                    #c7 = row[19]
                    #c15 = row[186]                                                           
                    c8 = row[2] 
                    c9 = row[177]
                    c10 = c18
                    c12 = c18
                    
                    c13 = "Related to " + c7                    
                    c19 = c18
                    c20 = 0.00
                    c21 = ''
                    #c22 = row[119]
                    c22 = ''
                    if row[62] == "":
                        c24 = 'Cash Advance'
                    else:
                        c24 = row[62]
                    #myTempData["LineGLAccount"] = c25 je peux pas l'enlever comme ca il faut l'ajouter dans tempData
                    c29 = row[266]
                    #c29 = row[41]
                    c31 = c7
                    c32 = row[186]
                    c33 = ""
                    c34 = row[185]  
                    """elif row[166] == "GENCA" and row[60] == '' :

                    print(3)
                    #print('ligne GENCA sans LINENUMBER')
                    #print('*'+row[19]+'*')
                    continue
                    """
                else:
                    #print(4)
                    c5 = row[4]
                    #c8 = row[2]
                    c8 = row[25]
                    c33 = ""
                    c32 = ""#row[286] #erreu out of range
                    c22 = row[119]
                    c20 = float(row[247]) if row[247] != '' else 0.0 # Specs David row[120]; ma spec row[247]; 
                    c18 = float(row[17]) if row[17] != '' else 0
                    c19 = c18
            """if c7 != '5267':                
                continue
            else:
                print("i exist")
                exit()"""
            if c7 == '' or c15 == '':
                print("Warning: InvoiceNumber vide")
            if c15 == '':
                print("Warning: LineNumber vide")
            myTempData = {
                        "InvoiceSource": c1,
                        "InvoicePCardInfo": c2,
                        "InvoicePCardReference": c3,
                        "PurchasingUnit": c4,
                        "SupplierID": c5,
                        #"InvoiceType": c6,
                        "InvoiceNumber": c7, # c'est la clé primaire pas besoin de repetition
                        "InvoiceDate": c8,
                        "InvoiceCurrencyCode": c9,
                        "InvoiceNetAmount": c18, # c18 au lieu de c10 pour commencer avec le premier montant/ ca peut poser probleme dans les entites non canadiennes
                        "InvoiceTaxAmount": c20, # c20 au lieu de c11 pour commencer avec le premier montant
                        "InvoiceGrossAmount": c12,
                        "InvoiceDescription": c13,
                        #"LineType": c14,
                        "LineNumber": c15, # c'est la clé secondaire pas besoin de repetition
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
            #print("MyTempData:")
            #print(myTempData)
            #print()
            if row[166] == "GENCA":
                myTempData["LineGLAccount"] = c25
                #print("GENCA")
            #exit()
            if row[41] not in CANADA_ENTITY: # tester avec c0* aulieu de row[41] pour voir si ca ameliore la sortie
                #print("Not canada")
                #continue
                #Traiter le cas des (Emplyee GBP)
                if c7 in myJson.keys():
                    if c25 == 'GENCA': #DEMANDE D'AVANCE
                        myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c18
                        myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c20
                        myJson[c7]["InvoiceGrossAmount"] = myJson[c7]["InvoiceGrossAmount"] + c12
                        if c15 not in myJson[c7]: # faire une tabulation et voir le resultat
                            myJson[c7][c15] = {
                                'GENCA': myTempData
                            }
                        else:
                            if "GENCA" in myJson[c7][c15]:
                                print("Mmm GENCA deja dans [c7][c15]")
                            else:
                                myJson[c7][c15]["GENCA"] = myTempData
                        continue #il ne faut pas que ca rentre dans les if suivants
                    
                    if row[225] == '': # voir si je mets elif ou if (si je calcule ou non)                        
                        myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c18
                        myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c20
                        #myJson[c7]["InvoiceGrossAmount"] = myJson[c7]["InvoiceGrossAmount"] + c12
                        if c15 not in myJson[c7]: # faire une tabulation et voir le resultat
                            myJson[c7][c15] = {
                                'data': myTempData
                            }
                        else:
                            myJson[c7][c15]['data']["LineUnitPrice"] = c18
                            myJson[c7][c15]['data']["LineNetAmount"] = c19
                    elif row[225] == 'VAT':
                        pass
                    elif row[225] == 'Employee':
                        pass
                    else:
                        pass

                else:#si le c7 (invoiceNumber) n'existe pas alors il faut créer la data
                    if c25 == 'GENCA': #DEMANDE D'AVANCE                        
                        myJson[c7] = {
                            "PurchasingUnit": c4,
                            "InvoiceNetAmount": c18,
                            "InvoiceTaxAmount": c20,
                            "InvoiceGrossAmount": c12,
                            c15: {
                                "GENCA": myTempData,                                
                            },
                        }
                    elif row[225] == '':                        
                        myJson[c7] = {
                            "PurchasingUnit": c4,
                            "InvoiceNetAmount": c18,
                            "InvoiceTaxAmount": c20,
                            "InvoiceGrossAmount": c12,
                            c15: {                                
                                "data": myTempData
                            },                         
                        }
                    else:
                        pass # cas non defini
                if c7 in myJson and c15 in myJson[c7] and 'data' in myJson[c7][c15] and "LineGLAccount" not in myJson[c7][c15]['data'] and row[225] == '' :
                    myJson[c7][c15]['data']["LineGLAccount"] = c25
                #else:
                 #   myJson[c7]['data'][c15]["LineGLAccount"] = c25 # j'ai ajouté LineGLAccount direct dans myTempData 
            else:                      
                #Les Entités CANADA
                if c25 == 'GENCA':
                        print('Erreur GENCA dans CANADA')
                myTempData["LineGLAccount"] = c25
                if c7 in myJson.keys():
                    #invoice number existe deja
                    #print("Invoice exist")                    
                    if c15 not in myJson[c7]:
                        if row[225] == '':
                            #invoice exist, linenumber not exist, expence line
                            myJson[c7][c15] = {
                                'data': myTempData
                            }   
                            myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10                            
                            myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11
                        elif row[225] == 'VAT':
                            print("VAT")
                            pass
                        elif row[225] == 'Employee':
                            print("Employee")
                            pass
                        else:                
                            #invoice exist, linenumber not exist, tax line            
                            vat_list = list()         
                            vat_list.append(myTempData)
                            myJson[c7][c15] = {
                                'tax': vat_list
                            }
                            myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10
                            myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11 
                    else:                        
                        if row[225] == '':
                            if 'data' not in myJson[c7][c15]:
                                
                                #invoice exist, linenumber exist, expence line et data not exist
                                myJson[c7][c15]['data'] = myTempData   
                                myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10                            
                                myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11
                            else:                                
                                #invoice exist, linenumber exist, expence line et data exist
                                myJson[c7][c15]['data']["LineUnitPrice"] = c18
                                # si il ya une erreur ici, càd qu'il ya une un linenumber sans expence 
                                myJson[c7][c15]['data']["LineNetAmount"] = c19
                                myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10
                                myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11
                        elif row[225] == 'VAT':
                            print("VAT")
                            pass
                        elif row[225] == 'Employee':
                            print("Employee")
                            pass
                        else:                            
                            if 'tax' not in myJson[c7][c15]:
                                #invoice exist, linenumber exist, tax line et tax not exist
                                vat_list = list()         
                                vat_list.append(myTempData)
                                myJson[c7][c15]['tax'] = vat_list

                                myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10
                                myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11
                            else:
                                #invoice exist, linenumber exist, tax line et tax exist           
                                myJson[c7][c15]['tax'].append(myTempData)    
                                myJson[c7]["InvoiceNetAmount"] = myJson[c7]["InvoiceNetAmount"] + c10
                                myJson[c7]["InvoiceTaxAmount"] = myJson[c7]["InvoiceTaxAmount"] + c11                                    
                else:                    
                    #print('Invoice not exist')
                    ##invoice number n'existe pas
                    #print("225 : "+row[225])
                    if row[225] == '':                        
                        # invoice n'existe pas, et c'est expence line
                        myJson[c7] = {
                            "PurchasingUnit": c4,
                            "InvoiceNetAmount": c10,
                            "InvoiceTaxAmount": c11,
                            "InvoiceGrossAmount": c12,
                            c15: {
                                "data": myTempData,
                                #"tax": {}
                            },
                        }                        
                    elif row[225] == 'VAT':
                        pass
                    elif row[225] == 'Employee':
                        pass
                    else:                        
                        # invoice n'existe pas, et c'est une taxe
                        vat_list = list()         
                        vat_list.append(myTempData)
                        myJson[c7] = {
                            "PurchasingUnit": c4,
                            "InvoiceNetAmount": c10, # a verifier si je dois le mettre 0 ou non
                            "InvoiceTaxAmount": c11, # a verifier si je dois le mettre 0 ou non
                            "InvoiceGrossAmount": c12,
                            c15: {
                                #"data": {},
                                "tax": vat_list # verifier si ca sera avec lineunitprice = 0 et lineNetAmount = 0                                
                            },
                        }        
    print(i)
    return myJson

def writeData(myJson, output_file_name):
    static_line = '"InvoiceSource","InvoicePCardInfo","InvoicePCardReference","PurchasingUnit","SupplierID","InvoiceType","InvoiceNumber","InvoiceDate","InvoiceCurrencyCode","InvoiceNetAmount","InvoiceTaxAmount","InvoiceGrossAmount","InvoiceDescription","LineType","LineNumber","LineDescription","LineQuantity","LineUnitPrice","LineNetAmount","LineTaxAmount","LineTaxType","LineTaxCode","PCardMatchStatus","LineCTA","LineGLAccount","LineAccountingType","LineAccountingCode","LineSubAccountingCode","LineGUD","LineSerialNumber","OrderNumber","OrderLineNumber","WarrantyNum","ReceiptDate"'
    i = 0
    for invoice in myJson:
        if round(myJson[invoice]["InvoiceGrossAmount"], 2) >= 0:               
            myJson[invoice]["InvoiceType"] = 'Invoice'
        else:            
            myJson[invoice]["InvoiceType"] = 'CreditMemo'
        for d in myJson[invoice]:         
            if d in ["PurchasingUnit", "InvoiceNetAmount", "InvoiceTaxAmount", "InvoiceGrossAmount"]:
                continue
            if 'data' in myJson[invoice][d]:
                if myJson[invoice][d]["data"]["LineUnitPrice"] >= 0:
                    myJson[invoice][d]["data"]["LineType"] = 'Debit'
                else:
                    myJson[invoice][d]["data"]["LineType"] = 'Credit'
            
                myJson[invoice][d]["data"]["LineUnitPrice"] = str("{:.2f}".format(myJson[invoice][d]["data"]["LineUnitPrice"]))#.rstrip('0').rstrip('.')
                myJson[invoice][d]["data"]["LineNetAmount"] = str("{:.2f}".format(myJson[invoice][d]["data"]["LineNetAmount"]))#.rstrip('0').rstrip('.')                    
                myJson[invoice][d]["data"]["LineTaxAmount"] = str("{:.2f}".format(myJson[invoice][d]["data"]["LineTaxAmount"]))
                myJson[invoice][d]["data"]["InvoiceGrossAmount"] = str("{:.2f}".format(myJson[invoice][d]["data"]["InvoiceGrossAmount"]))

            if 'GENCA' in myJson[invoice][d]:  #im here                
                #if myJson[invoice]["GENCA"][d]["InvoiceNetAmount"] >= 0:
                if myJson[invoice][d]["GENCA"]["LineUnitPrice"] >= 0:
                    myJson[invoice][d]["GENCA"]["LineType"] = 'Debit'
                else:
                    myJson[invoice][d]["GENCA"]["LineType"] = 'Credit'
            
                myJson[invoice][d]["GENCA"]["LineUnitPrice"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["LineUnitPrice"]))#.rstrip('0').rstrip('.')
                myJson[invoice][d]["GENCA"]["LineNetAmount"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["LineNetAmount"]))#.rstrip('0').rstrip('.')        
                myJson[invoice][d]["GENCA"]["LineTaxAmount"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["LineTaxAmount"]))
                myJson[invoice][d]["GENCA"]["InvoiceNetAmount"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["InvoiceNetAmount"]))
                myJson[invoice][d]["GENCA"]["InvoiceTaxAmount"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["InvoiceTaxAmount"]))
                myJson[invoice][d]["GENCA"]["InvoiceGrossAmount"] = str("{:.2f}".format(myJson[invoice][d]["GENCA"]["InvoiceGrossAmount"]))
            
        if myJson[invoice]['PurchasingUnit'] in CANADA_ENTITY:
            for t in myJson[invoice]:
                if t in ["PurchasingUnit", "InvoiceNetAmount", "InvoiceTaxAmount", "InvoiceGrossAmount"] or 'tax' not in myJson[invoice][t]:
                    continue
                for d in myJson[invoice][t]["tax"]:                                    
                    if d["LineUnitPrice"] >= 0:
                        d["LineType"] = 'Debit'
                    else:
                        d["LineType"] = 'Credit'
                
                    d["LineUnitPrice"] = str("{:.2f}".format(d["LineUnitPrice"]))#.rstrip('0').rstrip('.')
                    d["LineNetAmount"] = str("{:.2f}".format(d["LineNetAmount"]))#.rstrip('0').rstrip('.')        
                    d["LineTaxAmount"] = str("{:.2f}".format(d["LineTaxAmount"]))
                    d["InvoiceGrossAmount"] = str("{:.2f}".format(d["InvoiceGrossAmount"]))
        
                
        myJson[invoice]["InvoiceNetAmount"] = str("{:.2f}".format(myJson[invoice]["InvoiceNetAmount"]))#.rstrip('0').rstrip('.')
        myJson[invoice]["InvoiceTaxAmount"] = str("{:.2f}".format(myJson[invoice]["InvoiceTaxAmount"]))
        if "InvoiceGrossAmount" in myJson[invoice]:
            myJson[invoice]["InvoiceGrossAmount"] = str("{:.2f}".format(myJson[invoice]["InvoiceGrossAmount"]))
        
    #with open("myJson.json", "w") as fp:
    #    json.dump(myJson,fp, indent=4) 
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        output_file.write(static_line+'\n')            
        #for invoice in sorted(myJson, key=str):
        for invoice in myJson:            
            #for d in sorted(myJson[invoice]["data"], key=str):
            for d in myJson[invoice]:
                if d in ["PurchasingUnit", "InvoiceNetAmount", "InvoiceTaxAmount", "InvoiceGrossAmount"]:
                    continue
                if 'data' in myJson[invoice][d]:
                    l = '"'+myJson[invoice][d]["data"]["InvoiceSource"]+ '","' +myJson[invoice][d]["data"]["InvoicePCardInfo"]+ '","' +myJson[invoice][d]["data"]["InvoicePCardReference"]+ '","' +myJson[invoice][d]["data"]["PurchasingUnit"]+ '","' +myJson[invoice][d]["data"]["SupplierID"]+ '","' +myJson[invoice]["InvoiceType"]+ '","' +invoice+ '","' +myJson[invoice][d]["data"]["InvoiceDate"]+ '","' +myJson[invoice][d]["data"]["InvoiceCurrencyCode"]+ '","' +myJson[invoice]["InvoiceNetAmount"]+ '","' +myJson[invoice]["InvoiceTaxAmount"]+ '","' +myJson[invoice]["InvoiceGrossAmount"]+ '","' +myJson[invoice][d]["data"]["InvoiceDescription"]+ '","' +myJson[invoice][d]["data"]["LineType"]+ '","' +d+ '","' +myJson[invoice][d]["data"]["LineDescription"]+ '","' +myJson[invoice][d]["data"]["LineQuantity"]+ '","' +myJson[invoice][d]["data"]["LineUnitPrice"]+ '","' +myJson[invoice][d]["data"]["LineNetAmount"]+ '","' +myJson[invoice][d]["data"]["LineTaxAmount"]+ '","' +myJson[invoice][d]["data"]["LineTaxType"]+ '","' +myJson[invoice][d]["data"]["LineTaxCode"]+ '","' +myJson[invoice][d]["data"]["PCardMatchStatus"]+ '","' +myJson[invoice][d]["data"]["LineCTA"]+ '","' +myJson[invoice][d]["data"]["LineGLAccount"]+ '","' +myJson[invoice][d]["data"]["LineAccountingType"]+ '","' +myJson[invoice][d]["data"]["LineAccountingCode"]+ '","' +myJson[invoice][d]["data"]["LineSubAccountingCode"]+ '","' +myJson[invoice][d]["data"]["LineGUD"]+ '","' +myJson[invoice][d]["data"]["LineSerialNumber"]+ '","' +myJson[invoice][d]["data"]["OrderNumber"]+ '","' +myJson[invoice][d]["data"]["OrderLineNumber"]+ '","' +myJson[invoice][d]["data"]["WarrantyNum"]+ '","' +myJson[invoice][d]["data"]["ReceiptDate"]+'"'
                    output_file.write(l+'\n')
                if "GENCA" in myJson[invoice][d]:                    
                    l = '"'+myJson[invoice][d]["GENCA"]["InvoiceSource"]+ '","' +myJson[invoice][d]["GENCA"]["InvoicePCardInfo"]+ '","' +myJson[invoice][d]["GENCA"]["InvoicePCardReference"]+ '","' +myJson[invoice][d]["GENCA"]["PurchasingUnit"]+ '","' +myJson[invoice][d]["GENCA"]["SupplierID"]+ '","' +myJson[invoice]["InvoiceType"]+ '","' +invoice+ '","' +myJson[invoice][d]["GENCA"]["InvoiceDate"]+ '","' +myJson[invoice][d]["GENCA"]["InvoiceCurrencyCode"]+ '","' +myJson[invoice]["InvoiceNetAmount"]+ '","' +myJson[invoice]["InvoiceTaxAmount"]+ '","' +myJson[invoice]["InvoiceGrossAmount"]+ '","' +myJson[invoice][d]["GENCA"]["InvoiceDescription"]+ '","' +myJson[invoice][d]["GENCA"]["LineType"]+ '","' +d+ '","' +myJson[invoice][d]["GENCA"]["LineDescription"]+ '","' +myJson[invoice][d]["GENCA"]["LineQuantity"]+ '","' +myJson[invoice][d]["GENCA"]["LineUnitPrice"]+ '","' +myJson[invoice][d]["GENCA"]["LineNetAmount"]+ '","' +myJson[invoice][d]["GENCA"]["LineTaxAmount"]+ '","' +myJson[invoice][d]["GENCA"]["LineTaxType"]+ '","' +myJson[invoice][d]["GENCA"]["LineTaxCode"]+ '","' +myJson[invoice][d]["GENCA"]["PCardMatchStatus"]+ '","' +myJson[invoice][d]["GENCA"]["LineCTA"]+ '","' +myJson[invoice][d]["GENCA"]["LineGLAccount"]+ '","' +myJson[invoice][d]["GENCA"]["LineAccountingType"]+ '","' +myJson[invoice][d]["GENCA"]["LineAccountingCode"]+ '","' +myJson[invoice][d]["GENCA"]["LineSubAccountingCode"]+ '","' +myJson[invoice][d]["GENCA"]["LineGUD"]+ '","' +myJson[invoice][d]["GENCA"]["LineSerialNumber"]+ '","' +myJson[invoice][d]["GENCA"]["OrderNumber"]+ '","' +myJson[invoice][d]["GENCA"]["OrderLineNumber"]+ '","' +myJson[invoice][d]["GENCA"]["WarrantyNum"]+ '","' +myJson[invoice][d]["GENCA"]["ReceiptDate"]+'"'
                    output_file.write(l+'\n')
            if myJson[invoice]['PurchasingUnit'] in CANADA_ENTITY:
                for t in myJson[invoice]:
                    if t in ["PurchasingUnit", "InvoiceNetAmount", "InvoiceTaxAmount", "InvoiceGrossAmount"] or 'tax' not in myJson[invoice][t]:
                        continue
                    for v in myJson[invoice][t]["tax"]:
                        l = '"'+v["InvoiceSource"]+ '","' +v["InvoicePCardInfo"]+ '","' +v["InvoicePCardReference"]+ '","' +v["PurchasingUnit"]+ '","' +v["SupplierID"]+ '","' +myJson[invoice]["InvoiceType"]+ '","' +invoice+ '","' +v["InvoiceDate"]+ '","' +v["InvoiceCurrencyCode"]+ '","' +myJson[invoice]["InvoiceNetAmount"]+ '","' +myJson[invoice]["InvoiceTaxAmount"]+ '","' +myJson[invoice]["InvoiceGrossAmount"]+ '","' +v["InvoiceDescription"]+ '","' +v["LineType"]+ '","' +t+ '","' +v["LineDescription"]+ '","' +v["LineQuantity"]+ '","' +str(v["LineUnitPrice"])+ '","' +str(v["LineNetAmount"])+ '","' +str(v["LineTaxAmount"])+ '","' +v["LineTaxType"]+ '","' +v["LineTaxCode"]+ '","' +v["PCardMatchStatus"]+ '","' +v["LineCTA"]+ '","' +v["LineGLAccount"]+ '","' +v["LineAccountingType"]+ '","' +v["LineAccountingCode"]+ '","' +v["LineSubAccountingCode"]+ '","' +v["LineGUD"]+ '","' +v["LineSerialNumber"]+ '","' +v["OrderNumber"]+ '","' +v["OrderLineNumber"]+ '","' +v["WarrantyNum"]+ '","' +v["ReceiptDate"]+'"'
                        output_file.write(l+'\n')
            

# Constants
#INPUT_DIR = './INPUT/EXP'
#OUTPUT_DIR = './OUTPUT/'

def main(input_file , output_repo):
    # Clear output folder
    #clear_output_dir()

    # Get files list
    #exp_files_list = listdir(INPUT_DIR)

    # Process files
    #for file_name in exp_files_list:
    print(f"Processing file: {input_file}")
    replace_separators(input_file)
    exp_file_path, exp_file_name = write_output_file(input_file, output_repo)
    extractBySae.extract(output_repo, exp_file_path, 'LineGUD', exp_file_name)

def replace_separators(filename):
    print(1)
    # Replace separators in file contents
    with open(filename, 'r', encoding=ENCODING) as file:
        data = file.read()
        data = data.replace('||', ';')
        #data = data.replace('|', ';')
    with open(filename, 'w', encoding=ENCODING) as file:
        file.write(data)
    

def write_output_file(filename, output_repo):
    print(3)
    # Generate output filename based on current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    #current_time = "test"
    exp_file_name = f'extract_SpringboardEXP_oktopay_{current_time}.csv'
    output_path = path.join(output_repo, exp_file_name)
    print(3)
    # Write modified data to output file
    myJson = get_exp_data(output_path, filename)
    writeData(myJson, output_path)
    print(4)
    return output_path, exp_file_name

"""def clear_output_dir():
    # Clear output directory if it exists
    if path.exists(OUTPUT_DIR):
        for file_name in listdir(OUTPUT_DIR):
            remove(f'{OUTPUT_DIR}/{file_name}')
    else:
        makedirs(OUTPUT_DIR)"""


if __name__=='__main__':
    main()