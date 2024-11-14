import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz

# Constantes para o endereço IP e porta do servidor de dados
IP_ADDRESS = "IP DA VM"
PORT_STH = 8666
DASH_HOST = "0.0.0.0"  # Define o host para "0.0.0.0", permitindo acesso de qualquer IP

# FUNÇÃO PARA PEGAR OS ATRIBUTOS DE QUALQUER SENSOR
def get_sensor_data(entity_type, entity_id, attribute, lastN):
    # URL para acessar os dados do sensor através da API
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/{entity_type}/id/{entity_id}/attributes/{attribute}?lastN={lastN}"
    
    # Headers necessários para autenticação na API FIWARE
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }

    # Faz uma requisição GET para buscar os dados do sensor
    response = requests.get(url, headers=headers)
    
    # Se a requisição foi bem-sucedida, processa os dados
    if response.status_code == 200:
        data = response.json()
        try:
            # Extrai os valores dos atributos do sensor
            values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
            return values
        except KeyError as e:
            print(f"Key error: {e}")
            return []
    else:
        # Em caso de erro na requisição, imprime a mensagem de erro
        print(f"Error accessing {url}: {response.status_code}")
        return []

# FUNÇÃO PARA CONVERTER TIMESTAMPS UTC PARA O HORÁRIO DE SÃO PAULO
def convert_to_sao_paulo_time(timestamps):
    utc = pytz.utc  # Fuso horário UTC
    sp = pytz.timezone('America/Sao_Paulo')  # Fuso horário de São Paulo
    converted_timestamps = []
    
    # Para cada timestamp, converte de UTC para o horário de São Paulo
    for timestamp in timestamps:
        try:
            # Formata a string de timestamp
            timestamp = timestamp.replace('T', ' ').replace('Z', '')
            # Converte para datetime e ajusta para o fuso horário de São Paulo
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).astimezone(sp)
        except ValueError:
            # Se não houver milissegundos no timestamp, faz a conversão sem eles
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).astimezone(sp)
        
        # Adiciona o timestamp convertido à lista
        converted_timestamps.append(converted_time)
    
    return converted_timestamps

# Instância da aplicação Dash
app = dash.Dash(__name__)

# Layout da aplicação, incluindo cabeçalhos e gráficos
app.layout = html.Div([
    html.H1('Dashboard dos sensores LDR e DHT22'),  # Título principal

    # Gráfico de Luminosidade
    html.Div([
        html.H2('Luminosity Data'),
        dcc.Graph(id='luminosity-graph'),  # Componente gráfico para Luminosidade
        dcc.Store(id='luminosity-data-store', data={'timestamps': [], 'luminosity_values': []}),  # Armazena os dados de luminosidade
    ]),

    # Gráfico de Umidade
    html.Div([
        html.H2('Humidity Data'),
        dcc.Graph(id='humidity-graph'),  # Componente gráfico para Umidade
        dcc.Store(id='humidity-data-store', data={'timestamps': [], 'humidity_values': []}),  # Armazena os dados de umidade
    ]),

    # Gráfico de Temperatura
    html.Div([
        html.H2('Temperature Data'),
        dcc.Graph(id='temperature-graph'),  # Componente gráfico para Temperatura
        dcc.Store(id='temperature-data-store', data={'timestamps': [], 'temperature_values': []}),  # Armazena os dados de temperatura
    ]),

    # Componente Interval para atualizações periódicas (a cada 10 segundos)
    dcc.Interval(
        id='interval-component',
        interval= 10 * 1000,  # Intervalo de 10.000 milissegundos (10 segundos)
        n_intervals=0  # Número inicial de intervalos
    )
])

# Callback para atualizar o armazenamento de dados de luminosidade, umidade e temperatura
@app.callback(
    [Output('luminosity-data-store', 'data'),
     Output('humidity-data-store', 'data'),
     Output('temperature-data-store', 'data')],
    Input('interval-component', 'n_intervals'),  # Dispara a cada intervalo de tempo
    State('luminosity-data-store', 'data'),  # Armazena o estado anterior dos dados de luminosidade
    State('humidity-data-store', 'data'),  # Armazena o estado anterior dos dados de umidade
    State('temperature-data-store', 'data')  # Armazena o estado anterior dos dados de temperatura
)
def update_data_store(n, stored_luminosity, stored_humidity, stored_temperature):
    # Obtém os últimos 10 dados de luminosidade
    data_luminosity = get_sensor_data('Lamp', 'urn:ngsi-ld:Lamp:003', 'luminosity', 10)
    if data_luminosity:
        luminosity_values = [float(entry['attrValue']) for entry in data_luminosity]  # Extrai os valores de luminosidade
        timestamps_luminosity = [entry['recvTime'] for entry in data_luminosity]  # Extrai os timestamps
        timestamps_luminosity = convert_to_sao_paulo_time(timestamps_luminosity)  # Converte os timestamps para horário local

        # Atualiza o armazenamento de dados com os novos valores de luminosidade
        stored_luminosity['timestamps'].extend(timestamps_luminosity)
        stored_luminosity['luminosity_values'].extend(luminosity_values)

    # Obtém os últimos 10 dados de umidade
    data_humidity = get_sensor_data('DHTSensor', 'urn:ngsi-ld:DHT:001', 'humidity', lastN=10)
    if data_humidity:
        humidity_values = [float(entry['attrValue']) for entry in data_humidity]  # Extrai os valores de umidade
        timestamps_humidity = [entry['recvTime'] for entry in data_humidity]  # Extrai os timestamps
        timestamps_humidity = convert_to_sao_paulo_time(timestamps_humidity)  # Converte os timestamps para horário local

        # Atualiza o armazenamento de dados com os novos valores de umidade
        stored_humidity['timestamps'].extend(timestamps_humidity)
        stored_humidity['humidity_values'].extend(humidity_values)

    # Obtém os últimos 10 dados de temperatura
    data_temperature = get_sensor_data('DHTSensor', 'urn:ngsi-ld:DHT:001', 'temperature', lastN=10)
    if data_temperature:
        temperature_values = [float(entry['attrValue']) for entry in data_temperature]  # Extrai os valores de temperatura
        timestamps_temperature = [entry['recvTime'] for entry in data_temperature]  # Extrai os timestamps
        timestamps_temperature = convert_to_sao_paulo_time(timestamps_temperature)  # Converte os timestamps para horário local

        # Atualiza o armazenamento de dados com os novos valores de temperatura
        stored_temperature['timestamps'].extend(timestamps_temperature)
        stored_temperature['temperature_values'].extend(temperature_values)

    # Retorna os dados atualizados para os três sensores
    return stored_luminosity, stored_humidity, stored_temperature

