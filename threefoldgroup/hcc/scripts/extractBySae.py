import csv
from os import path

ENCODING = 'utf-8-sig'

def extract(output_dir, input_file, column_name, exp_file_name):
    print(input_file, column_name)
    # specify the column to divide by and the input/output file names
    #column_name = 'LineGUD'
    #input_file = 'input.csv'
    #output_prefix = 'output_'

    # create a dictionary to store the data for each unique column value
    data = {}

    # open the input file and read the data
    with open(input_file, 'r', encoding=ENCODING) as f:
        print(input_file)
        reader = csv.DictReader(f)
        for row in reader:
            # get the column value for this row
            column_value = row[column_name]
            
            # initialize an empty list for this column value if it doesn't already exist
            if column_value not in data:
                data[column_value] = []
            
            # add the row to the list for this column value
            data[column_value].append(row)

    # write the data to separate output files for each column value
    for column_value, rows in data.items():
        #output_file = output_prefix + column_value + '.csv'
        output_file = column_value + '_' + exp_file_name
        output_file = path.join(output_dir, output_file)
        with open(output_file, 'w', encoding=ENCODING, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=reader.fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

def main():
    output_dir = './CompareTo/'
    input_file =  'extract_prod_SpringboardEXP_oktopay_HCC_p06084973s3r-01_20230207141447.csv'
    column_name = 'LineGUD'
    extract(output_dir, input_file, column_name)

if __name__ == '__main__':
    main()