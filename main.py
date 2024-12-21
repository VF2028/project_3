from flask import Flask, render_template, request, redirect
from dash import Dash, dcc, html, Input, Output, callback_context, ALL, ctx
import dash_leaflet
import plotly.graph_objs as go
import json
from utls.main import get_weather_data, get_city_coordinates

app = Flask(__name__)

dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

cities = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global cities
    if request.method == 'POST':
        # Получение данных из формы
        start_point = request.form['start_point']
        end_point = request.form['end_point']
        intermediate_cities = request.form.getlist('intermediate_city')

        # Обновление списка городов
        cities = [start_point, end_point] + intermediate_cities
        return redirect('/dash/')

    return render_template('index.html')

dash_app.layout = html.Div([
    html.H1("Карта маршрута", style={'textAlign': 'center'}),
    
    # Контейнер для карты и графиков погоды
    html.Div([
        dash_leaflet.Map(center=[50, 50], zoom=4, children=[
            dash_leaflet.TileLayer(),
            dash_leaflet.LayerGroup(id="markers-layer"),
            dash_leaflet.Polyline(id="route-line", positions=[])
        ], id="map", style={'width': '100%', 'height': '50vh'}),

        html.Div(id='weather-graph-container', style={'width': '100%', 'height': 'auto'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}),

    # Выпадающие списки для выбора метрики и количества дней
    html.Div([
        dcc.Dropdown(
            id='metric-dropdown',
            options=[
                {'label': 'Температура', 'value': 'temperature'},
                {'label': 'Скорость ветра', 'value': 'wind_speed'},
                {'label': 'Вероятность осадков', 'value': 'precipitation'}
            ],
            value='temperature',
            clearable=False,
            style={'width': '50%'}
        ),

        dcc.Dropdown(
            id='days-dropdown',
            options=[
                {'label': '3 дня', 'value': 3},
                {'label': '5 дней', 'value': 5}
            ],
            value=3,
            clearable=False,
            style={'width': '50%'}
        )
    ], style={'marginTop': '10px', 'display': 'flex', 'justifyContent': 'center'})
])

@dash_app.callback(
    [Output("markers-layer", "children"), Output("route-line", "positions")],
    Input('map', 'id')
)
def add_route_and_markers(_):
    city_markers = []
    route_positions = []

    for city in cities:
        coordinates = get_city_coordinates(city)
        if coordinates:
            route_positions.append(coordinates)
            marker = dash_leaflet.Marker(
                position=coordinates,
                children=[
                    dash_leaflet.Tooltip(city),
                    dash_leaflet.Popup([html.H3(city), html.P("")])
                ],
                id={'type': 'marker', 'index': city}
            )
            city_markers.append(marker)
    
    return city_markers, route_positions

@dash_app.callback(
    Output("weather-graph-container", "children"),
    [Input("metric-dropdown", "value"), Input("days-dropdown", "value")],
    Input({'type': 'marker', 'index': ALL}, 'n_clicks')
)
def update_graph(selected_metric, days, _):
    if not cities:
        return html.Div("Выберите город для отображения графиков")

    # Функция для замены значений метрик на русский язык
    def replace_value(input_str):
        mapping = {
            'temperature': 'Температура',
            'wind_speed': 'Скорость ветра',
            'precipitation': 'Вероятность осадков'
        }
        return mapping.get(input_str, input_str)

    graphs = []

    # Генерация графиков для всех городов
    for city_name in cities:
        weather_data = get_weather_data(city_name, days)
        
        if weather_data is not None:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=weather_data['date'], 
                    y=weather_data[selected_metric], 
                    mode='lines+markers', 
                    name=f'{city_name} ({replace_value(selected_metric)})'
                )
            )
            
            fig.update_layout(
                title=f'{replace_value(selected_metric)} в {city_name} за {days} дней',
                xaxis_title='Дата',
                yaxis_title='Значение',
                template='plotly_white'
            )
            
            graphs.append(dcc.Graph(figure=fig))  

    return graphs if graphs else [html.Div("Нет данных для отображения")]

if __name__ == "__main__":
    app.run(port=8000)
