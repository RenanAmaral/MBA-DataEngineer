import logging

logger = logging.getLogger(__name__)

def keys_check(df, key_columns):
    """
    Função que valida as chaves especificadas no DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame que contém os dados.
    key_columns (list): Lista de colunas que devem ser usadas como chave.

    Returns:
    bool: True se as chaves forem válidas, False caso contrário.
    """
    for key in key_columns:
        if df[key].isnull().any():
            logger.error(f"Chave '{key}' contém valores nulos.")
            return False
        if df[key].duplicated().any():
            logger.error(f"Chave '{key}' contém valores duplicados.")
            return False
    
    logger.info("Validação das chaves concluída com sucesso.")
    return True
