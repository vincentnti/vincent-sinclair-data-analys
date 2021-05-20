import dash
import dash_core_components as dcc
import dash_html_components as HTML
from dash.dependencies import Input, Output

import plotly.express as px

import pandas as pd
import numpy as np

# Data
def aggregate_death_per_condition(file_path, group):
    data_frame = pd.read_excel(file_path)
    data_frame = data_frame[data_frame['Main pre-existing condition'] != 'All deaths involving COVID-19'] # Removal of non useful data

    selected_sex = data_frame['Sex'] == 'Persons'
    selected_age = data_frame['Age'] == group 

    pre_conditions = data_frame[selected_sex][selected_age]['Main pre-existing condition']
    deaths_per_condition = data_frame[selected_sex][selected_age]['Number of deaths']

    #return pre_conditions, deaths_per_condition
    return data_frame


def aggregate_deaths_per_period(file_path, group): 
    data_frame = pd.read_excel(file_path, header=[0,1]) # header=[0,1] allows for sub header readings

    selected_age = group 
    selected_conditon_amount = data_frame[('Unnamed: 1_level_0', 'Number of PRE-EXISTING CONDITIONS')] == 1 

    header_items = data_frame.iloc[0:0]
    periods = get_periods(header_items)

    deaths_per_period = []
    for period in periods: 
        temp = data_frame[selected_conditon_amount][(period, selected_age)]
        deaths_per_period.append(temp.values[0]) # Adding values from England

    return periods, deaths_per_period

# Tools
def filter_period(item):
    period, _ = item

    return 'Unnamed' not in period

def get_period_value(group):
    value, _ = group

    return  value 

def get_periods(header_items):
    # Sortera bort dom namnlösa cellerna
    temp = list(filter(filter_period, header_items))

    # Få tag på period namnen
    temp = map(get_period_value, temp)  
    
    # Sortera bort dubbleter
    temp = set(temp) 

    return list(temp) 

# temporary
#pre_conditions, deaths_per_condition
framiuz = aggregate_death_per_condition("./data/pre-existing-conditions/death-amount-condition.xlsx", "90+")
deaths_per_condition_bar = px.bar(framiuz, y="Age")
#deaths_per_condition_pie = px.pie(deaths_per_condition, pre_conditions)

periods, deaths_per_period = aggregate_deaths_per_period("./data/pre-existing-conditions/deaths-place-time-amount-condition.xlsx", "Aged 65 and over")
deaths_per_period_bar = px.bar(periods, deaths_per_period)
deaths_per_period_pie = px.pie(deaths_per_period, periods)

app = dash.Dash() #Name required?

app.layout = HTML.Div( id="divider", children = [
    HTML.H1(children = "Conditions before death"),
    dcc.Dropdown(
        id = "drop",
        options = [
            #dict(label="85-89 Years old", value="85-89"),
            #dict(label="80-84 Years old ", value="80-84"),
            #dict(label="75-49 Years old ", value="75-79"),
            #dict(label="70-74 Years old ", value="70-74"),
            #dict(label="65-69 Years old ", value="65-69"),
            #dict(label="60-64 Years old ", value="60-64"),
            #dict(label="55-59 Years old ", value="55-59"),
            #dict(label="50-54 Years old ", value="50-54"),
            #dict(label="45-49 Years old ", value="45-49"),
            dict(label="0-44 Years old ", value="0-44")
        ]
    ),
    dcc.Graph(
        id="dpc_pie_chart",
        figure=deaths_per_condition_bar
    )
])

@app.callback(
    Output("graph", "figure"),
    [Input("drop", "value")] 
)

def update_figure(value):
    pass

if __name__ == "__main__":
    app.run_server(debug = True)

"""
dcc.Graph(
id="dpc_pie_chart",
figure=deaths_per_condition_pie
)
dcc.Dropdown(
id = "drop_period_age_group",
options = [
dict(label="Aged 65 and over", value="Aged 65 and over"),
dict(label="Aged 1-64 years", value="Aged 1-64 years")
]
),
dcc.Graph(
    id="dpp_bar_chart",
    figure=deaths_per_period_bar
),
dcc.Graph(
    id="dpp_pie_chart",
    figure=deaths_per_period_pie 
),
"""
"""
# Mockup data

TE19 = np.random.randint(50,100,34)
NA19 = np.random.randint(30,100,30)

df_TE19 = pd.DataFrame({"Närvaro":TE19})
df_NA19 = pd.DataFrame({"Närvaro":NA19})

# Create figure
fig = px.bar(df_TE19, y ="Närvaro", title="Närvarograd i procent")

app = dash.Dash(__name__)

# Layout
app.layout = HTML.Div(children = [
    HTML.H1(children = "Conditions before death"),
    dcc.Dropdown(
        id = "drop",
        options = [dict(label = "TE19", value="TE19"), dict(label = "NA19", value="NA19")]
    ),
    dcc.Graph(
        id="graph",
        figure = fig
    ),
    dcc.Graph(
        id="graph2",
        figure = fig
    ),
    dcc.Graph(
        id="graph3",
        figure = fig
    ),
    dcc.Graph(
        id="graph4",
        figure = fig
    )
])

# Logic
@app.callback(
    Output("graph", "figure"),
    [Input("drop", "value")] 
)

def update_figure(value):
    if value == "TE19": df =df_TE19
    elif value == "NA19": df = df_NA19

    fig = px.bar(df, y="Närvaro", title=f"Närvarograd för klass {value}")
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run_server(debug = True)
"""