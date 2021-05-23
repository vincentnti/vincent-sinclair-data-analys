# Dash
import dash
import dash_core_components as dcc
import dash_html_components as HTML
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Plotly
import plotly.express as px 

# Pandas
import pandas as pd

# Hämta intressant data

def aggregate_death_per_condition(file_path, age_group):
    # Ladda in excel fil i form av en data frame
    data_frame = pd.read_excel(file_path)

    # Ta bort ointressant data 
    data_frame = data_frame[data_frame['Main pre-existing condition'] != 'All deaths involving COVID-19'] 

    # Krav för att undersöka båda kön och en åldersgrupp 
    selected_sex = data_frame['Sex'] == 'Persons'
    selected_age = data_frame['Age'] == age_group

    # Få tag på befintliga sjukdommar/inga sjukdommar och hur många som dött med dem
    pre_conditions = data_frame[selected_sex][selected_age]['Main pre-existing condition']
    deaths_per_condition = data_frame[selected_sex][selected_age]['Number of deaths']

    return pre_conditions, deaths_per_condition

def aggregate_deaths_per_period(file_path, age_group): 
    # Ladda in excel fil i form av en data frame
    data_frame = pd.read_excel(file_path, header=[0,1]) # header=[0,1] allows for sub header readings

    # Krav för att undersöka en åldersgrupp med någon typ av befintlig sjukdom
    selected_age = age_group 
    selected_conditon_amount = data_frame[('Unnamed: 1_level_0', 'Number of PRE-EXISTING CONDITIONS')] == 1 

    # Hämta tidsperioderna
    header_items = data_frame.iloc[0:0]
    periods = get_periods(header_items)

    # Hämta dödsfall under tidsperioderna
    deaths_per_period = []
    for period in periods: 
        # Hämta datan med kraven igenom rubrik och underrubriken
        temp = data_frame[selected_conditon_amount][(period, selected_age)]
        # Lägg till värdenna från England
        deaths_per_period.append(temp.values[0]) 

    # Ta bort ointressant data
    periods.remove("January to December 2020")
    deaths_per_period.remove(max(deaths_per_period)) # January to December 2020 kommer alltid vara störst


    return periods, deaths_per_period

# Sorterings verktyg 

def filter_period(item):
    # Ta ut perioden med under rubriken
    period, _ = item

    return 'Unnamed' not in period

def get_period_value(group):
    # Ta ut rubrik värdet och ignorera under rubriken
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

# Andra verktyg
def lists_to_dataframe(list1, list2, name1, name2):
    return pd.DataFrame({name1: list1, name2: list2})

# dpc står för (for deaths per condition)
# dpp står för (for deaths per period)

# Sätt fil sökvägar
DPC_FILE = "./data/pre-existing-conditions/death-amount-condition.xlsx"
DPP_FILE = "./data/pre-existing-conditions/deaths-place-time-amount-condition.xlsx"

# Definera graferna (Behöver inte fylla de med data än då update_figure() kommer gör det )
# dpc (deaths per condition)
dpc_bar_figure = px.bar()
dpc_pie_figure = px.pie()

# dpp (deaths per period)
dpp_bar_figure = px.bar()
dpp_radar_figure = px.line_polar()

