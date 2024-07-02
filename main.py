import numpy as np
import pandas as pd

from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure, show

data_num = 3000
df = pd.DataFrame(
    index=pd.date_range(start="1/1/2018", freq="s", periods=data_num),
    data={
        "AAPL": np.random.randn(data_num),
        "AAPL2": np.random.randn(data_num),
        "MSFT": np.random.randn(data_num),
        "GOOGL": np.random.randn(data_num),
        "GOOG": np.random.randn(data_num),
    },
)

dates = np.array(df.index, dtype=np.datetime64)
source = ColumnDataSource(data={"date": dates, "AAPL": df["AAPL"]})

p = figure(
    height=300,
    width=800,
    tools="xpan",
    toolbar_location=None,
    x_axis_type="datetime",
    x_axis_location="above",
    background_fill_color="#efefef",
    x_range=(dates[1500], dates[2500]),
)

p.line("date", "AAPL", source=source)
p.yaxis.axis_label = "Price"

select = figure(
    title="Drag the middle and edges of the selection box to change the range above",
    height=130,
    width=800,
    y_range=p.y_range,
    x_axis_type="datetime",
    y_axis_type=None,
    tools="",
    toolbar_location=None,
    background_fill_color="#efefef",
)

range_tool = RangeTool(x_range=p.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line("date", "AAPL", source=source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)

show(column(p, select))
