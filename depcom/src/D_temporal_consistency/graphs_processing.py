import pandas as pd

def clean_dataframe(df):
    """
    This function processes a DataFrame by performing the following steps:
    1. Removes the first row with NaN values.
    2. Drops the second row (previously used as a header).
    3. Renames the 'year' column to 'party'.
    4. Removes the suffix ".1", ".2", etc. from the column names (except the first one).
    5. Adds a suffix from the first row of values to the columns, starting from the second column.
    6. Drops the first row after processing the suffix.

    Args:
        df (pandas.DataFrame): The DataFrame to be processed.

    Returns:
        pandas.DataFrame: The cleaned DataFrame with updated column names.
    """
    # Remove the row with NaN values (index=1)
    df = df.drop(index=1).reset_index(drop=True)
    
    # Remove the second row (used as a header)
    df = df.drop(index=2)
    
    # Rename 'year' column to 'party'
    df = df.rename(columns={'year': 'party'})
    
    # Get the suffix from the first row of values (starting from the second column)
    sufix = df.iloc[0, 1:].astype(int).astype(str)
    
    # Remove the ".1", ".2", etc. suffixes from column names (except the first column)
    cleaned_columns = [df.columns[0]] + [col.split('.')[0] for col in df.columns[1:]]
    
    # Update column names after cleaning the suffix
    df.columns = cleaned_columns
    
    # Rename columns starting from the second column using the suffix from the first row
    new_columns = ['party'] + [f"{col}_{suf}" for col, suf in zip(df.columns[1:], sufix)]
    
    # Apply new column names to the DataFrame
    df.columns = new_columns
    
    # Remove the first row (which contained the suffix values)
    df = df.drop(0)
    
    return df


def get_last_year(df):
    """
    This function extracts the years from the column names (starting from the second column),
    removes the "_X" suffix, and returns the latest year (highest value).
    
    Args:
        df (pandas.DataFrame): The DataFrame containing the columns to extract years from.
    
    Returns:
        int: The latest year found in the column names.
    """
    # Extract the year from the column names (starting from the second column) and remove the "_X" suffix
    years = [int(col.split('_')[0]) for col in df.columns[1:]]
    
    # Find the latest year (maximum value)
    last_year = max(years)
    
    return last_year

def largest_party_by_community(df, year):
    """
    Determines the largest party by community for the specified year.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.
    - year (int): The year to analyze.

    Returns:
    - dict: A dictionary with community information.
    """
    print(f"\nAnalyzing year {year}")
    year_columns = [col for col in df.columns if col.startswith(str(year))]
    print(f"Year columns: {year_columns}")
    results = {}
    for col in year_columns:
        community = col.split('_')[1]
        print(f"\nProcessing community {community} in column {col}")
        # Get the party with the maximum deputies in this community
        total_by_party = df.groupby('party')[col].sum()
        print(f"Total deputies by party in community {community}:\n{total_by_party}")
        if total_by_party.empty:
            print(f"No data for community {community} in year {year}.")
            continue
        party = total_by_party.idxmax()
        print(f"Party with the maximum deputies in community {community}: {party}")
        deputies_in_community = total_by_party.loc[party]
        total_deputies_community = df[col].sum()
        percentage = (deputies_in_community / total_deputies_community) * 100 if total_deputies_community > 0 else 0
        print(f"Deputies of party {party} in community {community}: {deputies_in_community}")
        print(f"Total deputies in community {community}: {total_deputies_community}")
        print(f"Percentage of deputies in community {community}: {percentage}%")
        results[f'Community_{community}'] = {
            'party': party,
            'deputies': deputies_in_community,
            'percentage': round(percentage, 2)
        }
    print(f"\nResults for year {year}:")
    for k, v in results.items():
        print(f"{k}: {v}")
    return results

