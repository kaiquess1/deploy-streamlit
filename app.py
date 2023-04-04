# App para prvisão de preços de imóveis para aluguéis e preços de venda para a cidade de São Paulo
# Import das biblioteca
import numpy as np
import pandas as pd
import streamlit as st
import pickle
from sklearn.ensemble import GradientBoostingRegressor
from catboost impo

st.set_page_config(page_title='Simulador',
                   page_icon='https://w7.pngwing.com/pngs/566/66/png-transparent-computer-icons-home-page-web-page-real-estate-icon-angle-building-text.png')

def data_prep(dataset):
    # Encoding das Variáveis
    dataset['Elevator'] = dataset['Elevator'].map({'yes': 1, 'no': 0})
    dataset['Furnished'] = dataset['Furnished'].map({'yes': 1, 'no': 0})
    dataset['Swimming_Pool'] = dataset['Swimming_Pool'].map({'yes': 1, 'no': 0})

    # Criando a variável "Comercial"
    # dataset['Comercial'] = (dataset['Price'] >= 8000) | (dataset['Size'] >= 200)
    # dataset['Comercial'] = dataset['Comercial'].map({True: 1, False: 0})
    # Valor do metro quadrado por apartamento
    dataset['m2'] = np.round((dataset['Price'] + dataset['Condo']) / dataset['Size'])

    return dataset


