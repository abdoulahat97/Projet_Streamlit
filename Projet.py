import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from bs4 import BeautifulSoup as bs
from requests import get
import base64

# Titre de l'application
st.markdown("<h1 style='text-align: center; color: black;'>MY DATA SCRAPER APP</h1>", unsafe_allow_html=True)

# Description de l'application
st.markdown("""
Cette application permet de récupérer les données de Coinafrique pour les villas et les terrains. Vous pouvez également télécharger les données scrappées directement à partir de l'application.
* **Python libraries:** base64, pandas, streamlit, requests, bs4
* **Data source:** [Coinafrique Villas](https://sn.coinafrique.com/categorie/villas) -- [Coinafrique Terrains](https://sn.coinafrique.com/categorie/terrains).
""")

# Fonction pour ajouter un fond d'écran
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Fonction pour convertir un DataFrame en CSV
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Fonction pour afficher et télécharger les données
def load(dataframe, title, key, key1):
    st.markdown("""
    <style>
    div.stButton {text-align:center}
    </style>""", unsafe_allow_html=True)

    if st.button(title, key1):
        st.subheader('Display data dimension')
        st.write('Data dimension: ' + str(dataframe.shape[0]) + ' rows and ' + str(dataframe.shape[1]) + ' columns.')
        st.dataframe(dataframe)

        csv = convert_df(dataframe)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{title.replace(" ", "_")}.csv',
            mime='text/csv',
            key=key
        )

# Fonction pour charger les données des villas
def load_villas_data(num_pages):
    df = pd.DataFrame()
    
    for page in range(num_pages):
        st.write(f"Extraction des données de la page {page + 1}...")
        url = f'https://sn.coinafrique.com/categorie/villas?page={page}'
        res = get(url)
        if res.status_code != 200:
            st.error(f"Erreur : Impossible d'accéder à la page {page + 1}")
            continue
            
        contenu = bs(res.text, 'html.parser')
        Villas = contenu.find_all('div', class_="col s6 m4 l3")

        data = []

        for vil in Villas:
            try:
                image_element = vil.find('img', class_='ad__card-img')
                image_lien = 'https://sn.coinafrique.com/' + image_element['src'] if image_element else "Indisponible !"
                
                url_element = vil.find('a', class_='card-image ad__card-image waves-block waves-light')
                url_terrain = 'https://sn.coinafrique.com/' + url_element['href'] if url_element else None
                
                if not url_terrain:
                    st.warning("Error !")
                    continue
                
                recup = get(url_terrain)
                if recup.status_code != 200:
                    st.error(f"Error ! {url_terrain}")
                    continue
                    
                infos = bs(recup.text, 'html.parser')
                
                type_annonce_element = infos.find('h1', class_='title title-ad hide-on-large-and-down')
                type_annonce = type_annonce_element.text.strip().split()[0] if type_annonce_element else "Non spécifié !"
                
                nombre_pieces_element = infos.find('span', class_='qt')
                nombre_pieces = nombre_pieces_element.text.strip() if nombre_pieces_element else "Non spécifié !"
                
                prix_element = infos.find('p', class_='price')
                prix = prix_element.text.strip().replace(' ', '.').replace('.CFA', '') if prix_element else "Prix sur demande !"
                
                adresse_element = infos.find('span', class_='valign-wrapper', attrs={"data-address": True})
                adresse = adresse_element.text.strip() if adresse_element else "Address Non spécifié !"
                
                data.append({
                    'type_annonce': type_annonce,
                    'nombre_pieces': nombre_pieces,
                    'prix (F CFA)': prix,
                    'Adresse': adresse,
                    'Image Link': image_lien
                })
            except Exception as e:
                st.error(f"Error !{e}")
                continue

        temp_df = pd.DataFrame(data)
        df = pd.concat([df, temp_df], axis=0).reset_index(drop=True)
    
    return df

# Fonction pour charger les données des terrains
def load_terrains_data(num_pages):
    df = pd.DataFrame()
    
    for page in range(num_pages):
        st.write(f"Extraction des données de la page {page + 1}...")
        url = f'https://sn.coinafrique.com/categorie/terrains?page={page}'
        res = get(url)
        
        if res.status_code != 200:
            st.error(f"Error ! {page + 1}")
            continue
            
        soup = bs(res.text, 'html.parser')
        terrains = soup.find_all('div', class_='col s6 m4 l3')

        data = []

        for terrain in terrains:
            try:
                image_element = terrain.find('img', class_='ad__card-img')
                image_lien = 'https://sn.coinafrique.com/' + image_element['src'] if image_element else "Image invalide !"
                
                url_element = terrain.find('a', class_='card-image ad__card-image waves-block waves-light')
                url_terrain = 'https://sn.coinafrique.com/' + url_element['href'] if url_element else None
                
                if not url_terrain:
                    st.warning("Error !")
                    continue
                
                recup = get(url_terrain)
                if recup.status_code != 200:
                    st.error(f"Error ! {url_terrain}")
                    continue
                    
                infos = bs(recup.text, 'html.parser')
                
                superficie_element = infos.find('span', class_='qt')
                superficie = superficie_element.text.strip().replace('m²', '').replace(' m2', '').replace('m`', '') if superficie_element else "Non spécifié !"
                
                prix_element = infos.find('p', class_='price')
                prix = prix_element.text.strip().replace(' ', '.').replace('.CFA', '') if prix_element else "Prix sur demande !"
                
                adresse_element = infos.find('span', class_='valign-wrapper', attrs={"data-address": True})
                adresse = adresse_element.text.strip() if adresse_element else "Address Non spécifié !"
                
                data.append({
                    'superficie': superficie,
                    'Prix (F CFA)': prix,
                    'Adresse': adresse,
                    'Image Link': image_lien
                })
            except Exception as e:
                st.error(f"Error ! {e}")
                continue

        temp_df = pd.DataFrame(data)
        df = pd.concat([df, temp_df], axis=0).reset_index(drop=True)
    
    return df

# Interface utilisateur
st.sidebar.header('User Input Features')
Pages = st.sidebar.selectbox('Pages indexes', list([int(p) for p in np.arange(2, 600)]))
Choices = st.sidebar.selectbox('Options', ['Scrape data using beautifulSoup', 'Download scraped data', 'Fill the form (Kobotoolbox)', 'Fill the form (Google Forms)'])

add_bg_from_local('FF.jpg') 

if Choices == 'Scrape data using beautifulSoup':
    Villas_data_mul_pag = load_villas_data(Pages)
    Terrains_data_mul_pag = load_terrains_data(Pages)
    
    load(Villas_data_mul_pag, 'Villas data', '1', '101')
    load(Terrains_data_mul_pag, 'Terrains data', '2', '102')

elif Choices == 'Download scraped data': 
    Villas = pd.read_csv('Villas_data.csv')
    Terrains = pd.read_csv('Terrains_data.csv') 

    load(Villas, 'Villas data', '1', '101')
    load(Terrains, 'Terrains data', '2', '102')

elif Choices == 'Fill the form (Kobotoolbox)':
    components.html("""
    <iframe src="https://ee.kobotoolbox.org/i/y3pfGxMz" width="800" height="1100"></iframe>
    """, height=1100, width=800)

elif Choices == 'Fill the form (Google Forms)':
    # Lien du formulaire Google Forms
    google_form_url = "https://forms.gle/FRVdqvtLR4rqjNDm7"
    
    # Intégration du formulaire dans une iframe
    components.html(f"""
    <iframe src="{google_form_url}" width="800" height="1100" frameborder="0" marginheight="0" marginwidth="0">Chargement en cours...</iframe>
    """, height=1100, width=800)