def adjust_community_labels(df, reference_year):
    """
    Adjusts the community labels in the DataFrame based on the reference year,
    after excluding the community with the fewest deputies in each year (if there are more than 2 communities)
    and reorganizing the community numbers to eliminate gaps. The analysis is performed only on the largest community.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.
    - reference_year (int): The reference year to align communities.

    Returns:
    - pd.DataFrame: The adjusted DataFrame.
    """
    print(f"\nAdjusting community labels based on reference year: {reference_year}")

    # Exclude the community with the fewest deputies in the reference year if there are more than 2 communities
    year_columns = [col for col in df.columns if col.startswith(str(reference_year))]
    print(f"Reference year columns before exclusion: {year_columns}")

    if len(year_columns) > 2:
        # Determine the community with the fewest deputies
        total_deputies_per_community = {}
        for col in year_columns:
            total_deputies = df[col].sum()
            community = col.split('_')[1]
            total_deputies_per_community[community] = total_deputies

        # Find the community with the fewest deputies
        community_to_exclude = min(total_deputies_per_community, key=total_deputies_per_community.get)
        print(f"Community to exclude in reference year {reference_year}: {community_to_exclude}")

        # Exclude the community
        col_to_exclude = f"{reference_year}_{community_to_exclude}"
        df = df.drop(columns=[col_to_exclude])
        print(f"Columns after exclusion in reference year: {df.columns.tolist()}")

        # Reorganize community numbers in the reference year
        df = reorganize_community_numbers(df, reference_year)
        print(f"Columns after reorganizing in reference year: {df.columns.tolist()}")
    else:
        print(f"No community excluded in reference year {reference_year} (only 2 communities present).")
        # Reorganize community numbers to ensure they are consecutive
        df = reorganize_community_numbers(df, reference_year)
        print(f"Columns after reorganizing in reference year: {df.columns.tolist()}")

    # Update the reference_year_communities after exclusion and reorganization
    reference_year_communities = largest_party_by_community(df, reference_year)

    # Identify the largest community in the reference year
    largest_community = max(reference_year_communities.items(), key=lambda x: x[1]['deputies'])[0]
    largest_community_number = largest_community.split('_')[1]
    print(f"Largest community in reference year {reference_year}: {largest_community}")

    # We'll perform the analysis only on this largest community

    # Repeat the exclusion and reorganization process for each previous year
    previous_years = sorted(
        set(
            int(col.split('_')[0])
            for col in df.columns
            if col != 'party' and col.split('_')[0].isdigit() and int(col.split('_')[0]) < reference_year
        ),
        reverse=True
    )
    print(f"\nPrevious years to process: {previous_years}")
    for year in previous_years:
        print(f"\nProcessing year {year}")
        year_columns = [col for col in df.columns if col.startswith(str(year))]
        print(f"Year columns before exclusion: {year_columns}")

        if len(year_columns) > 2:
            # Determine the community with the fewest deputies
            total_deputies_per_community = {}
            for col in year_columns:
                total_deputies = df[col].sum()
                community = col.split('_')[1]
                total_deputies_per_community[community] = total_deputies

            # Find the community with the fewest deputies
            community_to_exclude = min(total_deputies_per_community, key=total_deputies_per_community.get)
            print(f"Community to exclude in year {year}: {community_to_exclude}")

            # Exclude the community
            col_to_exclude = f"{year}_{community_to_exclude}"
            df = df.drop(columns=[col_to_exclude])
            print(f"Columns after exclusion in year {year}: {df.columns.tolist()}")

            # Reorganize community numbers in the current year
            df = reorganize_community_numbers(df, year)
            print(f"Columns after reorganizing in year {year}: {df.columns.tolist()}")
        else:
            print(f"No community excluded in year {year} (only 2 communities present).")
            # Reorganize community numbers to ensure they are consecutive
            df = reorganize_community_numbers(df, year)
            print(f"Columns after reorganizing in year {year}: {df.columns.tolist()}")

    # Proceed with adjusting the community labels for the largest community
    # Now, we have at least 2 communities per year with consecutive numbers starting from 0

    # We will only adjust the labels for the largest community identified in the reference year
    previous_years = sorted(
        set(
            int(col.split('_')[0])
            for col in df.columns
            if col != 'party' and col.split('_')[0].isdigit() and int(col.split('_')[0]) < reference_year
        ),
        reverse=True
    )
    print(f"\nAdjusting community labels for previous years: {previous_years}")
    for year in previous_years:
        print(f"\nAdjusting labels for year {year}")
        year_columns = [col for col in df.columns if col.startswith(str(year))]
        print(f"Year columns: {year_columns}")
        # We need to adjust only the largest community
        community_ref = largest_community
        info_ref = reference_year_communities[community_ref]
        party_ref = info_ref['party']
        community_num_ref = community_ref.split('_')[1]
        print(f"\nProcessing community {community_ref} with party {party_ref}")
        # Evaluate both communities and find where the party has the most deputies
        max_deputies = -1
        found_community = None
        for col in year_columns:
            party_value_series = df.loc[df['party'] == party_ref, col]
            party_value = party_value_series.sum() if not party_value_series.empty else 0
            print(f"Party {party_ref} has value {party_value} in column {col}")
            if party_value > max_deputies:
                max_deputies = party_value
                found_community = col.split('_')[1]
        if found_community is None:
            print(f"Party {party_ref} not found in any community in year {year}")
            # Define old_col as the reference community number
            old_col = f'{year}_{community_num_ref}'
            # Create old_col if it does not exist
            if old_col not in df.columns:
                print(f"Column {old_col} does not exist. Creating column with zero values.")
                df[old_col] = 0.0
            # No swap needed
            continue
        else:
            print(f"Party {party_ref} has the most deputies in community {found_community} of year {year}")
            old_col = f'{year}_{found_community}'
        new_col = f'{year}_{community_num_ref}'
        # If old_col and new_col are the same, no action is needed
        if old_col == new_col:
            print(f"No swap needed for columns {old_col} and {new_col}")
            continue
        # Swap the column names
        print(f"Swapping column names {old_col} and {new_col}")
        df.rename(columns={old_col: 'temp_col_name'}, inplace=True)
        df.rename(columns={new_col: old_col}, inplace=True)
        df.rename(columns={'temp_col_name': new_col}, inplace=True)
        print(f"Columns after swap: {df.columns.tolist()}")
    return df

