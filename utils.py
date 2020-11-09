import base64
import pandas as pd

def encode_image(path_image):
    return base64.b64encode(open(path_image, 'rb').read())

def get_ranking_home(x):
    if x == 'H':
        return 3
    if x == 'D':
        return 1
    if x == 'A':
        return 0

def get_ranking_away(x):
    if x == 'A':
        return 3
    if x == 'D':
        return 1
    if x == 'H':
        return 0

def create_score(x, y):
    return x + ' (' + y + ')'


def create_classement_col(df):
    df.index = pd.RangeIndex(start=1, stop=len(df)+1, step=1)
    df.reset_index(level=0, inplace=True)
    df.rename(columns={'index':'Classement'}, inplace=True)
    return df

def df_to_datatable(df):
    return df.to_dict('records'), [{'name': col, 'id': col} for col in df.columns]