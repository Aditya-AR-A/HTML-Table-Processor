
# HTML Table Processor

This project extracts, cleans, and processes HTML tables from a specified folder and stores the structured data into a CSV file.

## Project Structure

```
Business Quant Dataset - Html Tables/
    table_12.html
    table_62.html
    table_9.html
Business-Quant-Dataset-Html-Tables.zip
final_result.csv
Main.py
Quant Crawler Script.zip
terst.ipynb
```

## Requirements

- Python 3.x
- pandas
- numpy
- BeautifulSoup4

## Installation

1. Clone the repository or download the zip file.
2. Install the required Python packages using pip:

```sh
pip install pandas numpy beautifulsoup4
```

## Usage

1. Place your HTML files in the `Business Quant Dataset - Html Tables` folder.
2. Run the Main.py script:

```sh
python Main.py
```

3. The script will process all HTML tables in the folder and store the structured data in final_result.csv.

## Functions

### `extract_data(file_path: Path) -> list`

Extracts all tables from an HTML file and converts them into DataFrames.

### `title_extraction(df: pd.DataFrame) -> str`

Extracts the title from the first row, second column of a DataFrame.

### `store_data(file_path: Path, title: str, df: pd.DataFrame, output_file: str, first_run: bool)`

Transforms the DataFrame into a structured format and appends it to a CSV file.

### `clean_tables(df_origin: pd.DataFrame, file_path: Path, first_run: bool)`

Cleans and structures an extracted HTML table DataFrame.

## Example

```python
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
```

## License

This project is licensed under the MIT License.
```

This `README.md` file provides an overview of the project, installation instructions, usage guidelines, and descriptions of the main functions.
This `README.md` file provides an overview of the project, installation instructions, usage guidelines, and descriptions of the main functions.
