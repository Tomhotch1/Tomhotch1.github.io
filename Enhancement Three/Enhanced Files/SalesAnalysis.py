from dash import Dash, html, dcc, callback, Output, Input

# Configure the necessary Python module imports
import dash_leaflet as dl
import plotly.express as px
import plotly.figure_factory as ff
from dash import dash_table
from dash.dependencies import Input, Output
import base64


# Configure the plotting routines
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# import mongoDB crud module
import sales_crud
from sales_crud import SalesAnalysis

# Database user information
USER = 'Tom'
PASS = 'SNHU1234'

# Connect to database via CRUD Module
db = SalesAnalysis(USER, PASS)

# class read method must support return of list object and accept projection json input
# sending the read method an empty document requests all documents be returned
df = pd.DataFrame.from_records(db.read({}))

# MongoDB v5+ is going to return the '_id' column and that is going to have an 
# invlaid object type of 'ObjectID' - which will cause the data_table to crash - so we remove
# it in the dataframe here. The df.drop command allows us to drop the column. If we do not set
# inplace=True - it will reeturn a new dataframe that does not contain the dropped column(s)
# df.drop(columns=['_id'],inplace=True)

## Debug
# print(len(df.to_dict(orient='records')))
# print(df.columns)

# Convert 'Date' to datetime format with the correct format
df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
df['Date'] = df['Date'].dt.date

# Round columns to 2 decimal places
df.round(2)

# Convert Store to string
df['Store'] = df['Store'].astype('str')

# Convert holiday flag to boolean
df['Holiday_Flag'] = df['Holiday_Flag'].astype('bool')

# Create mean weekly sales by store
df_means = df.groupby(by='Store').mean(numeric_only=True).reset_index()
# Remove holiday flag
df_means = df_means.drop(columns=['Holiday_Flag'])
# Round means to 2 decimal places
df_means = df_means.round(2)
# Convert store back to int for sorting
df_means['Store'] = df_means['Store'].astype('int')

# Create total sales by store sorted in descending order
store_totals = df.groupby('Store')['Weekly_Sales'].sum().sort_values(ascending=False)
store_totals.round(2)
totals_fig = px.bar(x=store_totals.index,
                    y=store_totals.values,
                    labels={'x': 'Store', 'y': 'Total Sales'},
                    text=store_totals.values
)
# Update the title layout for the total sales by store graph
totals_fig.update_layout(
    title={
            'text': 'Total Sales by Store',
            'x': 0.5,
            'xanchor': 'center'
        })


# Configure a correlation matrix
corr_matrix = df.drop(columns=['Store', 'Date']).corr()
corr_fig = ff.create_annotated_heatmap(z=corr_matrix.values,
                                  x=corr_matrix.columns.tolist(),
                                  y=corr_matrix.index.tolist(),
                                  colorscale='Viridis',
                                  annotation_text=np.round(corr_matrix.values, 2),
                                  showscale=True
)
# Update the title layout for the correlation matrix
corr_fig.update_layout(
            title={
            'text' : 'Variable Correlation Matrix',
            'x':0.5,
            'xanchor': 'center'
        })

# Create a data frame to compare store growth
df_growth = df.copy()
df_growth["Year"] = pd.to_datetime(df_growth['Date']).dt.year
df_growth["Week"] = pd.to_datetime(df_growth['Date']).dt.isocalendar().week
df_growth.drop("Date", axis=1, inplace=True)



#########################
# Dashboard Layout / View
#########################
app = Dash(__name__)

# Insert the header

