import json
import os
from Final_pre import all_functions

def extract_data(country_code, country_name):
    """Extract data from various sources."""
    data = {}
    data['projects'] = all_functions.Get_list_of_projects(country_name, country_code)[1]
    data['file_list'] = all_functions.download_files(country_code)
    data['indicator_data'] = all_functions.Indicator_data(country_code, country_name)
    data['indicator_meta_data'] = all_functions.indicator_meta_data(country_code)
    data['sectors_data'] = all_functions.sectors(country_code)
    data['sectors_information'] = all_functions.sectors_information(country_code, country_name)
    data['country_indicator_group_information'] = all_functions.country_indecator_groups_data(country_name)
    data['country_full_information'] = all_functions.country_information(country_code, country_name)
    data['projects_and_operations_data'] = all_functions.projects_and_operations_data(country_code, country_name)
    data['other_indicator_data'] = all_functions.other_indecators_data(country_code, country_name)
    data['project_document'] = all_functions.project_document_list(country_code)
    return data

def transform_data(data):
    """Transform the extracted data."""
    transformed_data = {}
    
    # Example transformations (you can add more based on your needs):
    if 'projects' in data:
        transformed_data['projects'] = data['projects'].get('projects', [])[:8]  # Limit to 8 projects
    
    if 'indicator_data' in data:
        transformed_data['indicator_data'] = {
            k: {year: value for year, value in v.items() if year.isdigit()}
            for k, v in data['indicator_data'].get('jsonGraph', {}).get('indicatorData', {}).get(data['country_code'], {}).items()
        }
    
    # Add more transformations for other data types as needed
    
    return transformed_data

def load_data(data, country_code):
    """Load the transformed data into a JSON file."""
    json_file = f"Database/{country_code}.json"
    with open(json_file, 'w') as f:
        json.dump(data, f)
    print(f"Data for {country_code} has been saved to {json_file}")

def etl_pipeline(country_code, country_name):
    """Run the full ETL pipeline."""
    print(f"Starting ETL pipeline for {country_name} ({country_code})")
    
    print("Extracting data...")
    extracted_data = extract_data(country_code, country_name)
    
    print("Transforming data...")
    transformed_data = transform_data(extracted_data)
    
    print("Loading data...")
    load_data(transformed_data, country_code)
    
    print("ETL pipeline completed successfully.")

if __name__ == "__main__":
    # Example usage
    country_code = "US"
    country_name = "United States"
    etl_pipeline(country_code, country_name)