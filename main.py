import argparse
import logging
import pandas as pd
import numpy as np
import random
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Randomly renames, reorders, and changes the data types of columns in a dataset to obfuscate its structure.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to the output CSV file.")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility.")
    return parser

def randomize_column_names(df, seed=None):
    """
    Randomly renames the columns of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to rename columns.
        seed (int, optional): Random seed for reproducibility. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with renamed columns.
    """
    if seed:
        random.seed(seed)
    new_names = [f"column_{i}" for i in range(len(df.columns))]
    random.shuffle(new_names)
    df = df.rename(columns=dict(zip(df.columns, new_names)))
    return df

def reorder_columns(df, seed=None):
    """
    Randomly reorders the columns of a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to reorder.
        seed (int, optional): Random seed for reproducibility. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with reordered columns.
    """
    if seed:
        random.seed(seed)
    columns = list(df.columns)
    random.shuffle(columns)
    df = df[columns]
    return df

def change_data_types(df, seed=None):
    """
    Changes the data types of columns in a DataFrame to obfuscate its structure.
    This attempts to preserve the underlying data as much as possible within new data types.

    Args:
        df (pd.DataFrame): The DataFrame to modify.
        seed (int, optional): Random seed for reproducibility. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame with modified data types.
    """
    if seed:
        random.seed(seed)
    
    for col in df.columns:
        original_type = df[col].dtype
        
        # List of possible types to convert to (excluding the original type)
        possible_types = [np.int64, np.float64, 'string', 'category']
        
        #Attempt numeric conversion and filtering.
        numeric_types = [np.int64, np.float64]

        if original_type in numeric_types:
            possible_types = [t for t in possible_types if t not in numeric_types]


        if original_type == 'object':
            possible_types = [t for t in possible_types if t != 'category']
        
        # Remove the original data type to avoid converting to the same type
        try:
            possible_types.remove(original_type)
        except ValueError:
            pass # If the original type is not explicitly in the list, ignore
        
        if not possible_types:
            logging.warning(f"No valid conversion types found for column: {col}")
            continue
        
        new_type = random.choice(possible_types)
        
        try:
            if new_type == np.int64:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(np.int64)
            elif new_type == np.float64:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(np.float64)
            elif new_type == 'string':
                df[col] = df[col].astype(str)
            elif new_type == 'category':
                df[col] = df[col].astype('category')
            
            logging.info(f"Column '{col}' converted from {original_type} to {new_type}")

        except Exception as e:
            logging.error(f"Failed to convert column '{col}' from {original_type} to {new_type}: {e}")

    return df

def validate_input(input_file):
    """
    Validates that the input file exists and is a CSV file.

    Args:
        input_file (str): The path to the input file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the input file is not a CSV file.
    """
    try:
        with open(input_file, 'r') as f:
            pass  # Just check if the file exists
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    except Exception as e:
        raise Exception(f"Error accessing input file: {e}")
    
    if not input_file.lower().endswith('.csv'):
        raise ValueError("Input file must be a CSV file.")


def main():
    """
    Main function to execute the data schema randomization.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        # Input validation
        validate_input(args.input_file)

        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(args.input_file)
        logging.info(f"Successfully read input file: {args.input_file}")

        # Apply randomization steps
        df = randomize_column_names(df, args.seed)
        df = reorder_columns(df, args.seed)
        df = change_data_types(df, args.seed)

        # Write the modified DataFrame to a new CSV file
        df.to_csv(args.output_file, index=False)
        logging.info(f"Successfully wrote output to file: {args.output_file}")

    except FileNotFoundError as e:
        logging.error(e)
    except ValueError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

# Example Usage:
# 1. Create a sample CSV file named 'input.csv' with some data.
# 2. Run the script from the command line:
#    python your_script_name.py input.csv output.csv --seed 42
#
#    This will:
#      - Read 'input.csv'.
#      - Randomize column names.
#      - Reorder columns.
#      - Change data types of some columns.
#      - Write the modified data to 'output.csv'.
#      - Use a random seed of 42 for reproducibility.