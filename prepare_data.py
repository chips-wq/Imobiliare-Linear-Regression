import pandas as pd
import numpy as np
import re
import unidecode

CURRENT_YEAR = 2025

# Daca ne uitam la primele 17 feature-uri, si le dam drop la toate care nu sunt nule, avem 30.000 de exemple din 35.000 (suficient)
def drop_low_info_columns(df, k = 17):
  df = df.copy()
  non_null_counts = df.notnull().sum()
  top_k_cols_index = non_null_counts.sort_values(ascending=False).head(k).index
  df = df[top_k_cols_index].copy()
  return df

def drop_object_columns(df):
  df = df.copy()
  df = df.drop(columns=['Accesinternet', # Probabil nu conteaza
                   'Altespatiiutile', # Probabil influenteaza, unele atribute au valoarea "Terasa", la care cineva s-ar uita si ar pune pretul mai mic / mai mare
                   'Amenajarestrazi', # Pierdem mult aici, unele au "De pamant" ceea ce duce pretul in jos.
                   'Bucatarie', # Mobilata / Utilata / Partial mobilata
                   'Climatizare', # Posibil are o influenta, dar avem prea putine cu acest field
                   'Contorizare', # Nu are influenta atat de mare
                   'Diverse', # Greu sa faci regresie liniara pe "diverse"
                   'Dotariimobil', # Lift, gradina, piscina (important)
                   'Electrocasnice', # Relevant
                   'Ferestrecugeamtermopan', # Prea putine exemple
                   'Izolatiitermice', # Doar exterior / interior
                   'Mobilat', # Conteaza mult < pierdem puncte (putem incerca One-Hot encoding), 20.000 lipsa
                   'Nr.balcoane', # Conteaza
                   'Nr.bucătării', # Conteaza
                   'Nr.locuriparcare', # Conteaza
                   'Pereti', # Probabil ca unii se uita si la asta
                   'Podele',
                   'Regimînălţime',
                   'Serviciiimobil',
                   'Sistemincalzire', # Conteaza si asta destul de mult, reintegreaza pentru scor mai bun
                   'Stareinterior',
                   'Structurărezistenţă', # Relevant
                   'Suprafaţăutilătotală', # Oricum corelat cu Suprafata utila / construita
                   'Usaintrare',
                   'Usiinterior',
                   'Utilitatigenerale', # Conteaza
                   'agentCompany', # Irelevant
                   'agentName', # Irelevant
                   'id', # Irelevant
                   'last_update', # Irelevant
                   'url'])
  return df

def prepare_price(df):
  df = df.copy()
  df['price'] = df['price'].str.replace('.', '', regex=False).astype(float)
  return df

def prepare_etaj(df, column='Etaj'):
    df = df.copy()
    # 1) First extract all numeric floors
    def extract_numeric(s):
        s = str(s).strip().lower()
        m = re.match(r'etaj\s+(\d+)', s)
        return int(m.group(1)) if m else np.nan

    df['etaj_numeric'] = df[column].apply(extract_numeric)

    # 2) Compute max numeric floor (ignore NaNs)
    max_floor = int(df['etaj_numeric'].max(skipna=True))

    # 3) Map all entries to their final etaj code
    def map_etaj(s, numeric):
        s = str(s).strip().lower()
        if s.startswith('demisol'):
            return -1
        if s.startswith('parter'):
            return 0
        if s.startswith('mansarda'):
            return max_floor + 1
        # else if we parsed a number, use it
        if not np.isnan(numeric):
            return int(numeric)
        # fallback for other cases (e.g. 'Ultimele 2 etaje')
        return np.nan

    df['Etaj'] = df.apply(lambda row: map_etaj(row[column], row['etaj_numeric']), axis=1)

    # 4) Clean up intermediate column
    return df.drop(columns=['etaj_numeric'])

def prepare_camere(df):
  df = df.copy()
  df = df[df['Nr.camere'] <= 5]
  return df

def prepare_tip_imobil(df):
  df = df.copy()
  df['is_apartament'] = (df['Tipimobil'] == 'bloc de apartamente').astype(int)
  df['is_casa'] = (df['Tipimobil'] == 'casa/vila').astype(int)
  df = df.drop(columns=['Tipimobil'])
  return df

