import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#%%
app = dash.Dash()

elements = [
        dcc.Input(id='my-id',value='Initial Text',type='text'),
        html.Div(id='my-div',style={'border':'2px blue solid'})
        ]

app.layout=html.Div(elements)

## note callback must by after app layout
@app.callback(
            ## for output div, we choose children property, whcih is the default
            Output(component_id='my-div',component_property='children'),
            ## for input div, we choose the value property
            ## not that Input is a list of Input items 
            [Input(component_id='my-id',component_property='value')] 
            )
def update_output_div(input_value):
    return "You entered: {}".format(input_value)



if __name__ == '__main__':
    app.run_server()

