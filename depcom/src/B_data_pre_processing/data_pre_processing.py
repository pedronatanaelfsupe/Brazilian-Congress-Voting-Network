import pandas as pd
from functools import reduce

def rename_columns(df, columns_mapping):
    """
    Renames columns in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to rename columns in.
        columns_mapping (dict): A dictionary mapping old column names to new ones.

    Returns:
        pd.DataFrame: The DataFrame with renamed columns.
    """
    return df.rename(columns=columns_mapping)

def merge_datasets(df_list, on_columns):
    """
    Merges multiple DataFrames on specified columns.

    Args:
        df_list (list): A list of DataFrames to merge.
        on_columns (list): A list of column names to merge on.

    Returns:
        pd.DataFrame: The merged DataFrame.
    """
    return reduce(lambda left, right: pd.merge(left, right, on=on_columns), df_list)

def filter_votacoes(df):
    """
    Filters out rows where 'aprovacao' is null.

    Args:
        df (pd.DataFrame): The DataFrame to filter.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    return df[df['aprovacao'].notnull()]

def calculate_yes_vote_percentage(df):
    """
    Calculates the percentage of 'Sim' votes.

    Args:
        df (pd.DataFrame): The DataFrame containing vote counts.

    Returns:
        pd.DataFrame: The DataFrame with an added 'yes_vote_percentage' column.
    """
    df['total_votes'] = df['voto_sim'] + df['voto_nao'] + df['voto_outro']
    df['yes_vote_percentage'] = df['voto_sim'] / df['total_votes']
    return df

def filter_polarized_votacoes(df, lower_bound, upper_bound):
    """
    Filters votacoes to keep only those where the percentage of 'Sim' votes
    is between lower_bound and upper_bound.

    Args:
        df (pd.DataFrame): DataFrame containing votacoes data.
        lower_bound (float): Lower bound percentage (0-100).
        upper_bound (float): Upper bound percentage (0-100).

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    return df[(df['yes_vote_percentage'] >= lower_bound) & (df['yes_vote_percentage'] <= upper_bound)]
