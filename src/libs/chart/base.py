from abc import ABC, abstractmethod

from bokeh.io import show
from bokeh.layouts import row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show

# from bokeh.plotting import show
from src.libs.chart import (
    BarChart,
    BarChartConfig,
    ChartData,
    PieChart,
    PieChartConfig,
)

from .config import FigureConfig


class Chart(ABC):
    def __init__(self, data: ChartData, config: FigureConfig = FigureConfig()):
        self.data = data
        self.config = config
        self.source = ColumnDataSource()

    @abstractmethod
    def _prepare_data_source(self) -> None:
        pass

    @abstractmethod
    def _add_elements(self, p: figure) -> None:
        pass

    def _create_figure(self) -> figure:
        """Bokehのfigureオブジェクトを作成し、設定します。"""
        x_range = (
            self.source.data["labels"]
            if isinstance(self.config, BarChartConfig)
            else getattr(self.config, "x_range", None)
        )
        y_range = getattr(self.config, "y_range", None)
        return figure(
            title=self.config.title,
            plot_height=self.config.plot_height,
            plot_width=self.config.plot_width,
            toolbar_location=self.config.toolbar_location,
            x_range=x_range,
            y_range=y_range,
        )

    def _configure_axes(self, p: figure) -> None:
        """軸とグリッドの表示設定を行います。"""
        if hasattr(self.config, "show_axis"):
            p.axis.visible = self.config.show_axis
        if hasattr(self.config, "show_grid"):
            p.grid.visible = self.config.show_grid

    def render(self) -> figure:
        """グラフを表示します。"""
        self._prepare_data_source()
        p = self._create_figure()
        self._configure_axes(p)
        self._add_elements(p)
        return p

    def show(self):
        p = self.render()
        show(p)


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
