#######
# This uses a small wheels.csv dataset
# to demonstrate multiple outputs.
######
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import base64   ## to encode images


df = pd.read_csv('../data/wheels.csv')
app = dash.Dash()

def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())

elements = [
                dcc.RadioItems(
                    id='wheels',
                    options=[{'label': i, 'value': i} for i in df['wheels'].unique()],
                    value=1
                ),
                        
                html.Div(id='wheels-output'),
                html.Hr(),  # add a horizontal rule
                dcc.RadioItems(
                    id='colors',
                    options=[{'label': i, 'value': i} for i in df['color'].unique()],
                    value='blue'
                ),
                html.Div(id='colors-output'),
                ## specify a image tag, give src as children, so that it is easier to write to
                html.Img(id='display-image',src='children',height=300)
                
            ]

app.layout=html.Div(elements,style={'fontFamily':'helvetica', 'fontSize':18})

@app.callback(
        Output('wheels-output','children'),
        [Input('wheels','value')]
        )
def callback_a(wheels_value):
    return "you chose {}".format(wheels_value)

@app.callback(
        Output('colors-output','children'),
        [Input('colors','value')]
        )
def callback_b(colors_value):
    return "you chose {}".format(colors_value)

@app.callback(
        Output('display-image','src'),
        [
         Input('wheels','value'),
         Input('colors','value')
         ]
        )
def callback_image(wheel,color):
    path = '../data/images/'
    return encode_image(path+df[(df['wheels']==wheel) & \
                                (df['color']==color)]['image'].values[0])

if __name__ == '__main__':
    app.run_server()

