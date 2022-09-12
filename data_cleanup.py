import numpy as np
import pandas as pd

def format_and_parse(webscrapper_csv_path):
    
    # Create Dataframe
    df = pd.read_csv(webscrapper_csv_path)

    # Eliminate non-useful fields
    df.drop('web-scraper-order', inplace=True, axis=1)
    df.drop('web-scraper-start-url', inplace=True, axis=1)
    df.drop('price', inplace=True, axis=1)
    df.drop('PaginationLinks', inplace=True, axis=1)
    df.drop('PaginationLinks-href', inplace=True, axis=1)
    
    # Eliminate rows with key missing data
    df.dropna(subset=['beds'], inplace=True)
    df.dropna(subset=['baths'], inplace=True)
    df.dropna(subset=['size'], inplace=True)
    df.dropna(subset=['address'], inplace=True)
    df.dropna(subset=['price-link'], inplace=True)

    # To support deduplication break up the address field
    df['StreetAddress'] = df['address'].str.split(',').str[0]
    df['City'] = df['address'].str.split(',').str[1]
    df['State'] = df['address'].str.split(',').str[2].str.split(' ').str[1]
    df['Zip'] = df['address'].str.split(',').str[2].str.split(' ').str[2]

    # For the street address field, delete text matches "LOT X" where X represents any digit, digits, letter, or hyphenated combination.
    target_regex = '\ (L|l)(O|o)(T|t)\ (([0-9]+-*[0-9]*[A-Z]*)|[A-Z])'
    df['StreetAddress'] = df_train['StreetAddress'].str.replace(target_regex, '')

    # Drop the Address Field
    df.drop('address', inplace=True, axis=1)

    # Standardize Lotsize units
    def convertToAcres(x):
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

    df['LotSize'] = df['LotSize'].apply(convertToAcres)

    # Remove occasional "Built in"
    def extractYearBuilt(x):
        target_regex = '[0-9]+'
        match = re.search(target_regex,str(x))
        if match:
          return int(match[0])
        else:
          return 0

    df['YearBuilt'] = df['YearBuilt'].apply(extractYearBuilt)

    # Replace non-target zip codes with zero (always found in duplicates)
    def replaceInvalidZipcodes(x):
        target_zipcodes = [27943, 27936, 27920, 27915, 27927, 27982, 27968]
        if x in target_zipcodes:
            return x
        else:
            return 0
    
    df['Zip'] = df['Zip'].apply(replaceInvalidZipcodes)


    # Replace non-target cities with empty string (always found in duplicates)
    def replaceInvalidCities(x):
        target_cities = ['Avon', 'Buxton', 'Frisco', 'Hatteras', 'Rodanthe', 'Salvo', 'Waves']
        if x in target_cities:
            return x
        else:
            return ''
    
    df['City'] = df['City'].apply(replaceInvalidCities)
    

    # For duplicate "StreetAddress": 
    #   Take the higher of all numerical fields
    #   Take the city and zip that match cities being evaluated
    #   Merge the PropertyDetails field.

    # Step on is replace any cities that aren't in the target cities
    
    # if df has a field called "date-sold"
    df = df.groupby('StreetAddress').agg({'ListingLink-href' : 'first','YearBuilt' : 'max',
                                          'LotSize' : 'max',
                                          'beds' : 'max',
                                          'baths' : 'max',
                                          'size' : 'max',
                                          'date-sold':'first',
                                          'price-link' : 'first',
                                          'PropertyDetails' : ', '.join}).reset_index()

    # else
    df = df.groupby('StreetAddress').agg({'ListingLink-href' : 'first',
                                          'YearBuilt' : 'max',
                                          'LotSize' : 'max',
                                          'beds' : 'max',
                                          'baths' : 'max',
                                          'size' : 'max',
                                          'price-link' : 'first',
                                          'PropertyDetails' : ', '.join}).reset_index()
