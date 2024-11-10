import pandas as pd


def fetch_setteings(fp: str):
    sheet_names = ["data", "layout", "graph", "calc"]
    setting_df_dict = pd.read_excel(fp, sheet_name=sheet_names, header=1)
    data_df = setting_df_dict["data"]
    layout_df = setting_df_dict["layout"]
    graph_df = setting_df_dict["graph"]
    calc_df = setting_df_dict["calc"]
    return data_df, layout_df, graph_df, calc_df


if __name__ == "__main__":
    setting_file_path = r"C:\Users\tomon\Documents\Python\settings.xlsx"
    data_df, layout_df, graph_df, calc_df = fetch_setteings(fp=setting_file_path)
    print(data_df)
    print(layout_df)
    print(graph_df)
    print(calc_df)
