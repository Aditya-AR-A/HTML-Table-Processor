
import os
import numpy as np
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from warnings import filterwarnings

# To Stop the unwanted warnings
filterwarnings('ignore')


# Creating empty list to store the Data
all_tables = []


def extract_data(file_path):
    '''Extracts all tables from an HTML file and converts them into DataFrames.

    Args:
        file_path (Path): The path to the HTML file.

    Returns:
        list: A list of tuples, where each tuple contains:
            - DataFrame extracted from an HTML table.
            - The file path for reference.
    '''

    # Load the HTML file
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Find all tables in the HTML
    tables = soup.find_all("table")

    # Extract data from each table
    for table in tables:
        rows = table.find_all("tr")
        table_data = []

        for row in rows:
            cells = row.find_all(["th", "td"])  # Extract both headers and data
            row_data = [cell.get_text(strip=True) for cell in cells]  # Clean text
            table_data.append(row_data)

        # Convert to DataFrame
        df = pd.DataFrame(table_data)

        all_tables.append([df, file_path])  # Store all extracted tables

    return all_tables


def title_extraction(df: pd.DataFrame):
    '''Extracts the title from the first row, second column of a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame extracted from an HTML table.

    Returns:
        str: The extracted title or 'No Title' if no valid title is found.
    '''
    
    # Extract the title candidate from the first row, second column
    title = df.iloc[0, 1]

    # Check for NaN or empty values
    return title if pd.notna(title) and title != '' else "No Title"


def store_data(file_path: Path, title: str, df: pd.DataFrame, output_file: str, first_run: bool):
    '''Transforms the DataFrame into a structured format and appends it to a CSV file.

    Args:
        file_path (Path): The file path of the original HTML file.
        title (str): The extracted title of the table.
        df (pd.DataFrame): The cleaned DataFrame to be stored.
        output_file (str): The CSV file to store the structured data.
        first_run (bool): Whether this is the first run (if True, overwrites the file).

    Returns:
        None
    '''
    structured_data = []  # Store transformed data

    file_name = file_path.name

    for row_idx in range(len(df)):  # Loop through rows
        label = df.iloc[row_idx, 0]  # First column is the label
        
        for col_idx in range(1, len(df.columns)):  # Loop through other columns
            column_name = df.columns[col_idx]  # Extract column name
            value = df.iloc[row_idx, col_idx]  # Extract value

            structured_data.append({
                "filename": file_name,
                "label": label,
                "tablename": title,
                "column name": column_name,
                "value": value
            })

    result_df = pd.DataFrame(structured_data)

    # Write to CSV (overwrite for first run, append for subsequent runs)
    mode = 'w' if first_run else 'a'
    result_df.to_csv(output_file, index=False, mode=mode, header=first_run)


def clean_tables(df_origin: pd.DataFrame, file_path: Path, first_run: bool):
    '''Cleans and structures an extracted HTML table DataFrame.

    Steps:
        1. Drops empty columns and rows.
        2. Extracts and removes the title if found.
        3. Merges dollar signs and percentage symbols with adjacent numbers.
        4. Shifts values to remove NaNs.
        5. Handles special cases like single-value rows.
        6. Stores cleaned data in a structured format.

    Args:
        df_origin (pd.DataFrame): The raw DataFrame extracted from an HTML table.
        file_path (Path): The file path of the original HTML file.
        first_run (bool): Whether this is the first run (for CSV writing mode).

    Returns:
        None
    '''

    df = df_origin.copy(deep = True)

    # Drop Empty Columns
    df = df.astype(object).replace("", np.nan)  # Convert empty strings to NaN explicitly
    # Remove columns where all values are NaN
    df.dropna(axis=1, how="all", inplace=True)  
    # Remove rows where all values are NaN
    df.dropna(axis=0, how="all", inplace=True)

    # Extracting The title
    title = title_extraction(df)
    if title != 'No Title':
        df = df.iloc[1:].reset_index(drop=True)  # Drops first row and resets index
    

    # Merge Dollar Signs with Adjacent Numbers
    for i in range(len(df)):
        for j in range(len(df.columns) - 1):
            if df.iloc[i, j] == '':
                df.iloc[i, j] = np.nan
            # Apply function to DataFrame column
            if str(df.iloc[i, j]).strip() == "$":  # Check if cell contains "$"
                df.iloc[i, j] = np.nan  # Remove "$"
                df.iloc[i, j + 1] = df.iloc[i, j + 1] # Replace with adjacent cell value

            if (("%" == str(df.iloc[i, j + 1]).strip()) | ("%)" == str(df.iloc[i, j + 1]).strip())) :  # Check if cell contains "%"
                df.iloc[i, j] =  str(df.iloc[i, j]) + " %" 
                df.iloc[i, j + 1] = np.nan  # Remove "%"

                if '(' in df.iloc[i, j]:
                    df.iloc[i, j] = df.iloc[i, j].replace('(', '-')


    # Shift values to the right (preserve order)
    df = df.apply(lambda row: pd.Series([np.nan] * row.isna().sum() + row.dropna().tolist()), axis=1)
    
    df.dropna(axis=1, how="all", inplace=True)  # Remove columns where all values are NaN

    values = df.iloc[0].values
    count = 0
    for val in values:
         if pd.notna(val):
             count += 1
             non_nan_val = val
        
    if count == 1:
        single_value = non_nan_val  
        # Shift all values in the second row (row index = 1) to remove NaNs
        second_row_values = df.iloc[1].dropna().tolist()  # Remove NaNs
        second_row_values.append(single_value)
        # Ensure new row length matches DataFrame columns (pad with NaNs if needed)
        df.iloc[1] = second_row_values + [np.nan] * (df.shape[1] - len(second_row_values))
        # Remove the original single-value row
        df.drop(index=i, inplace=True)  
        df.reset_index(drop=True, inplace=True)  
        df = df.iloc[1:].reset_index(drop=True)

    stored_columns = df.iloc[0]
    
    # Shift Values Left to Remove NaNs
    df = df.apply(lambda row: pd.Series(row.dropna().tolist() + [np.nan] * row.isna().sum()), axis=1)

    df.columns = stored_columns
    df = df.iloc[1:].reset_index(drop=True)

    store_data(file_path, title, df, "final_result.csv", first_run)


# Folder path
folder_path = "Business Quant Dataset - Html Tables"
# Get all HTML files in the folder
html_files = [f for f in os.listdir(folder_path) if f.endswith(".html")]

# Print file names
print(">>> Detected HTML Files:", html_files)


for file in html_files:
    print(f'>>> Extracting {file}')
    full_path = Path(folder_path) / file
    extract_data(full_path)
    print('... Done')


first_run = True
for table in all_tables:
    print(f'>>> Cleaning {table[1]}')
    clean_tables(table[0], table[1], first_run)
    first_run = False
    print('... Done')





