import re
import datetime
import numpy as np
import pandas as pd

def format_and_parse(webscrapper_csv_path):
    # Create Dataframe
    df = pd.read_csv(webscrapper_csv_path)

    # Eliminate non-useful fields
    df.drop('web-scraper-order', inplace=True, axis=1)
    df.drop('web-scraper-start-url', inplace=True, axis=1)
    df.drop('price', inplace=True, axis=1)
    # df.drop('PaginationLinks', inplace=True, axis=1)
    # df.drop('PaginationLinks-href', inplace=True, axis=1)

    # Eliminate rows with key missing data
    df.dropna(subset=['beds'], inplace=True)
    df.dropna(subset=['baths'], inplace=True)
    df.dropna(subset=['size'], inplace=True)
    df.dropna(subset=['address'], inplace=True)
    df.dropna(subset=['price-link'], inplace=True)

    # To support deduplication break up the address field
    df['StreetAddress'] = df['address'].str.split(',').str[0]
    df['City'] = df['address'].str.split(',').str[1].str.lstrip(' ')
    df['State'] = df['address'].str.split(',').str[2].str.split(' ').str[1]
    df['Zip'] = df['address'].str.split(',').str[2].str.split(' ').str[2]
    
    
    # Drop rows with NaN zip code
    df.dropna(subset=['Zip'], inplace=True)
    # Convert Zip to int
    df['Zip'] = df['Zip'].astype(int)

    # Convert PropertyDetails to string
    df['PropertyDetails'] = df['PropertyDetails'].astype(str)

    # For the street address field, delete text matches "LOT X" where X represents
    # any digit, digits, letter, or hyphenated combination.
    target_regex = '\ (L|l)(O|o)(T|t)\ (([0-9]+-*[0-9]*[A-Z]*)|[A-Z])'
    df['StreetAddress'] = df['StreetAddress'].str.replace(target_regex, '')

    # Also replace "Street" with "St" and "Drive" with "Dr"
    df['StreetAddress'] = df['StreetAddress'].str.replace("Street", "St")
    df['StreetAddress'] = df['StreetAddress'].str.replace("Drive", "Dr")


    # Drop the Address Field
    df.drop('address', inplace=True, axis=1)

    # Standardize Lotsize units
    def convert_to_acres(x):
        x = str(x).replace(',', '')
        if "No Data" in str(x):
            return 0.0
        if " Acres" in str(x):
            return float(str(x).replace(' Acres', ''))
        else:
            if " sqft" in str(x):
                sqft_val = float(str(x).replace(' sqft', ''))
                return sqft_val/43560
        return 0.0

    df['LotSize'] = df['LotSize'].apply(convert_to_acres)

    # Remove occasional "Built in"
    def extract_year_built(x):
        target_regex = '[0-9]+'
        match = re.search(target_regex,str(x))
        if match:
            return int(match[0])
        else:
            return 0

    df['YearBuilt'] = df['YearBuilt'].apply(extract_year_built)

    # Replace non-target zip codes with zero (always found in duplicates)
    def replace_invalid_zipcodes(x):
        target_zipcodes = [27943, 27936, 27920, 27915, 27972, 27982, 27968]
        if x in target_zipcodes:
            return x
        else:
            return 0

    df['Zip'] = df['Zip'].apply(replace_invalid_zipcodes)
    

    # Replace non-target cities with empty string (always found in duplicates)
    def replace_invalid_cities(x):
        target_cities = ['Avon', 'Buxton', 'Frisco', 'Hatteras', 'Rodanthe', 'Salvo', 'Waves']
        if x in target_cities:
            return x
        else:
            return ''

    df['City'] = df['City'].apply(replace_invalid_cities)

    # For duplicate "StreetAddress":
    #   Take the higher of all numerical fields
    #   Take the max city and max zip
    #       (based on above manipulation ensure match areas being targeted)
    #   Join the PropertyDetails field.

    # distiguish between sold data and for-sale data
    if 'date-sold' in df.columns:
        df = df.groupby('StreetAddress').agg({'ListingLink-href' : 'first',
                                              'YearBuilt' : 'max',
                                              'LotSize' : 'max',
                                              'beds' : 'max',
                                              'baths' : 'max',
                                              'size' : 'max',
                                              'date-sold':'first',
                                              'price-link' : 'first',
                                              'City' : 'max',
                                              'Zip' : 'max',
                                              'PropertyDetails' : ', '.join}).reset_index()
    else:
        df = df.groupby('StreetAddress').agg({'ListingLink-href' : 'first',
                                              'YearBuilt' : 'max',
                                              'LotSize' : 'max',
                                              'beds' : 'max',
                                              'baths' : 'max',
                                              'size' : 'max',
                                              'price-link' : 'first',
                                              'City' : 'max',
                                              'Zip' : 'max',
                                              'PropertyDetails' : ', '.join}).reset_index()

    # Drop any rows that have empty City
    df['City'].replace('',np.nan, inplace=True)
    df.dropna(subset=['City'], inplace=True)

    # Add binaries based on "PropertyDescription"
    def has_private_pool(x):
        target_regex = 'Private pool: Yes'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['PrivatePool'] = df['PropertyDetails'].apply(has_private_pool)


    def is_ocean_front(x):
        target_regex = '(waterfront features: ocean front)|(waterfront features: oceanfront)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['OceanFront'] = df['PropertyDetails'].apply(is_ocean_front)

    def is_sound_front(x):
        target_regex = '(waterfront features: sound front)|(waterfront features: soundfront)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['SoundFront'] = df['PropertyDetails'].apply(is_sound_front)

    def is_canal_front(x):
        target_regex = '(waterfront features: canal front)|(waterfront features: canalfront)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['CanalFront'] = df['PropertyDetails'].apply(is_canal_front)

    def has_beach_access(x):
        target_regex = '(beach access)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['BeachAccess'] = df['PropertyDetails'].apply(has_beach_access)

    def has_waterview(x):
        target_regex = '(has waterview: yes)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['WaterView'] = df['PropertyDetails'].apply(has_waterview)

    def lots_from_ocean_front(x):
        target_regex = '(lots from oceanfront)'
        if re.search(target_regex, str(x), re.IGNORECASE):
            return 1
        else:
            return 0

    df['LotsFromOceanFront'] = df['PropertyDetails'].apply(lots_from_ocean_front)

    # Rename columns to match legacy code

    df.rename(columns={"price-link" : "Price",
                        "size" : "Size",
                        "beds" : "Bedrooms",
                        "baths" : "Bathrooms",
                        "date-sold" : "DateSold" }, inplace=True)

    df['Price'] = df['Price'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['Size'] = df['Size'].replace({',': ''}, regex=True).astype(float)



    df['DateSold'] = pd.to_datetime(df['DateSold'])

    df['MonthsSold'] = datetime.datetime.now() - df['DateSold']
    df['MonthsSold'] = df['MonthsSold']/np.timedelta64(1,'M')

    return df

def join_and_dedup(old_dataframe, new_dataframe):
    df = pd.concat([old_dataframe, new_dataframe], ignore_index=True, sort=False)
    df.drop_duplicates(inplace=True)
    return df


def main():
    result = format_and_parse('zillow-sold.csv')
    result.to_csv('out.csv', index=False)
    
if __name__ == "__main__":
    main()