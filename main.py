import numpy as np
import pandas as pd

from bokeh.io import show
from bokeh.layouts import column, gridplot
from bokeh.models import (
    ColumnDataSource,
    Div,
    Grid,
    Line,
    LinearAxis,
    Plot,
    Range1d,
    RangeTool,
    Scatter,
)
from bokeh.plotting import curdoc, figure


def create_plot(x, y_list, legend_labels, title, x_range=None, colors=None):
    p = figure(
        height=300,
        width=800,
        tools="xpan",
        toolbar_location=None,
        x_axis_type="datetime",
        x_axis_location="below",  # x軸位置をbottomに変更
        background_fill_color="#efefef",
        x_range=x_range
        if x_range
        else (dates[0], dates[-1]),  # datesの最初から最後までの範囲を設定
        y_range=(
            min([min(y) for y in y_list]),
            max([max(y) for y in y_list]),
        ),  # y_rangeを最小最大値に設定
        title=title,
    )

    for i, (y, label, color) in enumerate(zip(y_list, legend_labels, colors)):
        source = ColumnDataSource(data={"x": x, "y": y})
        p.line("x", "y", source=source, legend_label=label, color=color)
        p.yaxis.axis_label = label
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"
        if i == 0:
            pass
        else:
            p.extra_y_ranges = {"legend": Range1d(start=min(y), end=max(y))}
            p.add_layout(LinearAxis(y_range_name="legend", axis_label=label), "left")

    select = figure(
        title="Drag the middle and edges of the selection box to change the range above",
        height=100,
        width=800,
        y_range=p.y_range,  # メインプロットと同じy_rangeを使用
        x_axis_type="datetime",
        y_axis_type=None,
        tools="",
        toolbar_location=None,
        background_fill_color="#efefef",
    )

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    select.line("x", "y", source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)

    return p, select


dates = np.array(pd.date_range(start="1/1/2018", periods=8), dtype=np.datetime64)
appl_prices = np.cumsum(np.random.randn(8)) + 100
appl_prices2 = np.cumsum(np.random.randn(8)) + 50

AAPL = pd.DataFrame({"adj_close": appl_prices}, index=dates)
AAPL2 = pd.DataFrame({"adj_close": appl_prices2}, index=dates)


graph1 = {
    "title": "AAPL Prices",
    "dates": dates,
    "plots": [
        {"name": "AAPL", "data": AAPL, "color": "blue"},
        {"name": "AAPL2", "data": AAPL2, "color": "red"},
    ],
}
graph2 = {
    "title": "AAPL2 Prices",
    "dates": dates,
    "plots": [{"name": "AAPL2", "data": AAPL2, "color": "green"}],
}


p1, select = create_plot(
    dates, [appl_prices, appl_prices2], ["AAPL", "AAPL2"], "AAPL Prices", colors=["blue", "red"]
)

p2, _ = create_plot(
    dates, [appl_prices2], ["AAPL2"], "AAPL2 Prices", x_range=p1.x_range, colors=["green"]
)


div = Div(
    text="""
<h1>Anscombe's Quartet</h1>
<p>Anscombe's Quartet is a collection of four small datasets that have nearly
identical simple descriptive statistics (mean, variance, correlation, and
linear regression lines), yet appear very different when graphed.
</p>
"""
)

curdoc().add_root(column(div, select, p1, p2))
curdoc().title = "AAPL Stock Prices"
