import csv
from os import listdir, path, mkdir, name
from datetime import datetime
from time import sleep
import os
from .config import ENCODING, COLUMN_1, THALES_DIR, GTS_DIR
from .importSpecs import spec_305

# Function to extract the Thales Entity from filename
def get_entity_from_filname(file_name, x):
    pathname, extension= path.splitext(file_name)
    splited_name = pathname.split('_')
    return splited_name[x]

# Print the static header for list file: "list_[ENTITE]_HCC_[DIR]_[currentTime].txt"
def list_hcc_file_header(output_file_name, entity, delete=False):
    if delete: last_column = 'Y'
    else: last_column = 'N'
    base = COLUMN_1 + ',' + COLUMN_1 + ',' + VAL_2 + ',' + entity
    line_1 = base + ',,,,,,,,,"'+entity+'",,,'+last_column
    line_2 = base + ',C,,,,,,,,"Cost Center",,,'+last_column
    line_3 = base + ',P,,,,,,,,"Project",,,'+last_column
    line_4 = base + ',A,,,,,,,,"A",,,'+last_column
    if delete : header_lines = line_2 + '\n' + line_3 + '\n' + line_4
    else: header_lines = line_1 + '\n' + line_2 + '\n' + line_3 + '\n' + line_4
    #return header_lines+'\n'
    with open(output_file_name, 'w', encoding=ENCODING) as output_file:
        output_file.write(header_lines+'\n')

#Print the static header for delete file: "list_[ENTITE]_DELETE_HCC_[DIR]_[currentTime].txt"
def delete_file_data(output_file_name, entity):
    #To have delete file data we use list file header with Y in the last column
    list_hcc_file_header(output_file_name, entity, delete=True)

# WRITE STATIC HEADER
def write_header(output_file_name):
    static_line = '100,0,SSO,UPDATE,EN,N,N'
    with open(output_file_name, 'w', encoding=ENCODING) as output_file:
        output_file.write(static_line+'\n')

# WRITE DATA
def write_305_data(output_file_name, input_file_name):
    lines = list()
    with open(input_file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=',')
        next(reader, None)
        for row in reader:
            #RECUPERER LES SPECS DU FICHIER SPECS
            myLine = spec_305(row)
            lines.append(myLine)
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        for l in lines:
            output_file.write(l+'\n')

def csv_to_dict(file_name, entity):
    dataDict = dict()
    operationalRespSet = list()
    with open(file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=',')
        next(reader, None)
        #parcourir les lignes du fichier
        for row in reader:
            #Verifier que la ligne n'est pas vide
            if not row :
                print("Erreur il existe une ligne vide : ligne "+ str(reader.line_num))
                exit()
            #Verifier que toutes les lignes contiennt la bonne Entity
            if not entity == row[1]:
                print("Erreur dans Entity de la ligne "+ str(reader.line_num))
                print("Remarque : Verifier l'emplacement de Entity dans le nom du fichier")
                exit()
            #Recuperer data selon les specs
            countryCode = row[0]
            accountingType = row[2]
            accountingCode = row[3].replace('-', '&&')
            accountingName = row[4].strip()
            #accountingDesc = row[5]
            secondaryAccountingCode = row[6].replace('-', '&&')
            secondaryAccountingName = row[7]
            #secondaryAccountingDesc = row[8]
            #validityEndDate = row[9]
            operationalResp = row[10]
            accountantRespon = row[11]
            #Enregistrer les OperationResp dans une ligne afin de l'utiliser pour le fichier write_305_adj_data
            if operationalResp not in operationalRespSet:
                operationalRespSet.append(operationalResp)

            #Créer un Dictionnaire tel que: 
            #La clé primaire c'est le accountingCode 
            #La liste des secondaryAccountingCode 
            #Chaque element de la liste contient: secondaryAccountingCode, secondaryAccountingName, operationalResp, accountantRespon

            if accountingCode in dataDict:
                dataDict[accountingCode]['secondary'].append({
                    'secondaryAccountingCode' : secondaryAccountingCode,
                    'secondaryAccountingName' : secondaryAccountingName,
                    'operationalResp' : operationalResp,
                    'accountantRespon' : accountantRespon,
                })
            else:
                if(secondaryAccountingCode != ''):
                    dataDict[accountingCode] = {
                        'accountingType': accountingType,
                        'accountingName': accountingName,
                        'secondary': [{
                            'secondaryAccountingCode' : secondaryAccountingCode,
                            'secondaryAccountingName' : secondaryAccountingName,
                            'operationalResp' : operationalResp,
                            'accountantRespon' : accountantRespon,
                        }]
                    }
                else:
                    dataDict[accountingCode] = {
                        'accountingType': accountingType,
                        'accountingName': accountingName,
                        'secondary': list()
                    }
        print("      - Toute les entity sont conforme")
    return dataDict, operationalRespSet