app.layout = [
    html.Div(id='hidden-div', style={'display':'none'}),
    html.Center(html.B(html.H1('CS-499 Dashboard: Thomas Hotchkiss'))),
    html.Hr(),

    # First row of content: full table and means for each store
    html.Div([
        # All Sales Table
        html.Div([
            html.H1(children='Weekly Sales by Store', style={'textAlign':'center'}),
            dash_table.DataTable(id='growth-table',
                    columns=[{"name": i, "id": i, "deletable": False, "selectable": False} for i in df_growth.columns],
                    data=df_growth.to_dict('records'),
                    sort_action='native',
                    filter_action='native',
                    sort_mode='single',
                    page_action='native',
                    page_current= 0,
                    page_size= 15,
                    selected_rows=[0]
            )
        ], style={'flex': '1', 'margin-right': '10px'}),

        # Means Table
        html.Div([
            html.H1(children='Mean Weekly Sales by Store', style={'textAlign':'center'}),
            dash_table.DataTable(id='means-table',
                         columns=[{"name": i, "id": i, "deletable": False, "selectable": False} for i in df_means.columns],
                         data=df_means.to_dict('records'),
                         # Set up the features for your interactive data table to 
                         # make it user-friendly for your client
                         # Added sorting and filtering by column, and a limit of 15 results per page
                         sort_action='native',
                         filter_action='native',
                         sort_mode='single',
                         page_action='native',
                         page_current= 0,
                         page_size= 15,
                         selected_rows=[0]
                        )
        ], style={'flex': '1', 'margin-right': '10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    html.Hr(),

    # Second row of content: yearly and total sales by store graphs
    html.Div([

        # Yearly sales by store
        html.Div([
            dcc.Dropdown(df['Store'].unique(), '1', id='yearly-dropdown'),
            dcc.Graph(id='store-yearly')
        ], style={'flex': '1', 'margin-right': '10px'}),

        # Total Sales by Store
        html.Div([
            dcc.Graph(id='store-totals', figure=totals_fig)
        ], style={'flex': '1'}),

        
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    html.Hr(),

    # Third row of content: the correlation matrix and weekly sales by store graph
    html.Div([
        html.Div([
            dcc.Graph(id='correlation-matrix', figure=corr_fig)
        ], style={'flex': '1', 'margin-right': '10px'}),

        html.Div([
            dcc.Dropdown(df['Store'].unique(), '1', id='weekly-dropdown'),
            dcc.Graph(id='weekly-graph')
        ], style={'flex': '2'})           

    ], style={'display': 'flex', 'justify-content': 'space-between'})
]


#############################################
# Interaction Between Components / Controller
#############################################


# This callback will update the store specific sales graph when the user selects a store.
@callback(
    Output('weekly-graph', 'figure'),
    Input('weekly-dropdown', 'value')
)
def update_weekly_graph(value):
    # Create a graph for sales by store for the full timeline
    dff = df[df['Store'] == value]
    figure = px.line(dff, x='Date', y='Weekly_Sales')
    figure_title = f"Weekly Sales for Store {value}"
    # Center and format the title
    figure.update_layout(
            title={
            'text' : figure_title,
            'x':0.5,
            'xanchor': 'center'
        })
    return figure


# This callback will update the store specific yearly sales graph when the user selects a store.
@callback(
        Output('store-yearly', 'figure'),
        Input('yearly-dropdown', 'value')
)
def update_yearly_graph(value):
    # Create a graph for sales by store for each year
    dff = df_growth[df_growth['Store'] == value]
    figure = px.line(dff, x='Week', y='Weekly_Sales', color='Year')
    figure_title = f"Weekly Sales for Store {value} by Year"
    figure.update_layout(
        title={
            'text' : figure_title,
            'x':0.5,
            'xanchor': 'center'
        },
        xaxis_title='Week',
        yaxis_title='Weekly Sales',
        legend_title='Year')
    return figure


# This callback will highlight a cell on the means table when the user selects it.
@app.callback(
    Output('means-table', 'style_data_conditional'),
    [Input('means-table', 'selected_columns')]
)
def update_styles(selected_columns):
    if selected_columns is None:
        return
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


# This callback defines the default sort logic for the means table.
@app.callback(
    Output('means-table', 'sort_by'),
    [Input('means-table', 'sort_by')]
)
def default_means_sort(sort_by):
    if not sort_by:
        return [{'column_id': 'Weekly_Sales', 'direction': 'desc'}]
    else:
        return sort_by
    

# This callback will highlight a cell on the growth table when the user selects it.
@app.callback(
    Output('growth-table', 'style_data_conditional'),
    [Input('growth-table', 'selected_columns')]
)
def update_styles(selected_columns):
    if selected_columns is None:
        return
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


if __name__ == '__main__':
    app.run(debug=True)