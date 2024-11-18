import basedosdados as bd
import pandas as pd
import os

def fetch_dataset(dataset_id, table_id, billing_project_id, save_path):
    """
    Fetches a dataset from basedosdados and saves it as a CSV file.

    Args:
        dataset_id (str): The dataset ID.
        table_id (str): The table ID.
        billing_project_id (str): The billing project ID.
        save_path (str): The path to save the CSV file.
    """
    # Fetch the dataset
    df = bd.read_table(dataset_id=dataset_id,
                       table_id=table_id,
                       billing_project_id=billing_project_id)
    # Ensure the save directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    # Save the DataFrame as a CSV file
    df.to_csv(save_path, index=False)
    print(f"Dataset {table_id} saved to {save_path}")

def fetch_all_datasets():
    """
    Fetches all required datasets and saves them as CSV files.
    """
    datasets = [
        'orgao_deputado',
        'proposicao_microdados',
        'proposicao_tema',
        'votacao_objeto',
        'votacao_parlamentar',
        'votacao'
    ]
    for table_id in datasets:
        save_path = f"data/csv/{table_id}.csv"
        fetch_dataset(
            dataset_id='br_camara_dados_abertos',
            table_id=table_id,
            billing_project_id="voting-networks",
            save_path=save_path
        )

if __name__ == "__main__":
    fetch_all_datasets()