# Initiera applikationen
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Bygg upp applikationens struktur
app.layout = HTML.Div(id="divider", children=[
    dbc.Jumbotron(
        [
            HTML.H1("Undersökning på covid-19 dödsfall med förhandsvillkor / utan förhandsvillkor", className="display-3"),
            HTML.P(
                "Data från www.ons.gov.uk",
                className="lead",
            ),
            HTML.Hr(className="my-2"),
            HTML.P(
                "Scrolla ner för att kolla diagrammen"
            )
        ]
    ),
    HTML.H1(children = "Antal Covid-19 dödsfall med förhandsvillkor / utan förhandsvillkor i vald åldersgrupp"),
    dcc.Dropdown(
        id="dpc_drop",
        options = [
            dict(label="90+ år gamla", value="90+"),
            dict(label="Mellan 85-89 år gamla", value="85-89"),
            dict(label="Mellan 80-84 år gamla", value="80-84"),
            dict(label="Mellan 75-79 år gamla", value="75-79"),
            dict(label="Mellan 70-74 år gamla", value="70-74"),
            dict(label="Mellan 65-69 år gamla", value="65-69"),
            dict(label="Mellan 60-64 år gamla", value="60-64"),
            dict(label="Mellan 55-59 år gamla", value="55-59"),
            dict(label="Mellan 50-54 år gamla", value="50-54"),
            dict(label="Mellan 45-49 år gamla", value="45-49"),
            dict(label="Mellan 0-44 år gamla", value="0-44"),
        ],
        value="65-69" # Start urval 
    ),
    dcc.Graph(
        id="dpcbar",
        figure=dpc_bar_figure
    ),
    dcc.Graph(
        id="dpcpie",
        figure=dpc_pie_figure,
    ),
    HTML.H1(children = "Antal Covid-19 dödsfall i vald åldersgrupp med ett förhandsvillkor under olika tids perioder"),
    dcc.Dropdown(
        id="dpp_drop",
        options = [
            dict(label="Mellan 1-64 år gamla", value="Aged 1-64 years"),
            dict(label="65+ år gamla", value="Aged 65 and over")
        ],
        value="Aged 65 and over" # Start urval
    ),
    dcc.Graph(
        id="dppbar",
        figure=dpp_bar_figure
    ),
    dcc.Graph(
        id="dppradar",
        figure=dpp_radar_figure
    )
],
style={
    'margin': '50px'
})

# Applikation Input Output 
@app.callback(
    [
        # För dpc (deaths per condition) diagrammen 
        Output("dpcbar", "figure"),
        Output("dpcpie", "figure"),

        # För dpp (deaths per period) diagrammen
        Output("dppbar", "figure"),
        Output("dppradar", "figure")
    ],
    [
        # För dpc (deaths per period) diagrammen 
        Input("dpc_drop", "value"),
        Input("dpc_drop", "value"),

        # För dpp (deaths per period) diagrammen
        Input("dpp_drop", "value"),
        Input("dpp_drop", "value")
    ]
)

# Uppdatera figurer med data beroende på urval
def update_figure(dpc_value, a, dpp_value, b):
    # Hämta listor för (deaths per condition) med intressant data 
    pre_conditions, deaths_per_condition = aggregate_death_per_condition(DPC_FILE, dpc_value)

    # Konvertera listorna för (deaths per condition) till en dataframe
    df_dpc = lists_to_dataframe(pre_conditions, deaths_per_condition, "Pre-conditions", "Deaths per condition")
    
    # Med den skapade data framen skapa sedan figurerna
    dpc_bar_figure = px.bar(df_dpc, x="Pre-conditions", y="Deaths per condition")
    dpc_pie_figure = px.pie(df_dpc, names="Pre-conditions", values="Deaths per condition")



    # Hämta listor för (deaths per period) med intressant data och skapa en data frame med dem
    periods, deaths_per_period = aggregate_deaths_per_period(DPP_FILE, dpp_value)

    # Konvertera listorna för (deaths per period) till en dataframe
    df_dpp = lists_to_dataframe(periods, deaths_per_period, "Periods", "Deaths per period")

    # Med den skapade data framen skapas sedan figurerna
    dpp_bar_figure = px.bar(df_dpp, x="Periods", y="Deaths per period")
    dpp_radar_figure = px.line_polar(df_dpp, r="Deaths per period", theta="Periods", line_close=True)

    # Returnera skapade figurerna 
    return dpc_bar_figure, dpc_pie_figure, dpp_bar_figure, dpp_radar_figure

if __name__ == "__main__":
    app.run_server(debug = True)