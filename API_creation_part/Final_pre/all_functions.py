import requests
import pandas as pd
import zipfile
import io
import json
import links

def get_headers(referer):      
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.5',
        'cookie': 'at_check=true; AMCVS_1E7B833554B8360D0A4C98A5%40AdobeOrg=1; ai_user=mgday|2024-08-29T18:31:28.154Z; TS0154aeeb=01689d3836a514a17473abf0d6f5ad5772e6e7bdb10ccf16fdf7f852744e393965cb477533a1c076dc911f6898034a512bedbeafdf52b860296ee44b6419fb896179cd3b33; uvts=3bcc00f2-9137-4ec1-4bca-553dfd2f7e7e; uvts=3bcc00f2-9137-4ec1-4bca-553dfd2f7e7e; mbox=session^#4559eaac119848209945fe3090653f3a^#1724992383; AMCV_1E7B833554B8360D0A4C98A5%40AdobeOrg=179643557%7CMCIDTS%7C19965%7CMCMID%7C92218247660966655474435029970291211097%7CMCAID%7CNONE%7CMCOPTOUT-1724997736s%7CNONE%7CvVersion%7C5.5.0; ai_session=m1RlN|1724990527962|1724991411759; __cf_bm=y83JOBDCN11I32uIXEpt4dB25styFQLMct9j.DPZ9og-1724994534-1.0.1.1-gVkJt16acGz6nFpt_hjk8ndMYxAqOzSYJU3TQx37V_WrFXbT99wj1ak.mA.8sQR44MZBvkIJrRxSMzi7TmlUEA; search.ApplicationGatewayAffinity=fb51af8e6aa3233ad17b87332ccf2d86; search.ApplicationGatewayAffinityCORS=fb51af8e6aa3233ad17b87332ccf2d86',
        'priority': 'u=1, i',
        'referer': referer,
        'request-id': '|19b787b0e2194db9a608a6a3914c62f8.28c92ff7311c4fd7',
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    return headers

def Get_list_of_projects(country_name, country_short_name):
    headers = get_headers(f'https://data.worldbank.org/country/{country_name}?view=chart')
        
    url = links.get_url('list_of_projects', country_short_name)
    response = requests.get(url, headers=headers)
    dta = response.json()
    length = dta.get("total", 8)  
    print("Total pages of projects are ", length)
    curnt_project_fecthing = 9 #if not present but i am taking 9 so that it will work fast api 
    url = f"https://search.worldbank.org/api/v2/projectsarchives?format=json&order=desc&fct=countryname&rows={curnt_project_fecthing}&apilang=en&os=0&srt=docdt"
    
    response = requests.get(url, headers=headers)
    return length, response.json()

def sectors(sort_name):
    url = links.get_url('sectors', sort_name)
    payload = {}
    headers = get_headers(f'https://projects.worldbank.org/')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


def sectors_information(full_name, sort_name):
    url = links.get_url('sectors_information', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()






def Indicator_data(sort_name, full_name):
    url = links.get_url('indicator', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def indicator_meta_data(sort_name):  
    url = links.get_url('indicator_meta_data', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/indicator/SP.POP.TOTL?locations={sort_name}')
    response = requests.request("GET", url, headers=headers, data=payload)  
    return response.json()

def country_indecator_groups_data(full_name):
    url = "https://data.worldbank.org/model.json?paths=%5B%5B%22countryIndicatorGroups%22%5D%5D&method=get"
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def country_information(sort_name, full_name):
    url = links.get_url('country_information', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def projects_and_operations_data(sort_name, full_name):
    url = links.get_url('projects_and_operations_data', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

def other_indecators_data(sort_name, full_name):
    url = links.get_url('other_indecators_data', sort_name)
    payload = {}
    headers = get_headers(f'https://data.worldbank.org/country/{full_name}?view=chart')
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()

payload = {}

def Get_countrys_name_and_short_name():
    url = "https://data.worldbank.org/model.json?paths=%5B%5B%22lists%22%2C%22countries%22%2C%22en%22%5D%5D&method=get"
    payload = {}
    headers = get_headers('https://data.worldbank.org/country')
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    country_data = [item for item in data["jsonGraph"]["lists"]["countries"]["en"]["value"] if item.get('locationType') == 'country']
    return [(m['name'], m['id']) for m in country_data]

def download_files(sort_name):
    url = f"https://api.worldbank.org/v2/en/country/{sort_name}?downloadformat=csv"
    response = requests.get(url)
    if response.status_code == 200:
        zip_file = io.BytesIO(response.content)
        with zipfile.ZipFile(zip_file) as z:
            csv_filenames = [f for f in z.namelist() if f.endswith('.csv')]
            all_data = []
            for csv_filename in csv_filenames:
                with z.open(csv_filename) as csv_file:
                    try:
                        df = pd.read_csv(csv_file, skiprows=4, encoding='latin-1')
                        if df.empty:
                            print(f"Skipping empty file: {csv_filename}")
                            continue
                        df = df.iloc[:, :-1]
                        json_data = df.to_json(orient='records')
                        parsed_json = json.loads(json_data)
                        print("csv_filename_extracted", csv_filename)
                        all_data.append({
                            'filename': csv_filename,
                            'data': parsed_json
                        })
                    except pd.errors.EmptyDataError:
                        print(f"Skipping file with no data: {csv_filename}")
                    except Exception as e:
                        print(f"Error processing file {csv_filename}: {str(e)}")
        if not all_data:
            print("No valid data found in any of the CSV files.")
            return None
        print(len(all_data), "file Extracted")
        return all_data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None
    


def project_document_list(sort_code):

    url = f"https://search.worldbank.org/api/v2/wds?format=json&os=0&order=desc&apilang=en&status_exact=Active^Closed&prodline_exact=GU^PE&countrycode_exact={sort_code}&fct=docty_exact,count_exact,lang_exact,disclstat_exact&majdocty_key=658102&rows=20&srt=docdt"

    payload = {}
    headers = get_headers('https://projects.worldbank.org')

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()
