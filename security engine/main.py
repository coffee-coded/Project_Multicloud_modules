import sys
import json
import csv
from classes.google_cloud import gcp_dlp
from tqdm import tqdm, trange
import os

if len(sys.argv) == 2:

    # Json file from user
    data = {}
    with open(sys.argv[-1]) as file:
        data = json.load(file)

    # Setting up credentials of service account to access GCP
    os.system('export GOOGLE_APPLICATION_CREDENTIALS=' +
              data['project']['config_name'])
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = data['project']['config_name']
    print('Credentials from environ: {}'.format(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))

    # Project ID and location ID setting up
    project_id = data['project']['project_id']
    location_id = 'global'
    key_id = data['project']['key_id']
    key_ring_id = data['project']['key_ring_id']
    # Initialing object of GCP's DLP from classes.google_cloud

    dlp = gcp_dlp(project_id, location_id, key_id, key_ring_id)
    count = 0
    columns = []
    output = []
    row = []
    print('\nTransforming csv from ', os.path.basename(
        data['project']['csv_path']))
    for column in data['methods']:
        columns.append(column['column'])
    csv_lines = 0
    with open(data['project']["csv_path"], mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_len = len(list(csv_file)) - 1
    with open(data['project']["csv_path"], mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        with tqdm(total=100) as progressbar:
            for i in csv_reader:
                for j in range(len(columns)):
                    # print(i[columns[j]], data["methods"][j]["method"], end='   ')
                    count += 1
                    if data["methods"][j]["method"] == "None":
                        row.append(i[columns[j]])
                    elif data["methods"][j]["method"] == "Replace":
                        row.append(dlp.deidentify_with_replace(
                            input_str=i[columns[j]], info_types=data["methods"][j]["info_types"], replacement_str=data["methods"][j]["replacement_str"]))
                    elif data["methods"][j]["method"] == "Masking":
                        row.append(dlp.deidentify_with_mask(
                            input_str=i[columns[j]], info_types=data["methods"][j]["info_types"], masking_character=data["methods"][j]["masking_character"], number_to_mask=int(data["methods"][j]["number_to_mask"])))
                    elif data["methods"][j]["method"] == "Redact":
                        row.append(dlp.deidentify_with_redact(
                            input_str=i[columns[j]], info_types=data["methods"][j]["info_types"]))
                    elif data["methods"][j]["method"] == "FPE":
                        row.append(dlp.deidentify_with_fpe(
                            input_str=i[columns[j]], info_types=data["methods"][j]["info_types"], alphabet=data["methods"][j]["alphabet"], name=os.path.basename(
                                data['project']['csv_path']), key_id=key_id, key_ring_id=key_ring_id))
                output.append(row)
                row = []
                progressbar.update(100//csv_len)
    print(dlp)
    dlp.export_wrap_fn(os.path.basename(data['project']['csv_path']))
    out_file = os.path.basename(data['project']['csv_path'])
    out_file = out_file.split('.')
    out_file[0] += '_protected'
    out_file = '.'.join(out_file)
    print(f'Writing to {out_file}')
    with open(out_file, mode='w', encoding='utf-8') as csv_file:
        # csv_reader = csv.reader(csv_file, delimiter=',')
        # for row in csv_reader:
        #     print(row)
        writer = csv.writer(csv_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([column for column in columns])
        with tqdm(total=100) as progressbar:
            for i in output:
                writer.writerow(i)
                progressbar.update(100//len(output))
    # print(dlp)
    print(f'Count : {count}')
else:
    print('ERROR: JSON File missing.')
    print('To use the command properly, Type: python3 main.py <test.json>')
