import pandas as pd
import numpy as np
from typing import Union


class RecipeSearch:

    def __init__(self, data, ingredients):
        self.df = data
        max_ing = 12
        self.ingredient_cols = []
        for i in range(1, max_ing):
            self.ingredient_cols.append(f"ing_{i}")
        recipe_search_df = self.filter_by_ingredients(ingredients)
        # self.recipe_names_array = recipe_search_df["name"].values
        self.recipe_search_dict = recipe_search_df.loc[:,
                                  ["name", "servings", "time_min", "time_max", "link"]].to_dict()
        self.ingredients_df = self.organize_ingredients(recipe_search_df)

    def filter_by_ingredients(self, ingredients: Union[str, list]) -> np.array:
        """Filters the recipe dataframe based on ingredient. Returns a df of the recipe names that contain
        the ingredients passed"""
        idx_list = list()
        for ingredient in ingredients:
            idx = self.df[self.df.isin([ingredient]).any(axis=1)].index
            idx_list.extend(list(idx))
        new_df = self.df.iloc[list(set(idx_list))]
        return new_df.reset_index(drop=True)

    def organize_ingredients(self, df):
        """Reorganizes the ingredients from recipe df into a filtered datafram"""
        df.drop(["name", "servings", "time_min", "time_max", "tags", "link"], axis=1, inplace=True)
        return df.dropna(how="all", axis=1)


# recipe_df = pd.read_csv(r"resources/recipes_database.csv", header=0)
# rs = RecipeSearch(recipe_df, ["chicken", "potatoes"])
# print(rs.recipe_search_dict)
