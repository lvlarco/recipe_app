# dashtools requirements
import pathlib

# import packages
import random
import dash
import dash_cool_components
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd

from data_ingest import RecipeSearch

pd.options.mode.chained_assignment = None

recipe_df = pd.read_csv(r"resources/recipes_database.csv", header=0)
rp = recipe_df[["name", "protein"]]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI])
app.title = 'Recipe Finder'
server = app.server

input_size = "md"
input_class = "py-2"
color_options = ["primary", "secondary", "success", "info", "warning", "danger"]

ingredients_list_suggestions = ["potatoes", "lemon"]
html.Datalist(id="list-suggestions", children=[html.Option(value=i) for i in ingredients_list_suggestions])

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
                            html.Br(),
                            "Click on the recipe title to go to the source for instructions"
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
                                       n_clicks=0
                                       ),
                            width="auto", className=input_class
                        ),
                    ]
                )
            ]
        ),
        dbc.Row(id="recipe-output")

    ]
)


@app.callback(
    Output(component_id="recipe-output", component_property="children"),
    Input(component_id="search-btn", component_property="n_clicks"),
    State(component_id="ingredients-input", component_property="value"),
    prevent_initial_call=True
)
def ingredient_search_callback(_, ing_dict: list) -> list:
    """Returns a dataframe that is filtered by the search of ingredients"""
    ing_list = list()
    for i in range(len(ing_dict)):
        ing = ing_dict[i].get("displayValue")
        ing_list.append(ing)
    rs = RecipeSearch(recipe_df, ing_list)
    recipe_dict = rs.recipe_search_dict
    ing_df = rs.ingredients_df
    recipe_card_list = create_recipe_card(recipe_dict, ing_df)
    return recipe_card_list


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
                    color=random.choice(color_options),
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
    app.run_server(debug=True)
