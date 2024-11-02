import random
from datetime import datetime
from typing import List

from bokeh.io import show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, LinearAxis, Panel, Range1d, Tabs
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from schema import (
    AxisSettings,
    Data,
    FigureSettings,
    axis_settings1,
    axis_settings2,
    data1,
    data2,
    figure_settings1,
    figure_settings2,
)


# create a new plot with a title and axis labels
def create_figure(data: Data, figure_settings: FigureSettings, axis_settings: AxisSettings):
    p = figure(
        x_range=figure_settings.x_range,
        y_range=figure_settings.y_range,
        width=figure_settings.width,  # plot_widthの代わりにwidthを使用
        height=figure_settings.height,  # plot_heightの代わりにheightを使用
        title=figure_settings.title,
    )

    # デフォルトのY軸を削除
    p.yaxis.visible = False
    # 新しいY軸を追加
    new_yaxis = create_axis(axis_settings)
    p.add_layout(new_yaxis, "left")

    # データをプロット
    p.line(data.x, data.y, legend_label="Temp.", line_width=2)

    return p


# 軸の設定をする関数
def create_axis(axis_settings: AxisSettings):
    return LinearAxis(
        axis_label=axis_settings.title,
        axis_label_text_font_size=axis_settings.label_font_size,
        major_label_text_font_size=axis_settings.tick_label_font_size,
    )


if __name__ == "__main__":
    p1 = create_figure(data1, figure_settings1, axis_settings1)
    p2 = create_figure(data2, figure_settings2, axis_settings2)

    layout = row(column(p1, p2), column(p1, p2))
    show(layout)
