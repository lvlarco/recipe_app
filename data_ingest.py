import pandas as pd
from typing import Union

pd.options.mode.chained_assignment = None


class RecipeSearch:

    def __init__(self, data: pd.DataFrame, ingredients: list):
        self.df = data
        ingredients = list(map(lambda x: str(x).lower(), ingredients))
        max_ing = 12
        self.ingredient_cols = []
        for i in range(1, max_ing):
            self.ingredient_cols.append(f"ing_{i}")
        self.recipe_search_df = self.filter_by_ingredients(ingredients)
        if not self.recipe_search_df.empty:
            self.map_fish_type()
            self.recipe_search_dict = self.recipe_search_df.loc[:,
                                      ["name", "servings", "time_min", "time_max", "link"]].to_dict()
            self.ingredients_df = self.organize_ingredients()

    def filter_by_ingredients(self, ingredients: Union[str, list]) -> pd.DataFrame:
        """Filters the recipe dataframe based on ingredient. Returns a df of the recipe names that contain
        the ingredients passed
        :param ingredients: elements from the search
        """
        idx_list = list()
        for ingredient in ingredients:
            idx = self.df[self.df.isin([ingredient]).any(axis=1)].index
            idx_list.extend(list(idx))
        new_df = self.df.iloc[list(set(idx_list))]
        return new_df.dropna(how="all", axis=1).reset_index(drop=True)

    def extract_tags(self, recipe_idx: int) -> list:
        """Extracts the tag for a specific recipe from the df and returns a list with the elements
        :param recipe_idx: must be the index of the recipe to extract tags from
        """
        try:
            tags = self.recipe_search_df.loc[recipe_idx, "tags"].split(",")
        except AttributeError:
            tags = list()
        return [t.strip() for t in tags]

    def get_fish_type(self, recipe_idx: int):
        """Maps the fish to its type by looking at the tags_list"""
        fishes = ["cod", "tilapia", "salmon", "bass", "trout"]
        try:
            i = set(fishes) & set(self.extract_tags(recipe_idx))
            return list(i)[0]
        except IndexError:
            pass

    def map_fish_type(self):
        fish_df = self.recipe_search_df.loc[self.recipe_search_df["protein"] == "fish"]

        def row_index(row):
            return row.name

        if not fish_df.empty:
            fish_df.loc[:, "row_index"] = fish_df.apply(row_index, axis=1)
            fish_df.loc[:, "protein"] = fish_df["row_index"].apply(self.get_fish_type)
            self.recipe_search_df.loc[fish_df.loc[:, "protein"].index, "protein"] = fish_df.loc[:, "protein"]
            # self.recipe_search_df.drop("row_index", axis=1, inplace=True)

    @staticmethod
    def check_in_tag(word: str, tag_list: list) -> bool:
        """Examines key word passed to see if it is within tag of a specific recipe"""
        return word in tag_list

    def organize_ingredients(self) -> pd.DataFrame:
        """Reorganizes the ingredients from recipe df into a filtered datafram"""
        df = self.recipe_search_df.drop(["name", "servings", "time_min", "time_max", "tags", "link"], axis=1)
        return df.dropna(how="all", axis=1)

# recipe_df = pd.read_csv(r"resources/recipes_database.csv", header=0)
# rs = RecipeSearch(recipe_df, ["orzo"])
# print(rs.recipe_search_df)
