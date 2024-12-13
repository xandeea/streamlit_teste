import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

# Lista de URLs a ser percorrida
urls = [
    'https://www.ogol.com.br/jogador/diego-rocha/175564?search=1',
    'https://www.ogol.com.br/jogador/lucio/106211',
    'https://www.ogol.com.br/jogador/vini-santos/236278?search=1',
    'https://www.ogol.com.br/jogador/augusto-pedra/586269?search=1',
    'https://www.ogol.com.br/jogador/vinicius-silva/619709',
    'https://www.ogol.com.br/jogador/vinicius-lima/464152?search=1',
    'https://www.ogol.com.br/jogador/felipe-cordeiro/111463?search=1',
    'https://www.ogol.com.br/jogador/gabriel-biteco/454840?search=1',
    'https://www.ogol.com.br/jogador/sampson/218388?search=1',
    'https://www.ogol.com.br/jogador/allan/187761?search=1',
    'https://www.ogol.com.br/jogador/jean-roberto/450999?search=1',
    'https://www.ogol.com.br/jogador/rafinha/562240?search=1',
    'https://www.ogol.com.br/jogador/edson-silva/603000?search=1',
    'https://www.ogol.com.br/jogador/wesley-pratti/708117?search=1',
    'https://www.ogol.com.br/jogador/franklin/256505?search=1',
    'https://www.ogol.com.br/jogador/cafe/427017',
    'https://www.ogol.com.br/jogador/mario/978217',
    'https://www.ogol.com.br/jogador/tom-farias/250654?search=1'
]

# Lista para armazenar os DataFrames de cada jogador
dfs_jogadores = []

# Iterar sobre cada URL
for url_completa in urls:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    response = requests.get(url_completa, headers=headers)
    response.raise_for_status()

    # Criar o objeto BeautifulSoup para a página do jogador
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extrair o nome
    nome = soup.find('div', class_='zz-enthdr-data').find('span', class_='name').get_text(strip=True)

    # Extrair a idade e a posição
    info = soup.find('div', class_='info').get_text(separator="|").split('|')

    # Remover o "m" da posição e da idade, se existir
    idade = info[1].strip() if len(info) > 1 else ''
    idade = idade.replace('m', '').strip()  # Remover "m" da idade

    if 'anos' in idade:
        idade = idade.replace('anos', '').strip()  # Remover a palavra "anos"

    # Verificar se a idade é numérica
    idade = int(idade) if idade.isdigit() else 0  # Converter para inteiro

    posicao = info[3].strip() if len(info) > 2 else ''
    posicao = posicao.replace('m', '').strip()  # Remover "m" da posição

    # Encontrar a div com a classe 'footer'
    footer_div = soup.find('div', class_='footer')

    # Encontrar o elemento <a> dentro dessa div
    link = footer_div.find('a')
    href = link['href'] if link else None

    # URL base
    url_base = 'https://www.ogol.com.br'

    # URL completa
    url_completa_stats = url_base + href if href else None

    if url_completa_stats:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }
        response_stats = requests.get(url_completa_stats, headers=headers)
        response_stats.raise_for_status()

        # Criar o objeto BeautifulSoup para a página de estatísticas
        soup_stats = BeautifulSoup(response_stats.text, 'html.parser')

        # Procurar diretamente pelos <td> com a classe 'totals'
        totais = soup_stats.find_all('td', class_='totals')
        if totais:
            dados_totais = [td.get_text(strip=True) for td in totais]

            # Remover as colunas vazias (1 e 16)
            dados_totais = dados_totais[1:-1]

            # Criar um DataFrame com os dados
            nomes_colunas = [
                'Jogos', 'Vitórias', 'Empates', 'Derrotas', 'Saldo de Gols',
                'Minutos', 'Titulares', 'Reserva Utilizado', 'Gols Marcados', 'Assistências',
                'Gols Contra', 'Cartões Amarelos', 'Segundos Amarelos', 'Cartões Vermelhos'
            ]
            df = pd.DataFrame([dados_totais], columns=nomes_colunas)

            # Adicionar nome, idade e posição como novas colunas no início
            df.insert(0, 'Nome', nome)
            df.insert(1, 'Idade', idade)
            df.insert(2, 'Posição', posicao)

            # Adicionar o DataFrame do jogador à lista
            dfs_jogadores.append(df)