def main():
    html_temp = """
    <div style="background-color:;padding:10px">
    <h1 style="color:black;text-align:center;">Habitação São Paulo</h1>

    """
    st.markdown(html_temp, unsafe_allow_html=True)
    page_bg_img = '''
    <STYLE>
    BODY { 
    background-image: url('https://th.bing.com/th/id/OIP.Y9_iTlO1h6yNPXFOmaY38QHaDt?pid=ImgDet&rs=1');
    background-size: cover;
    }
    </STYLE>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)


if __name__ == '__main__':
    main()

st.markdown(''' Criei esse aplicativo para prever preços de imóveis na cidade de São Paulo, \
	        através dele podemos simular valores de imóveis para alugar ou comprar.\
	        ''')
st.image(
    'https://th.bing.com/th/id/R.76d2646e5ee142f78f0d451e75c434f2?rik=g9AKbRZeyojB2w&riu=http%3a%2f%2fbulbox.com.br%2fservicos-ambientais%2fwp-content%2fuploads%2f2014%2f02%2f2015-01-24_SPAnniversary_PT-BR9428457289_1920x1080.jpg&ehk=RR4uQdAogOJxgsnNT0hssRgMHQ%2bOulw9hVlgD6ebzMk%3d&risl=&pid=ImgRaw&r=0',
    use_column_width=True)
# st.sidebar.info('Qual tipo de finalide tem interesse em prver')
st.sidebar.title('Faça uma simulação do imóvel que deseja')
add_selectbox = st.sidebar.selectbox(
    'Escolha a Finalidade', ('Alugar', 'Comprar'))

# st.sidebar.image('SP-Center.jpg', use_column_width=True)

if add_selectbox == 'Alugar':
    Condo = st.sidebar.slider('Taxa de Condomínio', min_value=0, max_value=10000)
    Price = st.sidebar.slider('Valor que está disposto a pagar', min_value=500, max_value=50000)
    Size = st.sidebar.number_input('Tamanho', min_value=30, max_value=880)
    Rooms = st.sidebar.selectbox('Quantidade de Quartos', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    Suites = st.sidebar.selectbox('Quantidade de Suites', [0, 1, 2, 3, 4, 5])
    Toilets = st.sidebar.selectbox('Quantidade de banheiros', [1, 2, 3, 4, 5, 6, 7, 8])

    if st.sidebar.checkbox('Elevador'):
        Elevator = 'yes'
    else:
        Elevator = 'no'

    if st.sidebar.checkbox('Imóvel Mobiliado'):
        Furnished = 'yes'
    else:
        Furnished = 'no'

    if st.sidebar.checkbox('Piscina'):
        Swimming_Pool = 'yes'
    else:
        Swimming_Pool = 'no'

    Parking = st.sidebar.selectbox('Vagas no Estacionamento', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    data = {'Condo': Condo,
            'Size': Size,
            'Rooms': Rooms,
            'Toilets': Toilets,
            'Suites': Suites,
            'Parking': Parking,
            'Elevator': Elevator,
            'Furnished': Furnished,
            'Swimming_Pool': Swimming_Pool,
            'Price': Price}

    rent = pd.DataFrame(data, index=[0])
    X_test = data_prep(rent)

    df_cols = ['Condo', 'Size', 'Rooms', 'Toilets',
               'Suites', 'Parking', 'Elevator', 'Furnished',
               'Swimming_Pool', 'm2']

    if st.sidebar.button('Buscar'):
        model = pickle.load(open('ModeloRent_GradientBoostingRegressor.pkl', 'rb'))
        ans = model.predict(rent[df_cols])
        st.subheader(f'O preço do imóvel com as características que você deseja alugar é ${np.round(ans, 2)} (INR) ')

if add_selectbox == 'Comprar':

    Condo = st.sidebar.slider('Taxa de Condomínio', min_value=0, max_value=10000)
    Price = st.sidebar.slider('Valor que está disposto a pagar', min_value=45000, max_value=10000000)
    Size = st.sidebar.number_input('Tamanho', min_value=30, max_value=880)
    Rooms = st.sidebar.selectbox('Quantidade de Quartos', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    Suites = st.sidebar.selectbox('Quantidade de Suites', [0, 1, 2, 3, 4, 5])
    Toilets = st.sidebar.selectbox('Quantidade de banheiros', [1, 2, 3, 4, 5, 6, 7, 8])

    if st.sidebar.checkbox('Elevador'):
        Elevator = 'yes'
    else:
        Elevator = 'no'

    if st.sidebar.checkbox('Imóvel Mobiliado'):
        Furnished = 'yes'
    else:
        Furnished = 'no'

    if st.sidebar.checkbox('Piscina'):
        Swimming_Pool = 'yes'
    else:
        Swimming_Pool = 'no'

    Parking = st.sidebar.selectbox('Vagas no Estacionamento', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    data = {'Condo': Condo,
            'Size': Size,
            'Rooms': Rooms,
            'Toilets': Toilets,
            'Suites': Suites,
            'Parking': Parking,
            'Elevator': Elevator,
            'Furnished': Furnished,
            'Swimming_Pool': Swimming_Pool,
            'Price': Price}

    sale = pd.DataFrame(data, index=[0])
    X_test = data_prep(sale)

    df_cols = ['Condo', 'Size', 'Rooms', 'Toilets',
               'Suites', 'Parking', 'Elevator', 'Furnished',
               'Swimming_Pool', 'm2']

    if st.sidebar.button('Buscar'):
        model = pickle.load(open('Modelo_GradientBoostingRegressor.pkl', 'rb'))
        ans = model.predict(sale[df_cols])
        st.subheader(f'O preço do imóvel com as características que você deseja comprar é ${np.round(ans, 2)} (INR) ')

localizacao = pd.read_csv('sao-paulo-properties-april-2019.csv')
columns = {'Price': 'Price',
           'Condo': 'Condo',
           'Size': 'Size',
           'Roomns': 'Rooms',
           'Toilets': 'Toilets',
           'Suites': 'Suites',
           'Parking': 'Parking',
           'Elevator': 'Elevator',
           'Furnished': 'Furnished',
           'SwimmingPool': 'SwimmingPool',
           'New': 'New',
           'District': 'District',
           'Negotiation Type': 'Negotiation Type',
           'Property Type': 'Property Type',
           'Latitude': 'latitude',
           'Longitude': 'longitude'}

novo = localizacao.rename(columns=columns)
st.subheader('Mapa')
if st.checkbox('Apresentar mapa'):
    st.map(novo)


