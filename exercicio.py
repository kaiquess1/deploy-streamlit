# Imports
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

@st.cache(show_spinner=True, allow_output_mutation=True)
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)


# Função para filtrar baseado na multiseleção de categorias
@st.cache(allow_output_mutation=True)
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)


@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


@st.cache
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def main():

    st.set_page_config(page_title='Telemarketing analisys', \
                       page_icon='telmarketing_icon.png',
                       layout="wide",
                       initial_sidebar_state='expanded'
                       )


    st.write('# Telemarketing analisys')
    st.markdown("---")


    image = Image.open("Bank-Branding.jpg")
    st.sidebar.image(image)

    st.sidebar.write("## Incluir arquivo")
    data_file_1 = st.sidebar.file_uploader("Procurar arquivo", type=['csv', 'xlsx'])


    if (data_file_1 is not None):
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):

            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade',
                               min_value=min_age,
                               max_value=max_age,
                               value=(min_age, max_age),
                               step=1)
            st.write('IDADES:', idades)
            st.write('IDADE MIN:', idades[0])
            st.write('IDADE MAX:', idades[1])

            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            # st.write('PROFISSÕES DISPONIVEIS:', jobs_list)
            jobs_list.append('all')
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])
            st.write('PROFISSÕES SELECIONADAS:', jobs_selected)


            bank = bank[(bank['age'] >= idades[0]) & (bank['age'] <= idades[1])]
            bank = multiselect_filter(bank, 'job', jobs_selected)

            submit_button = st.form_submit_button(label='Aplicar')

        st.write('## Após os filtros')
        st.write(bank.head())
        st.markdown("---")

        # PLOTS
        fig, ax = plt.subplots(1, 2, figsize=(5, 3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize=True).to_frame() * 100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()
        sns.barplot(x=bank_raw_target_perc.index,
                    y='y',
                    data=bank_raw_target_perc,
                    ax=ax[0])
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_title('Dados brutos',
                        fontweight="bold")

        try:
            bank_target_perc = bank.y.value_counts(normalize=True).to_frame() * 100
            bank_target_perc = bank_target_perc.sort_index()
            sns.barplot(x=bank_target_perc.index,
                        y='y',
                        data=bank_target_perc,
                        ax=ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados',
                            fontweight="bold")
        except:
            st.error('Erro no filtro')

        st.write('## Proporção de aceite')
        st.pyplot(plt)

        df = pd.DataFrame(bank)

        # st.write(df)

        @st.cache
        def convert_df(df):

            return df.to_csv().encode('utf-8')

        csv = convert_df(df)

        agr = st.download_button(
            label="Baixar o arquivo",
            data=csv,
            file_name='bank.csv',
            mime='text/csv',
        )

        if agr:
            return st.success('Arquivo baixado com sucesso!', icon="✅")
        st.balloons()

if __name__ == '__main__':
    main()










