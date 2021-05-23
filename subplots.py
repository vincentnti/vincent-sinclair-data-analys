import pandas as pd

# Graphing
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

class VisualizerManager:
    charts = []
    container: plotly.graph_objs.Figure
    data_frame: pd.DataFrame 

    def __init__(self):
        self.__setup_container()
        self.__setup_layout_axis_titles()
    
    def __setup_container(self):
        self.container = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                'Antal Covid-19 dödsfall med/utan förhandsvillkor (Mellan 65-69 år gamla) ',
                'Antal Covid-19 dödsfall med ett förhandsvillkor under olika tids perioder (65+ år gamla)',
                'Antal Covid-19 dödsfall med/utan förhandsvillko (Mellan 65-69 år gamla)',
                'Antal Covid-19 dödsfall med ett förhandsvillkor under olika tids perioder (65+ år gamla)',
            ),
            specs=[
                [{'type': 'xy'}, {'type': 'xy'}],
                [{'type': 'domain'}, {'type': 'domain'}]
            ]
        )
    
    def __setup_layout_axis_titles(self):
        # Axel titlar för första grafen 
        self.container['layout']['xaxis']['title']='Conditions'
        self.container['layout']['yaxis']['title']='Number of deaths'

        # Axel titlar för andra grafen
        self.container['layout']['xaxis2']['title']='Periods'
        self.container['layout']['yaxis2']['title']='Number of deaths'

    def add_data_chart(self, dv):
        self.charts.append(dv)
    
    def show(self):
        # Måla upp alla Diagram
        for chart in self.charts:
            chart.draw(self.container)
        self.container.show()

class BarChart():
    xdata: pd.DataFrame 
    ydata: pd.DataFrame

    row: int
    col: int

    def __init__(self, xdata, ydata, row, col):
        # Koppla data till attributen
        self.xdata = xdata
        self.ydata = ydata

        # Positionering i subplot
        self.row = row
        self.col = col

    def draw(self, container):
        # Lägg till spår för att måla upp Diagrammet
        container.add_trace(
            go.Bar(x=self.xdata,y=self.ydata),
            row=self.row,
            col=self.col
        )

class PieChart():
    label_data: pd.DataFrame
    value_data: pd.DataFrame

    row: int
    col: int

    def __init__(self, label_data, value_data, row, col):
        # Koppla data till attributen
        self.label_data = label_data
        self.value_data = value_data

        # Positionering i subplot
        self.row = row
        self.col = col

    def draw(self, container):
        # Lägg till spår för att måla upp Diagrammet
        container.add_trace(
            go.Pie(labels=self.label_data, values=self.value_data),
            row=self.row,
            col=self.col
        )

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

def aggregate_death_per_condition(file_path):
    # Ladda in excel fil i form av en data frame
    data_frame = pd.read_excel(file_path)

    # Ta bort ointressant data 
    data_frame = data_frame[data_frame['Main pre-existing condition'] != 'All deaths involving COVID-19'] 

    # Krav för att undersöka båda kön och en åldersgrupp 
    selected_sex = data_frame['Sex'] == 'Persons'
    selected_age = data_frame['Age'] == '65-69'

    # Få tag på befintliga förhandsvillkor/icke förhandsvillkor och hur många som dött med dem
    pre_conditions = data_frame[selected_sex][selected_age]['Main pre-existing condition']
    deaths_per_condition = data_frame[selected_sex][selected_age]['Number of deaths']

    return pre_conditions, deaths_per_condition

def aggregate_deaths_per_period(file_path): 
    # Ladda in excel fil i form av en data frame
    data_frame = pd.read_excel(file_path, header=[0,1]) # header=[0,1] allows for sub header readings

    # Krav för att undersöka en åldersgrupp med någon typ av förhandsvillkor
    selected_age = 'Aged 65 and over'
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

    return periods, deaths_per_period

def main():
    vm = VisualizerManager()

    # Hämta data och lägg till diagram 
    pre_conditions, deaths_per_condition = aggregate_death_per_condition('./data/pre-existing-conditions/death-amount-condition.xlsx')
    vm.add_data_chart(BarChart(pre_conditions, deaths_per_condition, 1, 1))
    vm.add_data_chart(PieChart(pre_conditions, deaths_per_condition, 2, 1))

    # Hämta data och lägg till diagram
    periods, monthly_deaths = aggregate_deaths_per_period('./data/pre-existing-conditions/deaths-place-time-amount-condition.xlsx')
    vm.add_data_chart(BarChart(periods, monthly_deaths, 1, 2))
    vm.add_data_chart(PieChart(periods, monthly_deaths, 2, 2))

    # Visa diagrammen
    vm.show()

# Kör main() ifall filen körs direkt
if __name__ == '__main__':
    main()