# Callback para atualizar o gráfico de luminosidade
@app.callback(
    Output('luminosity-graph', 'figure'),
    Input('luminosity-data-store', 'data')
)
def update_luminosity_graph(stored_luminosity):
    if stored_luminosity['timestamps'] and stored_luminosity['luminosity_values']:
        # Calcula a luminosidade média
        mean_luminosity = sum(stored_luminosity['luminosity_values']) / len(stored_luminosity['luminosity_values'])

        # Cria o traçado do gráfico de luminosidade
        trace_luminosity = go.Scatter(
            x=stored_luminosity['timestamps'],
            y=stored_luminosity['luminosity_values'],
            mode='lines+markers',  # Modo linhas com marcadores
            name='Luminosity',
            line=dict(color='red')
        )
        # Traçado para a linha média de luminosidade
        trace_mean = go.Scatter(
            x=[stored_luminosity['timestamps'][0], stored_luminosity['timestamps'][-1]],
            y=[mean_luminosity, mean_luminosity],
            mode='lines',  # Modo de linha contínua
            name='Mean Luminosity',
            line=dict(color='blue', dash='dash')  # Linha pontilhada
        )

        # Cria a figura e adiciona os traçados
        fig_luminosity = go.Figure(data=[trace_luminosity, trace_mean])
        fig_luminosity.update_layout(
            title='Luminosity Over Time',  # Título do gráfico
            xaxis_title='Timestamp',  # Título do eixo X
            yaxis_title='Luminosity',  # Título do eixo Y
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_luminosity

    return {}

# Callback para atualizar o gráfico de umidade
@app.callback(
    Output('humidity-graph', 'figure'),
    Input('humidity-data-store', 'data')
)
def update_humidity_graph(stored_humidity):
    if stored_humidity['timestamps'] and stored_humidity['humidity_values']:
        # Calcula a umidade média
        mean_humidity = sum(stored_humidity['humidity_values']) / len(stored_humidity['humidity_values'])

        # Cria o traçado do gráfico de umidade
        trace_humidity = go.Scatter(
            x=stored_humidity['timestamps'],
            y=stored_humidity['humidity_values'],
            mode='lines+markers',  # Modo linhas com marcadores
            name='Humidity',
            line=dict(color='green')
        )
        # Traçado para a linha média de umidade
        trace_mean = go.Scatter(
            x=[stored_humidity['timestamps'][0], stored_humidity['timestamps'][-1]],
            y=[mean_humidity, mean_humidity],
            mode='lines',  # Modo de linha contínua
            name='Mean Humidity',
            line=dict(color='blue', dash='dash')  # Linha pontilhada
        )

        # Cria a figura e adiciona os traçados
        fig_humidity = go.Figure(data=[trace_humidity, trace_mean])
        fig_humidity.update_layout(
            title='Humidity Over Time',  # Título do gráfico
            xaxis_title='Timestamp',  # Título do eixo X
            yaxis_title='Humidity',  # Título do eixo Y
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_humidity

    return {}

# Callback para atualizar o gráfico de temperatura
@app.callback(
    Output('temperature-graph', 'figure'),
    Input('temperature-data-store', 'data')
)
def update_temperature_graph(stored_temperature):
    if stored_temperature['timestamps'] and stored_temperature['temperature_values']:
        # Calcula a temperatura média
        mean_temperature = sum(stored_temperature['temperature_values']) / len(stored_temperature['temperature_values'])

        # Cria o traçado do gráfico de temperatura
        trace_temperature = go.Scatter(
            x=stored_temperature['timestamps'],
            y=stored_temperature['temperature_values'],
            mode='lines+markers',  # Modo linhas com marcadores
            name='Temperature',
            line=dict(color='orange')
        )
        # Traçado para a linha média de temperatura
        trace_mean = go.Scatter(
            x=[stored_temperature['timestamps'][0], stored_temperature['timestamps'][-1]],
            y=[mean_temperature, mean_temperature],
            mode='lines',  # Modo de linha contínua
            name='Mean Temperature',
            line=dict(color='blue', dash='dash')  # Linha pontilhada
        )

        # Cria a figura e adiciona os traçados
        fig_temperature = go.Figure(data=[trace_temperature, trace_mean])
        fig_temperature.update_layout(
            title='Temperature Over Time',  # Título do gráfico
            xaxis_title='Timestamp',  # Título do eixo X
            yaxis_title='Temperature',  # Título do eixo Y
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_temperature

    return {}

# Inicia o servidor da aplicação
if __name__ == '__main__':
    app.run_server(debug=True, host=DASH_HOST, port=8050)
