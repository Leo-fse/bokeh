from bokeh.plotting import figure

from ..base import Chart
from ..config import BarChartConfig
from ..schema import ChartData


class BarChart(Chart):
    """Bokehを使用して棒グラフを作成するクラス。"""

    def __init__(self, data: ChartData, config: BarChartConfig = BarChartConfig()):
        super().__init__(data, config)

    def _prepare_data_source(self) -> None:
        """Bokehプロット用のデータソースを準備します。"""
        self.source.data = {
            "labels": self.data.x,
            "amounts": self.data.y,
            "colors": self.data.colors,
        }

    def _add_elements(self, p: figure) -> None:
        """棒グラフのバーを追加します。"""
        p.vbar(x="labels", top="amounts", width=0.9, source=self.source.data, color="colors")
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.yaxis.axis_label = self.config.y_label if hasattr(self.config, "y_label") else None
        p.xaxis.axis_label = self.config.x_label if hasattr(self.config, "x_label") else None

    def render(self) -> None:
        """棒グラフを表示します。"""
        return super().render()
