import logging
import datetime
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import assets.utils as utils

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def data_clean(df, metadados):
    '''
    Função principal para saneamento dos dados
    INPUT: Pandas DataFrame, dicionário de metadados
    OUTPUT: Pandas DataFrame, base tratada
    '''
    df["data_voo"] = pd.to_datetime(df[['year', 'month', 'day']]) 
    df = utils.null_exclude(df, metadados["cols_chaves"])
    df = utils.convert_data_type(df, metadados["tipos_originais"])
    df = utils.select_rename(df, metadados["cols_originais"], metadados["cols_renamed"])
    df = utils.string_std(df, metadados["std_str"])

    df.loc[:,"datetime_partida"] = df.loc[:,"datetime_partida"].str.replace('.0', '')
    df.loc[:,"datetime_chegada"] = df.loc[:,"datetime_chegada"].str.replace('.0', '')

    for col in metadados["corrige_hr"]:
        lst_col = df.loc[:,col].apply(lambda x: utils.corrige_hora(x))
        df[f'{col}_formatted'] = pd.to_datetime(df.loc[:,'data_voo'].astype(str) + " " + lst_col)
    
    logger.info(f'Saneamento concluído; {datetime.datetime.now()}')
    return df


def feat_eng(df):
    '''
    Função para realizar engenharia de features no DataFrame.
    INPUT: Pandas DataFrame
    OUTPUT: Pandas DataFrame com novas features
    '''
    # Verificar se as colunas necessárias estão presentes
    required_columns = ['datetime_chegada', 'datetime_partida', 'data_voo']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Coluna {col} não encontrada no DataFrame.")
    
    # Converter 'data_voo' para datetime diretamente, se necessário
    df['data_voo'] = pd.to_datetime(df['data_voo'], format='%Y-%m-%d', errors='coerce')
    
    # Função auxiliar para converter HHMM para datetime
    def convert_hhmm_to_datetime(series, base_date):
        # Cria uma série de strings no formato 'HH:MM' a partir dos valores 'HHMM'
        time_str = series.astype(str).str.zfill(4)  # Preenche com zeros à esquerda se necessário
        time_str = time_str.str[:2] + ':' + time_str.str[2:]  # Adiciona ':' entre horas e minutos
        return pd.to_datetime(base_date + ' ' + time_str, format='%Y-%m-%d %H:%M', errors='coerce')

    # Adicionar a data base para concatenar com as horas
    base_date = df['data_voo'].dt.strftime('%Y-%m-%d')  # Formata a data base para a concatenação

    # Converter 'datetime_chegada' e 'datetime_partida'
    df['datetime_chegada'] = convert_hhmm_to_datetime(df['datetime_chegada'], base_date)
    df['datetime_partida'] = convert_hhmm_to_datetime(df['datetime_partida'], base_date)
    
    # Remover linhas onde as conversões falharam
    df = df.dropna(subset=['datetime_chegada', 'datetime_partida', 'data_voo'])
    
    # Verificar se há datas válidas
    if df['datetime_chegada'].isnull().any() or df['datetime_partida'].isnull().any():
        logger.warning("Algumas datas de chegada ou partida são inválidas.")
    
    # Crie uma cópia do DataFrame para evitar problemas com SettingWithCopyWarning
    df = df.copy()
    
    # Calcular a duração do voo em horas
    df['duracao_voo'] = (df['datetime_chegada'] - df['datetime_partida']).dt.total_seconds() / 3600.0
    
    # Criar uma coluna de período com mês e ano
    df['mes_ano'] = df['data_voo'].dt.to_period('M')
    
    logger.info("Engenharia de features concluída com sucesso.")
    return df


def save_data_sqlite(df):
    '''
    Função para salvar o DataFrame no banco de dados SQLite.
    INPUT: Pandas DataFrame
    OUTPUT: None
    '''
    # Converter 'mes_ano' para string se existir
    if 'mes_ano' in df.columns:
        df['mes_ano'] = df['mes_ano'].astype(str)
    
    try:
        conn = sqlite3.connect("data/NyflightsDB.db")
        logger.info(f'Conexão com banco estabelecida ; {datetime.datetime.now()}')
    except Exception as e:
        logger.error(f'Problema na conexão com banco: {e}; {datetime.datetime.now()}')
        return
    
    try:
        df.to_sql('nyflights', con=conn, if_exists='replace', index=False)
        conn.commit()
        logger.info(f'Dados salvos com sucesso; {datetime.datetime.now()}')
    except Exception as e:
        logger.error(f'Erro ao salvar dados: {e}; {datetime.datetime.now()}')
    finally:
        conn.close()
        

def fetch_sqlite_data(table):
    try:
        conn = sqlite3.connect("data/NyflightsDB.db")
        logger.info(f'Conexão com banco estabelecida ; {datetime.datetime.now()}')
    except:
        logger.error(f'Problema na conexão com banco; {datetime.datetime.now()}')
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} LIMIT 5")
    print(c.fetchall())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    logger.info(f'Inicio da execução ; {datetime.datetime.now()}')
    metadados  = utils.read_metadado(os.getenv('META_PATH'))
    df = pd.read_csv(os.getenv('DATA_PATH'), index_col=0)
    df = data_clean(df, metadados)
    print(df.head())
    utils.null_check(df, metadados["null_tolerance"])
    utils.keys_check(df, metadados["cols_chaves"])
    df = feat_eng(df)
    save_data_sqlite(df)
    fetch_sqlite_data(metadados["tabela"][0])
    logger.info(f'Fim da execução ; {datetime.datetime.now()}')