#La fonction qui crée le fichier List
#NB: il faut refactorer le code et la séparer dans une fonction ex:write_list_file()
def dict_to_csv(output_file_name, dataDict, entity):
    #Using a two part text so i don't have to use two loops
    headLinesPart = ""
    bottomLinesPart = ""

    for accountingCode in dataDict:
        #Une liste avec toutes les colonnes respectives
        tempLine = [COLUMN_1, COLUMN_1, VAL_2, entity, dataDict[accountingCode]['accountingType'], accountingCode, '', '', '', '', '', '', '\"'+dataDict[accountingCode]['accountingName']+'\"', '', '', 'N']
        #Joiner les elements avec , entre les 
        tempLine = ','.join(tempLine)
        headLinesPart += tempLine+'\n'
        #il existe le cas ou il n ya pas de Secondary alors il faut verifier et l'ajouter a tempLine
        if len(dataDict[accountingCode]['secondary']) == 0:
            tempLine = [COLUMN_1, COLUMN_1, VAL_2, entity, dataDict[accountingCode]['accountingType'], accountingCode, 'N/A', '', '', '', '', '', '\"'+'N/A'+'\"', '', '', 'N']
            tempLine = ','.join(tempLine)            
            #l'ajouter a bottonLines direct psq il n'aura pas la boucle for aprés    
            bottomLinesPart += tempLine+'\n'
        #Parcourir les secondary 
        for secondaryAccounting in dataDict[accountingCode]['secondary']:
            """if s['operationalResp'] == '':
                lastColumn = ''
            else:
                lastColumn = 'N'"""
            tempLine = [COLUMN_1, COLUMN_1, VAL_2, entity, dataDict[accountingCode]['accountingType'], accountingCode, secondaryAccounting['secondaryAccountingCode'], '', '', '', '', '', '\"'+secondaryAccounting['secondaryAccountingName']+'\"', '', '', 'N']
            tempLine = ','.join(tempLine)                
            bottomLinesPart += tempLine+'\n'
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        #Ecrire les données apres la fin de la premiere boucle for 
        output_file.write(headLinesPart+'\n')
        output_file.write(bottomLinesPart+'\n')
    # Fonction des données de 305_adj qui consiste au operationalResp
def write_305_adj_data(operationalResp_file_name, operationalRespSet):
    with open(operationalResp_file_name, 'a', encoding=ENCODING) as output_file:
        for o in operationalRespSet:
            if o == '':
                o = 'nothing'
            tempLine = "305,,,,"+o+",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Y,,,,,,,,,,,,,,,,,,,,,,,,Y,,,,,,,,,,,,,,,Y,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
            output_file.write(tempLine+'\n')
