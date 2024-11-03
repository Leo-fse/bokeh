from bokeh.io import output_notebook
from bokeh.layouts import row
from bokeh.plotting import show

from libs.chart import (
    BarChart,
    BarChartConfig,
    ChartData,
    PieChart,
    PieChartConfig,
)

def set_chart_data() -> ChartData:
    return ChartData(
        x=["Pepperoni", "Cheese", "Mixed Veggies", "Bacon"],
        y=[221, 212, 152, 72],
        colors=["red", "darkorange", "darkgreen", "hotpink"],
    )

def config_pie_chart():
    return PieChartConfig(
        title="Pizza Orders - Pie Chart",
        label_position_adjust=1.3,
    )

def config_bar_chart():
    return BarChartConfig(
        title="Pizza Orders - Bar Chart",
    )

def create_charts(data):
    pie_config = config_pie_chart()
    bar_config = config_bar_chart()

    pie_chart = PieChart(data, pie_config)
    bar_chart = BarChart(data, bar_config)

    return pie_chart.render(), bar_chart.render()

def main():
    data = set_chart_data()
    pie_figure, bar_figure = create_charts(data)
    show(row(pie_figure, bar_figure))

if __name__ == "__main__":
    main()