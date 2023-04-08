import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO

custom_params = { "axes.spines.right": False, "axes.spines.top":False}

@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')
@st.cache
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output,engine = 'xlswriter')
    df.to_excel(writer,index=False,sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def recencia_class(x, r, q_dict):
    """Classifica como melhor o menor quartil
    X= valor da linha,
    R=recencia,
    q_dict=quartil dicionario
    """
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'


def freq_val_class(x, fv, q_dict):
    """Classifica como melhor o maior quartil
    x= valor da linha,
    fv=frequencia ou valor,
    q_dict=quartil dicionario
    """
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'
def main():

    st.set_page_config(page_title='RFV', \
                       layout="wide",
                       initial_sidebar_state='expanded'
                       )


    st.markdown("""# RFV 
    RFV significa recência, frequência,valor é utilizado 
    para segmentação de clientes baseados no comportamento de compras dos clientes e 
    agrupa-los em clusters parecidos. Utilizando esse tipo de agrupamento podemos realizar ações de marketing
    e CRM melhores direcionados, ajudando assim na personalização de conteúdo e até retenção de clientes.
    
    Para cada cliente é preciso calcular cada uma das componentes abaixo:
    
    - **Recência (R)** : Quantidade de dias desde a última compra;
    - **Frequência (F)** : Quantidade total de compras nio período;
    - **Valor (V)** : Total de dinheiro gasto nas compras do período;
 
    
             """)
    st.markdown("---")


    #image = Image.open("Bank-Branding.jpg")
    #st.sidebar.image(image)

    st.sidebar.write("## Incluir arquivo")
    data_file_1 = st.sidebar.file_uploader("Procurar arquivo", type=['csv', 'xlsx'])

    if (data_file_1 is not None):
        df_compras = pd.read_csv(data_file_1,infer_datetime_format=True,parse_dates=['DiaCompra'])

        st.write('## Recência (R)')

        dia_atual = df_compras['DiaCompra'].max()
        st.write('Dia máximo na base de dados:', dia_atual)


        st.write('Quantos dias faz que o cliente fez a sua última compra ?')

        df_recencia = df_compras.groupby(by='ID_cliente',as_index=False)['DiaCompra'].max()
        df_recencia.columns = ['ID_cliente','DiaUltimaCompra']
        df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(lambda x : (dia_atual - x).days)
        st.write(df_recencia.head())


        df_recencia.drop('DiaUltimaCompra',axis=1,inplace=True)

        st.write('## Frequência (F)')
        st.write('Quantas vezes cada cliente comprou com a gente?')
        df_frequencia = df_compras[['ID_cliente','CodigoCompra']].groupby('ID_cliente').count().reset_index()
        df_frequencia.columns = ['ID_cliente','Frequencia']
        st.write(df_frequencia.head())


        st.write('## Valor (V)')
        st.write('Quanto que cada cliente gastou no período?')
        df_valor = df_compras[['ID_cliente','ValorTotal']].groupby('ID_cliente').sum().reset_index()
        df_valor.columns = ['ID_cliente','Valor']
        st.write(df_valor.head())

        st.write('## Tabela RFV final')
        df_RF = df_recencia.merge(df_frequencia, on='ID_cliente')
        df_RFV = df_RF.merge(df_valor, on='ID_cliente')
        df_RFV.set_index('ID_cliente', inplace=True)
        st.write(df_RFV.head())


        st.write('## Segmentação utilizando o RFV')


        st.write("""
        Um jeito de segmentar os clientes é criando quartis para cada componente do RFV, sendo que o melhor quartil é chamado de 'A', o segundo melhor quartil de 'B', o terceiro melhor de 'C' e o pior de 'D'. O melhor e o pior depende da componente. Po exemplo, quanto menor a recência melhor é o cliente (pois ele comprou com a gente tem pouco tempo) logo o menor quartil seria classificado como 'A', já pra componente frêquencia a lógica se inverte, ou seja, quanto maior a frêquencia do cliente comprar com a gente, melhor ele/a é, logo, o maior quartil recebe a letra 'A'.
Se a gente tiver interessado em mais ou menos classes, basta a gente aumentar ou diminuir o número de quantils pra cada componente.
""")

        st.write("## Quartis para o RFV ")
        quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
        st.write(quartis)


        st.write('Tabela após a criação dos grupos')

        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class,
                                                       args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class,
                                                         args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class,
                                                    args=('Valor', quartis))


        df_RFV['RFV_score'] = (df_RFV.R_quartil + df_RFV.F_quartil +
                               df_RFV.V_quartil)
        st.write(df_RFV.head())

        st.write('Quantidade de cliente por grupos')
        st.write(df_RFV['RFV_score'].value_counts())


        st.write('#### Clientes com menor recência, maior frequência e maior valor gasto')
        st.write(df_RFV[df_RFV['RFV_score'] == 'AAA'].sort_values('Valor',
                                                         ascending=False).head(10))


        st.write('### Ações de marketing/CRM')

        dict_acoes = {
            'AAA':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'ABA':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'ABB':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'DDD':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CCB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CBA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CDC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'AAB':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'ABC':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'DCD':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'BBA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BCC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BCB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DAA':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'DBC':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'BDB':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'CDD':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'CAA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CBB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DCB':
                'Churn! Cliente que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
            'BAA':
                'Enviar cupons de desconto,Pedir para indicar nosso produto para algum amigo, Ao lançar um novo produto enviar amostrar grátis pra esses.',
            'CCC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DCC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BBC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ACB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BBB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BDC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BDD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ADD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ADC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ACD':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CDB':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'DCA':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'DDB':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CBC':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CBD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BBD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ACC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'ABD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BAB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BCD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CCA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CCD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BCA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DBB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'CAB':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DBD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DBA':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CDA':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'DDA':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'ADB':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'ACA':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'DAB':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'AAC':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',
            'BDA':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'CAC':
                'Churn! Clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
            'AAD':
                'Cliente com perfil moderado. Enviar cupons para incentivar consumo',

        }

        df_RFV['acções_marketing'] = df_RFV['RFV_score'].map(dict_acoes)
        st.write(df_RFV.head(10))




        st.write('Quantidade de clientes por tipos de ação')
        st.write(df_RFV['acções_marketing'].value_counts())

        @st.cache
        def convert_df(df):

            return df.to_csv().encode('utf-8')

        csv = convert_df(df_RFV)

        agr = st.download_button(
            label="Baixar o arquivo",
            data=csv,
            file_name='arquivo_RFV.csv',
            mime='text/csv',
        )

        if agr:
            return st.success('Processo finalizado com sucesso!', icon="✅")
        st.balloons()


if __name__ == '__main__':
    main()