#Fonction de données 700, c'est las liste de EXP,REQ de chaque secondaryAccountingCode
def write_700_data(output_file_name, input_file_name):
    lines = list()
    with open(input_file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=',')
        next(reader, None)
        #lines = []
        #accountingNames = []
        #lastAccountingName = ''
        for row in reader:
            #Les scpecs ont été "deviné" en comparant les output Concur avec nos Output
            #countryCode = row[0]
            entity = row[1]
            accountingType = row[2]
            accountingCode = row[3].replace('-', '&&')
            secondaryAccountingCode = row[6].replace('-', '&&')
            operationalResp = row[10]
            if secondaryAccountingCode == '':
                secondaryAccountingCode = 'N/A'
            if operationalResp == '':
                operationalResp = 'null'

            exp_line = "700,EXP,"+ operationalResp +","+VAL_2+","+entity+","+accountingType+","+accountingCode+","+secondaryAccountingCode+",,,,,,,,"
            req_line = "700,REQ,"+ operationalResp +","+VAL_2+","+entity+","+accountingType+","+accountingCode+","+secondaryAccountingCode+",,,,,,,,"
            lines.append(exp_line)
            lines.append(req_line)
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        for l in lines:
            output_file.write(l+'\n')
#Fonction de données 350
def write_350_data(output_file_name, input_file_name, code):
    lines = list()
    with open(input_file_name, encoding=ENCODING) as listfile:
        reader = csv.reader(listfile, delimiter=',')
        next(reader, None)
        for row in reader:
            c5 = row[4]
            c12 = row[11].capitalize()
            if code == 'Thales':
                c22 = 'THAL'
            elif code == 'GTS':
                c22 = 'GTS'
            c23 = row[22]
            c42 = row[41]
            c60 = row[59]
            c138 = row[137]
            c139 = row[138]
            c142 = row[141].replace('+', '00')
            c144 = row[143]
            c145 = row[144]
            c147 = row[146]
            c148 = row[147]

            tmp_line = '"350","'+c5+'","'+c139+'",,,,,,"'+c60+'",,"'+c142+'",,,,,,,"'+c42+'-'+c12+'",,"'+c138+'",,,,,,"'+c144+'","'+c145+'",,"'+c147+'","'+c148+'",,,"Portrait SubUnit Name='+c42.upper()+'-C '+c138.upper()+'",,,,,"TRAINLINE_GUD='+c23+'",,,,,,,,,,,,,,,,,,,,"'+c42+c22+c5+'",,,,,,,,,'
            tmp_line = tmp_line.replace('""', '')

            lines.append(tmp_line)
    with open(output_file_name, 'a', encoding=ENCODING) as output_file:
        for l in lines:
            output_file.write(l+'\n')