def reorganize_community_numbers(df, year):
    """
    Renames the community numbers in the given year to ensure they are consecutive
    starting from 0, eliminating any gaps.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.
    - year (int): The year for which to reorganize community numbers.

    Returns:
    - pd.DataFrame: The DataFrame with reorganized community numbers.
    """
    # Get current community numbers for the year
    year_columns = [col for col in df.columns if col.startswith(str(year))]
    print(f"Reorganizing community numbers for year {year}. Current columns: {year_columns}")
    # Extract community numbers and sort them
    community_numbers = sorted(int(col.split('_')[1]) for col in year_columns)
    # Create a mapping from old community numbers to new consecutive numbers
    new_numbers = list(range(len(community_numbers)))
    mapping = dict(zip(community_numbers, new_numbers))
    print(f"Community number mapping for year {year}: {mapping}")
    # Rename the columns according to the mapping
    rename_dict = {}
    for col in year_columns:
        old_community_num = int(col.split('_')[1])
        new_community_num = mapping[old_community_num]
        new_col_name = f"{year}_{new_community_num}"
        rename_dict[col] = new_col_name
    df = df.rename(columns=rename_dict)
    print(f"Columns after renaming for year {year}: {list(rename_dict.values())}")
    return df

def sort_columns(df):
    """
    Sorts the columns of the DataFrame from the earliest year to the latest year.

    Parameters:
    - df (pd.DataFrame): DataFrame containing the data.

    Returns:
    - pd.DataFrame: DataFrame with columns sorted.
    """
    # Exclude 'party' from the columns to be sorted
    columns = [col for col in df.columns if col != 'party']
    # Extract year and community from each column
    col_info = []
    for col in columns:
        parts = col.split('_')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            year = int(parts[0])
            community = int(parts[1])
            col_info.append((col, year, community))
        else:
            # Columns that do not follow the 'year_community' pattern go to the end
            col_info.append((col, float('inf'), float('inf')))
    # Sort the columns by year and community
    col_info_sorted = sorted(col_info, key=lambda x: (x[1], x[2]))
    # Get the sorted column names
    sorted_columns = ['party'] + [col[0] for col in col_info_sorted]
    # Reindex the DataFrame with the sorted columns
    df = df.reindex(columns=sorted_columns)
    return df

def export_dataframe_to_csv(df, file_name):
    """
    Exports the given DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to export.
        file_name (str): The name of the CSV file to save the DataFrame to.

    Returns:
        None
    """
    df.to_csv(file_name, index=False)
    print(f"DataFrame exported successfully to {file_name}")

# Função para criar um dataframe com a comunidade de menor número de membros de cada ano, com condições para duas ou mais comunidades
def get_min_community_generalized(df):
    # Criar uma cópia do dataframe para evitar modificar o original
    result_df = df.copy()

    # Obter os anos presentes no dataframe
    years = range(2003, 2024)  # Intervalo de anos mencionado na pergunta

    # Iterar por cada ano do dataframe
    for year in years:
        # Filtrar as colunas correspondentes às comunidades do ano atual
        community_cols = [col for col in df.columns if col.startswith(f"{year}_")]

        # Verificar o número de comunidades no ano
        if len(community_cols) == 2:
            # Se houver apenas duas comunidades, definir o valor mínimo como zero
            result_df[f"{year}_min"] = 0
        elif len(community_cols) >= 3:
            # Se houver três ou mais comunidades, calcular o menor valor entre elas
            result_df[f"{year}_min"] = result_df[community_cols].min(axis=1)

    # Filtrar apenas as colunas com o sufixo '_min' e a coluna 'party'
    result_df = result_df[['party'] + [f"{year}_min" for year in years if f"{year}_min" in result_df.columns]]

    return result_df

def merge_min_community_with_suffix_change(df_original, df_min_community):
    # Renomear as colunas do dataframe de comunidades mínimas, trocando o sufixo '_min' por '_2'
    df_min_community = df_min_community.rename(columns={col: col.replace('_min', '_2') for col in df_min_community.columns if '_min' in col})
    
    # Mesclar os dois dataframes usando a coluna 'party' como chave
    merged_df = pd.merge(df_original, df_min_community, on='party', how='left')
    
    return merged_df