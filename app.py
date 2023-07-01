# dashtools requirements
import pathlib

# import packages
import random
import dash
import dash_cool_components
from dash import dcc, html, callback_context
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd

from data_ingest import RecipeSearch

pd.options.mode.chained_assignment = None

recipe_df = pd.read_csv(r"resources/recipes_database.csv", header=0)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY, r"css/main.css"], update_title=None)
app.title = 'Recipe Finder'
server = app.server

input_size = "md"
input_class = "py-2"
color_options = ["primary", "secondary", "success", "info", "warning", "danger"]

app.layout = dbc.Container(
    id="app-container",
    style={'padding': '3vh 10vh 8vh 10vh'},
    children=[
        html.Div(
            id="header-area",
            children=[
                html.H1(
                    id="header-title",
                    children="Recipe Finder"),
                html.P(
                    children=[
                        html.P([
                            "Unlock a world of delicious possibilities by simply entering the ingredients "
                            "you have at home.",
                            html.Br(),
                            "You can search multiple ingredients and the app will suggest recipes tailored "
                            "to you.",
                        ])
                    ]
                )
            ],
            style={
                "margin-bottom": "30px",
            }
        ),
        html.Div(
            id="menu-area",
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            dash_cool_components.TagInput(
                                id="ingredients-input",
                                placeholder="Type ingredients and hit enter...",
                                wrapperStyle={"position": "inherit",
                                              "transform": "inherit"}
                            ), width=12, className=input_class
                        ),
                        dbc.Col(
                            dbc.Button('Search',
                                       id='search-btn',
                                       disabled=False,
                                       n_clicks=0,
                                       color="primary"
                                       ),
                            width="auto", className=input_class
                        ),
                        dbc.Col(
                            dbc.Button('Pick a random one for me!',
                                       id='random-btn',
                                       disabled=True,
                                       n_clicks=0,
                                       color="secondary"
                                       ),
                            width="auto", className=input_class
                        ),
                        dbc.Alert("Write an ingredient and press Enter before clicking search", id="search-warning",
                                  color="warning", dismissable=True, is_open=False, fade=True),
                        dbc.Alert("No results found. Try more ingredients or check spelling", id="search-alert",
                                  color="danger", dismissable=True, is_open=False, fade=True)
                    ]
                )
            ]
        ),
        dbc.Row(id="recipe-output"),
        # html.Footer("This is a danger alert. Scary!", style={"position": "absolute", "bottom": "10px", "left": "40%"})
    ]
)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <script src="https://kit.fontawesome.com/bec780fc18.js" crossorigin="anonymous"></script>
        {%metas%}
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div id="content-wrapper">
            {%app_entry%}
        </div>
        <footer>
            <div id="button-wrapper">
                <div id="icons">
                    <a href="https://github.com/lvlarco/recipe_app" target="_blank" class="fa-brands fa-github"></a>
                    <a href="https://lvlarco.github.io/contact" target="_blank" class="fa-solid fa-envelope"></a>
                </div>
                <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="lvlarco" data-color="#FFDD00" data-emoji="" data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff"></script>
            </div>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            #content-wrapper {
                min-height: calc(100% - 50px);
                padding-bottom: 50px;
            }
            #button-wrapper {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #f8f8f8;
                padding: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            #icons {
                display: flex;
                align-items: center
            }
            #icons a.fa-github:before,
            #icons a.fa-envelope:before {
                font-size: 200%;
                margin-left: 30px;
                text-decoration: none;
            }
        </style>
    </body>
</html>
'''


@app.callback(
    [Output(component_id="recipe-output", component_property="children"),
     Output(component_id="search-warning", component_property="is_open"),
     Output(component_id="search-alert", component_property="is_open"),
     Output(component_id="random-btn", component_property="disabled")],
    Input(component_id="search-btn", component_property="n_clicks"),
    Input(component_id="random-btn", component_property="n_clicks"),
    State(component_id="ingredients-input", component_property="value"),
    prevent_initial_call=True
)
def ingredient_search_callback(_, __, ing_dict: list) -> list:
    """Returns a dataframe that is filtered by the search of ingredients"""
    if ing_dict is None:
        warning_in_on, alert_is_on, random_btn_disabled = True, False, True
        return [list(), warning_in_on, alert_is_on, random_btn_disabled]
    ing_list = list()
    for i in range(len(ing_dict)):
        ing = ing_dict[i].get("displayValue")
        ing_list.append(ing)
    rs = RecipeSearch(recipe_df, ing_list)
    if rs.recipe_search_df.empty:
        warning_in_on, alert_is_on, random_btn_disabled = False, True, True
        return [list(), warning_in_on, alert_is_on, random_btn_disabled]
    recipe_dict = rs.recipe_search_dict
    ing_df = rs.ingredients_df
    recipe_card_list = create_recipe_card(recipe_dict, ing_df)
    if callback_context.triggered_id == "random-btn":
        recipe_card_list = random.choice(recipe_card_list)
    return [recipe_card_list, False, False, False]


def create_recipe_card(recipe_dict: dict, ingredients_df: pd.DataFrame) -> list:
    """Creates a list of dbc.Card objects for every result from the search callback"""
    recipe_layout = [
        dbc.Col(
            children=[
                dbc.Card(
                    [
                        dbc.CardHeader(
                            html.A(
                                html.H4(f"""{recipe_dict.get("name").get(i).title()}"""),
                                href=f"""{recipe_dict.get("link").get(i)}""",
                                target="_blank",
                                style={"text-decoration": "none"}
                            )
                        ),
                        dbc.ListGroup(
                            create_ingredients_layout_list(ingredients_df.iloc[i])
                        ),
                        dbc.CardFooter(
                            [
                                dbc.Row(
                                    [
                                        dcc.Markdown(
                                            f'''
                                    *{recipe_dict.get("servings").get(i)} servings, 
                                    {recipe_dict.get("time_min").get(i)} minutes*
                                    '''
                                        ),
                                        dbc.Button(
                                            "Go to recipe",
                                            href=f"""{recipe_dict.get("link").get(i)}""",
                                            target="_blank",
                                            color="primary",
                                        )
                                    ]
                                )
                            ]
                        ),
                    ],
                    color="info",
                    outline=True
                )
            ],
            width=4,
            className=input_class
        ) for i in range(len(recipe_dict.get("name")))
    ]
    return recipe_layout


def create_ingredients_layout_list(ing_df: pd.DataFrame) -> list:
    """Returns the list of ingredients for the recipe passed"""
    ing_df.dropna(inplace=True)
    no_ing = int((len(ing_df.index) - 3) / 3)
    layout_list = [dbc.ListGroupItem(ing_df["protein"].capitalize())]
    for i in range(1, no_ing + 1):
        layout = dbc.ListGroupItem(ing_df[f"ing_{i}"].capitalize())
        layout_list.append(layout)
    return layout_list


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)