def prepare_confort(df):
  df = df.copy()
  df['is_confort_lux'] = (df['Confort'] == 'lux').astype(int)
  df['is_confort_1'] = (df['Confort'] == '1').astype(int)
  df['is_confort_2'] = (df['Confort'] == '2').astype(int)
  df['is_confort_3'] = (df['Confort'] == '3').astype(int)
  df = df.drop(columns=['Confort'])
  return df

def prepare_suprafete(df):
  df = df.copy()
  def parse_mp(value):
      # Remove ' mp', replace comma with dot, and convert to float
      return float(value.replace(' mp', '').replace(',', '.'))

  df['Suprafaţăutilă'] = df['Suprafaţăutilă'].map(parse_mp)
  df['Suprafaţăconstruită'] = df['Suprafaţăconstruită'].map(parse_mp)
  df = df[df['Suprafaţăconstruită'] <= 500]
  df = df[df['Suprafaţăconstruită'] >= 30]
  return df

def prepare_age(df):
  def parse_year(value):
      if isinstance(value, str):
          if value.isdigit():
              return CURRENT_YEAR - int(value)

          match = re.match(r'^(\d{4})', value)
          if match:
              return CURRENT_YEAR - int(match.group(1))

          if "Între" in value:
              years = re.findall(r'\d{4}', value)
              if years:
                  years = list(map(int, years))
                  avg_year = sum(years) // len(years)
                  return CURRENT_YEAR - avg_year

          if "Înainte de" in value:
              match = re.search(r'\d{4}', value)
              if match:
                  return CURRENT_YEAR - int(match.group(0)) + 10

      return None
  df['building_age'] = df['Anconstrucţie'].map(parse_year)
  df = df[df['building_age'] <= 75]
  df = df.drop('Anconstrucţie', axis=1)
  return df

def prepare_compartimentare(df):
    """
    One-hot encode the ‘Compartimentare’ column.
    Drops the original column and appends dummy variables:
      comp_nedecomandat, comp_vagon, comp_circular, comp_semidecomandat, comp_decomandat
    """
    df = df.copy()
    # create dummies
    dummies = pd.get_dummies(df['Compartimentare'], prefix='comp', dtype=int)
    # drop original and concat
    df = pd.concat([df.drop(columns=['Compartimentare']), dummies], axis=1)
    return df

def prepare_location(df):
  df = df.copy()
  def parse_location(loc):
      # 1) normalize: strip accents, lowercase
      s = unidecode.unidecode(loc).lower()
      # 2) extract sector number (or mark as none)
      m = re.search(r'sector\s*(\d+)', s)
      sector = f"sector_{m.group(1)}" if m else "sector_none"
      # 3) isolate zona: remove labels, commas, spaces
      z = re.sub(r'bucuresti|sector\s*\d+|zona', '', s)       # drop labels
      z = z.replace(',', '').replace(' ', '')                # drop commas & spaces
      zona = f"zona_{z}" if z else "zona_none"
      return pd.Series([sector, zona], index=['sector','zona'])

  # assume df['location'] holds your array of strings
  df[['sector','zona']] = df['location'].apply(parse_location)

  # one-hot encode
  sector_dummies = pd.get_dummies(df['sector'], prefix='is_sector', dtype=int)
  zona_dummies   = pd.get_dummies(df['zona'],   prefix='is_zona', dtype=int)

  # merge back
  df = pd.concat([df, sector_dummies, zona_dummies], axis=1)
  df = df.drop(columns=['location', 'sector', 'zona'])
  return df


def get_parsed_csv():
  df = pd.read_csv('imobiliare.csv')
  df = (df.pipe(drop_object_columns)
        .dropna()
        .pipe(prepare_price)
        .pipe(prepare_etaj)
        .dropna()
        .pipe(prepare_camere)
        .pipe(prepare_tip_imobil)
        .pipe(prepare_confort)
        .pipe(prepare_suprafete)
        .pipe(prepare_age)
        .pipe(prepare_compartimentare)
        .pipe(prepare_location))

  return df

if __name__ == '__main__':
  df = get_parsed_csv()
  df.info()