def main(Env_SAECode, isTestOrProd, isDebutOrFin, parent_dir, accountingDataInputDir, employeeInputDir):
    logs = ""
    
    #Validations

    #Recuperer la liste des fichiers accountingData uploadé par user
    listOfAccountingDataFiles = listdir(accountingDataInputDir)
    #Recuperer le nom du fichier Employee uploadé par user
    listOfEmployeeFiles = listdir(employeeInputDir)

    #Vérifier que la requete contient bien au max 1 seul fichier employee 
    if len(listOfEmployeeFiles) > 1:
        print("Erreur : Il existe plusieurs fichiers Employee")
        exit()    

    #Récuperer les directory correspondant 
    if Env_SAECode == 'Thales':
        PROD_DIR, TEST_DIR = THALES_DIR
    elif Env_SAECode == 'GTS':
        PROD_DIR, TEST_DIR = GTS_DIR
    else:
        print("Aucune Entité Choisis")
        exit()
        
    global VAL_2

    VAL_2 = Env_SAECode

    # Verifier si c'est la prod ou test, pour choisir le directory

    print("*** TEST ou PRODUCTION ? ***")
    isTestOrProd = isTestOrProd
    if (isTestOrProd.upper() == 'T'):
        DIR = TEST_DIR
    elif (isTestOrProd.upper() == 'P'):
        DIR = PROD_DIR
    else:
        print("Erreur : Vous avez entrer une valeur differente de T ou P.")
        exit()

    # Savoir ou extraire l'Entity dans le nom du fichier début/fin
    print("*** Entity est au debut du nom du fichier ou a la fin ? ***")
    isDebutOrFin = isDebutOrFin
    if (isDebutOrFin.upper() == 'D'):
        x = 0
    elif (isDebutOrFin.upper() == 'F'):
        x = -1
    else:
        print("Erreur : Vous avez entrer une valeur differente de D ou F.")
        exit()
    
    print("\n\n_______ Execution " + str(datetime.now())+'_______\n')
    print("\n***** Processing ****")
    print("\n*** Fichiers List **")
    #Pour chaque fichier accoutingData: créer les fichiers et lancer les fonctions
    for file_name in listOfAccountingDataFiles:
        print(ENCODING)
        # INIT
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d%H%M%S")
        
        # GET ENTITE FROM FILENAME
        ENTITE = get_entity_from_filname(file_name, x)
        output_folder = os.path.join(parent_dir, ENTITE)
        mkdir(output_folder)
        
        # CREATE DELETE FILE
        delete_file_name = 'list_'+ ENTITE + '_DELETE_HCC_' + DIR + '_' + currentTime +'.txt'
        delete_file_path = os.path.join(output_folder, delete_file_name)
        delete_file_data(delete_file_path, ENTITE)

        # PREPARE ALL FILES HEADER
        # Create files names
        list_file_name = 'list_'+ ENTITE + '_HCC_' + DIR + '_' + currentTime +'.txt'
        employee_305_adj_file_name = 'employee_305_adj_'+ ENTITE +'_HCC_' + DIR + '_' + currentTime +'.txt'
        employee_700_file_name = 'employee_700_'+ ENTITE +'_HCC_' + DIR + '_' + currentTime +'.txt'

        # Create Files Paths
        list_file_path = os.path.join(output_folder, list_file_name)
        employee_305_adj_file_path = os.path.join(output_folder, employee_305_adj_file_name)
        employee_700_file_path = os.path.join(output_folder, employee_700_file_name)
        
        # Write Headers
        list_hcc_file_header(list_file_path, ENTITE)
        write_header(employee_305_adj_file_path)
        write_header(employee_700_file_path)

        # WRITE DATA
        dataDict, operationalRespSet = csv_to_dict(os.path.join(accountingDataInputDir,file_name), ENTITE)
        dict_to_csv(list_file_path, dataDict, ENTITE)

        write_305_adj_data(employee_305_adj_file_path, operationalRespSet)
        write_700_data(employee_700_file_path, os.path.join(accountingDataInputDir,file_name))

    
    #Pour chaque fichier accoutingData: créer les fichiers et lancer les fonctions
    #Un seul fichier Employee par traitement
    if len(listOfEmployeeFiles) == 1:
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y%m%d%H%M%S")
        print("\n*** Fichier Employee **")
        print("  - Creation des fichiers")
        print("    - Fichier 350")
        employee_350_file_name = 'employee_350_HCC_' + DIR + '_' + currentTime +'.txt'
        write_header(parent_dir +'/' + employee_350_file_name)
        print("    - Fichier 305")
        employee_305_file_name = 'employee_305_HCC_' + DIR + '_' + currentTime +'.txt'
        write_header(parent_dir+'/'  + employee_305_file_name)
        print("  - Traitement de données")
        print("    - Fichier 350")
        print(parent_dir+'/' + employee_350_file_name)
        print( listOfEmployeeFiles[0])
        write_350_data(parent_dir+'/' + employee_350_file_name, os.path.join(employeeInputDir,listOfEmployeeFiles[0]), VAL_2)
        print("    - Fichier 305")
        write_305_data(parent_dir+'/' + employee_305_file_name, os.path.join(employeeInputDir,listOfEmployeeFiles[0]))

if __name__=='__main__':
    main()