# Concatenar todos os DataFrames dos jogadores em um único DataFrame
df_final = pd.concat(dfs_jogadores, ignore_index=True)

df_final['Minutos'] = pd.to_numeric(df_final['Minutos'], errors='coerce').fillna(0).astype(int)

# Adicionar o nome do time fixo
time_fixo = "Bagé"  # Altere para o nome do time

# Adicionar a coluna 'Time'
df_final['Time'] = time_fixo

# Título do app
st.title("Análise de Jogadores - Bagé FC")

# Subtítulo
st.subheader("Adicione novos jogadores ao gráfico interativo")

# Gráfico inicial
def plot_graph(df, novo_jogador=None):
    plt.figure(figsize=(10, 6))
    
    # Scatterplot para jogadores atuais (Bagé em preto)
    sns.scatterplot(data=df[df['Time'] == 'Bagé'], x="Idade", y="Minutos", hue="Time", palette=['black'], s=100, legend=False)
    
    # Adicionar o novo jogador (em amarelo)
    if novo_jogador is not None:
        plt.scatter(
            novo_jogador['Idade'], novo_jogador['Minutos'], 
            color='yellow', s=200, marker='*', label=f"Novo Jogador ({novo_jogador['Nome']})"
        )
    
    plt.title("Minutos em Campo vs Idade")
    plt.xlabel("Idade")
    plt.ylabel("Minutos em Campo")
    plt.legend()
    st.pyplot(plt)

# Mostrar gráfico inicial
st.write("### Gráfico Atual")
plot_graph(df_final)

# Entrada de URL
st.write("### Adicionar Novo Jogador")
url = st.text_input("Insira o link do jogador do site ogol.com.br:")

if st.button("Adicionar Jogador"):
    if url:
        try:
            # Função para extrair informações do jogador
            def extrair_dados_jogador(url):
                headers = {'user-agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                nome = soup.find('div', class_='zz-enthdr-data').find('span', class_='name').get_text(strip=True)
                info = soup.find('div', class_='info').get_text(separator="|").split('|')

                idade = info[1].strip() if len(info) > 1 else ''
                idade = idade.replace('m', '').strip()
                if 'anos' in idade:
                    idade = idade.replace('anos', '').strip()  # Remover a palavra "anos"

                # Verificar se a idade é numérica
                idade = int(idade) if idade.isdigit() else 0  # Converter para inteiro
                
                minutos = soup.find('td', class_='totals').get_text(strip=True)
                minutos = int(minutos.replace('.', '')) if minutos.isdigit() else 0
                
                return {'Nome': nome, 'Idade': int(idade), 'Minutos': minutos, 'Posição': 'Desconhecida', 'Time': 'Novo Jogador'}

            # Extraindo informações do novo jogador
            novo_jogador = extrair_dados_jogador(url)
            novo_jogador_df = pd.DataFrame([novo_jogador])
            
            # Atualizar DataFrame
            df_final = pd.concat([df_final, novo_jogador_df], ignore_index=True)
            
            df_final['Minutos'] = pd.to_numeric(df_final['Minutos'], errors='coerce').fillna(0).astype(int)
            
            # Atualizar gráfico
            st.success(f"Jogador {novo_jogador['Nome']} adicionado com sucesso!")
            plot_graph(df_final, novo_jogador)
        except Exception as e:
            st.error(f"Erro ao processar a URL: {e}")
    else:
        st.warning("Por favor, insira um link válido.")