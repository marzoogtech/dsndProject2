import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine 


def load_data(messages_filepath, categories_filepath):
    '''
    INPUT:
    messages_filepath - string of messages csv file path
    categories_filepath - string of categories csv file path

    OUTPUT:
    df - dataframe contaning messages and categories join using id col
    '''


    # reading massages and categories csv files
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    
    # merging the twe dataframe on id
    df = messages.merge(categories, left_on='id', right_on='id')
    
    return df


def clean_data(df):
    '''
    creat 36 category columns of 0 or 1 to replace the category col 
    and removing the duplicate values

    INPUT:
    df - dataframe 
    OUTPUT:
    df - dataframe after cleaning the data
    '''



    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)
    
    # select the first row of the categories dataframe
    row = categories.head(1)
    
    # rename the columns of `categories`
    get_col_name = lambda x: x[0][:-2]
    category_col_names = list(row.apply(get_col_name))
    categories.columns = category_col_names
    
    # Convert category values to 0 or 1
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
    
        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
    
    # replacing the 2 to 1 in the related column
    categories.related.replace(2, 1, inplace=True)
    
    # Replace categories column in df with new cateogry columns
    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    
    # Remove duplicaates
    df.drop_duplicates(inplace=True)
    
    return df


def save_data(df, database_filename):
    '''
    INPUT:
    df - dataframe to be saved
    database_filename - name of the database file
    '''


    engine = create_engine(f'sqlite:///{database_filename}')
    df.to_sql('tweets', engine, index=False, if_exists='replace')
    


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()