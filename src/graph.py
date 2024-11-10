import random
from datetime import datetime, timedelta
from typing import List

from bokeh.layouts import column, gridplot
from bokeh.models import ColumnDataSource, Panel, Tabs
from bokeh.plotting import figure, show

from src.libs.model.page import DataCondition, GraphCondition, GraphLayout, Page, Tab, XAxis, YAxis


# ダミーデータ生成用の関数
def generate_dummy_data(start_date, end_date, interval):
    dates = []
    values = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        values.append(random.uniform(0, 100))  # ダミーのランダム値
        current_date += timedelta(days=1)  # 仮に1日ごとのデータとする
    return dates, values


# 各タブのグラフを作成する関数
def create_bokeh_graph(tab: Tab):
    # 各タブのグラフを保持するリスト
    tab_plots = []

    for graph_condition in tab.graph_conditions:
        # 新しい Figure を作成
        p = figure(
            title=tab.tabtitle,
            x_axis_label=graph_condition.x_axis.label,
            y_axis_label=" / ".join([y_axis.label for y_axis in graph_condition.y_axes]),
            x_axis_type="datetime",
        )

        # データ条件に従って折れ線グラフを追加
        for data_condition in tab.data_conditions:
            # ダミーデータを生成（本番環境ではデータベースなどから取得する）
            dates, values = generate_dummy_data(
                data_condition.start_date, data_condition.end_date, data_condition.interval
            )
            source = ColumnDataSource(data=dict(x=dates, y=values))

            # 折れ線グラフを描画
            p.line(
                x="x",
                y="y",
                source=source,
                legend_label=f"{data_condition.id} ({data_condition.unit})",
                color=data_condition.graph_color,
                line_width=2,
            )

        # グラフに対してレイアウト設定 (GraphLayout) を適用
        p.legend.title = "Data Conditions"
        p.legend.click_policy = "hide"
        p.grid.grid_line_alpha = 0.3

        # 各グラフをリストに追加
        tab_plots.append(p)

    # グリッドレイアウトに並べる
    grid = gridplot(tab_plots, ncols=tab.layout.columns, sizing_mode="stretch_both")

    return grid


# 複数ページの作成と表示
def display_multiple_pages(pages: List[Page]):
    all_tabs = []

    for page in pages:
        page_tabs = []
        for tab in page.tabs:
            # 各タブに対応するグラフを生成
            grid = create_bokeh_graph(tab)

            # Panelとしてタブに追加
            panel = Panel(child=column(grid), title=tab.tabname)
            page_tabs.append(panel)

        # 各ページごとにTabsを作成
        page_layout = Tabs(tabs=page_tabs)
        all_tabs.append(Panel(child=page_layout, title=page.pagename))

    # メインのページレイアウトとして複数のページを表示
    main_tabs = Tabs(tabs=all_tabs)
    show(main_tabs)


# テスト用のダミーPageデータ
page_data = [
    Page(
        pagename="Page 1",
        title="Sample Page 1",
        tabs=[
            Tab(
                tabname="Tab 1",
                tabtitle="Sample Graph for Tab 1",
                layout=GraphLayout(tabname="Tab 1", columns=2, rows=1),
                data_conditions=[
                    DataCondition(
                        id="data1",
                        tabname="Tab 1",
                        unit="Unit A",
                        start_date=datetime(2023, 1, 1),
                        end_date=datetime(2023, 1, 10),
                        interval="daily",
                        data_source="Source A",
                        graph_color="blue",
                    ),
                    DataCondition(
                        id="data2",
                        tabname="Tab 1",
                        unit="Unit B",
                        start_date=datetime(2023, 1, 1),
                        end_date=datetime(2023, 1, 10),
                        interval="daily",
                        data_source="Source B",
                        graph_color="green",
                    ),
                ],
                graph_conditions=[
                    GraphCondition(
                        id="graph1",
                        tabname="Tab 1",
                        x_axis=XAxis(param="date", unit="datetime", range=(0, 10), label="Date"),
                        y_axes=[
                            YAxis(
                                param="value",
                                unit="units",
                                range=(0, 100),
                                color="blue",
                                label="Value A",
                            ),
                            YAxis(
                                param="value",
                                unit="units",
                                range=(0, 100),
                                color="green",
                                label="Value B",
                            ),
                        ],
                    )
                ],
            ),
            Tab(
                tabname="Tab 2",
                tabtitle="Sample Graph for Tab 2",
                layout=GraphLayout(tabname="Tab 2", columns=1, rows=1),
                data_conditions=[
                    DataCondition(
                        id="data3",
                        tabname="Tab 2",
                        unit="Unit C",
                        start_date=datetime(2023, 2, 1),
                        end_date=datetime(2023, 2, 10),
                        interval="daily",
                        data_source="Source C",
                        graph_color="purple",
                    ),
                ],
                graph_conditions=[
                    GraphCondition(
                        id="graph2",
                        tabname="Tab 2",
                        x_axis=XAxis(param="date", unit="datetime", range=(0, 10), label="Date"),
                        y_axes=[
                            YAxis(
                                param="value",
                                unit="units",
                                range=(0, 100),
                                color="purple",
                                label="Value C",
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
]

# グラフを作成・表示
display_multiple_pages(page_data)
