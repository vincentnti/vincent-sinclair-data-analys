import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as HTML
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np



app = dash.Dash(__name__)

# Mockup data

TE19 = np.random.randint(50,100,34)
NA19 = np.random.randint(30,100,30)

df_TE19 = pd.DataFrame({"Närvaro":TE19})
df_NA19 = pd.DataFrame({"Närvaro":NA19})

# Create figure
fig = px.bar(df_TE19, y ="Närvaro", title="Närvarograd i procent")


# Layout
app.layout = HTML.Div(children = [
    HTML.H1(children = "Ost"),
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