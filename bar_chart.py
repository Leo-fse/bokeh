from dataclasses import dataclass
from math import pi
from typing import List, Optional, Tuple

import numpy as np

from bokeh.layouts import row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show


@dataclass
class ChartData:
    """グラフ作成に必要なデータを保持するデータ構造"""

    x: List[str]  # 各セクションのラベル
    y: List[int]  # 各セクションの数量
    colors: List[str]  # 各セクションの色


@dataclass
class ChartConfig:
    """グラフの共通設定を保持するデータ構造"""

    title: str = "Chart Title"
    plot_width: int = 500  # サイズを調整
    plot_height: int = 500  # サイズを調整
    toolbar_location: Optional[str] = None
    show_grid: bool = False
    legend_location: Optional[str] = "top_left"


@dataclass
class PIChartConfig(ChartConfig):
    """円グラフのプロット設定を保持するデータ構造"""

    x_range: Tuple[float, float] = (-1.5, 1.5)
    y_range: Tuple[float, float] = (-1.5, 1.5)
    show_axis: bool = False
    label_position_adjust: float = 0.65  # ラベルの位置を調整するための係数


@dataclass
class BarChartConfig(ChartConfig):
    """棒グラフのプロット設定を保持するデータ構造"""

    title: str = "Pizza Orders - Bar Chart"
    show_grid: bool = True


class Chart:
    """Bokehを使用してグラフを作成する基底クラス。"""

    def __init__(self, data: ChartData, config: ChartConfig = ChartConfig()):
        self.data = data
        self.config = config
        self.source = ColumnDataSource()

    def _prepare_data_source(self) -> None:
        """Bokehプロット用のデータソースを準備します。"""
        raise NotImplementedError

    def _create_figure(self) -> figure:
        """Bokehのfigureオブジェクトを作成し、設定します。"""
        x_range = self.source.data["labels"] if isinstance(self, BarChart) else self.config.x_range
        y_range = self.config.y_range if hasattr(self.config, "y_range") else None
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

    def _add_elements(self, p: figure) -> None:
        """各チャートに固有の要素を追加するためのメソッド。"""
        raise NotImplementedError


class PIChart(Chart):
    """Bokehを使用して円グラフを作成するクラス。"""

    def __init__(self, data: ChartData, config: PIChartConfig = PIChartConfig()):
        super().__init__(data, config)

    def _calculate_angles(self) -> None:
        """各セクションの開始角度、終了角度、および中央角度を計算します。"""
        total = sum(self.data.y)
        ratios = [amount / total for amount in self.data.y]
        angles = [ratio * 2 * pi for ratio in ratios]

        self.start_angles = [sum(angles[:i]) + pi / 2 for i in range(len(angles))]
        self.end_angles = [start + angle for start, angle in zip(self.start_angles, angles)]
        self.mid_angles = [(s + e) / 2 for s, e in zip(self.start_angles, self.end_angles)]

    def _calculate_label_positions(self) -> None:
        """ラベルのx, y座標を計算します。"""
        adjust = self.config.label_position_adjust
        print(adjust)
        self.label_x = [adjust * np.cos(angle) for angle in self.mid_angles]
        self.label_y = [adjust * np.sin(angle) for angle in self.mid_angles]

    def _prepare_data_source(self) -> None:
        """Bokehプロット用のデータソースを準備します。"""
        total = sum(self.data.y)
        percentages = [(amount / total) * 100 for amount in self.data.y]
        display_text = [f"{amount} ({(amount / total) * 100:.1f}%)" for amount in self.data.y]
        self.source.data = {
            "labels": self.data.x,
            "start_angle": self.start_angles,
            "end_angle": self.end_angles,
            "colors": self.data.colors,
            "label_x": self.label_x,
            "label_y": self.label_y,
            "amounts": self.data.y,
            "percentages": percentages,
            "display_text": display_text,
        }

    def _add_elements(self, p: figure) -> None:
        """楔部分とラベルを追加します。"""
        p.wedge(
            x=0,
            y=0,
            radius=1,  # 半径を調整
            start_angle="start_angle",
            end_angle="end_angle",
            color="colors",
            legend_field="labels",
            source=self.source,
        )

        p.text(
            x="label_x",
            y="label_y",
            text="display_text",
            text_align="center",
            text_baseline="middle",
            text_font_size="10pt",
            source=self.source,
        )

        total_amount = sum(self.data.y)
        p.text(
            x=self.config.x_range[0] * 0.9,
            y=self.config.y_range[1] * 0.9,
            text=[f"Total: {total_amount}"],
            text_align="left",
            text_baseline="top",
            text_font_size="12pt",
            color="black",
        )

    def render(self) -> None:
        """円グラフを表示します。"""
        self._calculate_angles()
        self._calculate_label_positions()
        return super().render()


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
        p.yaxis.axis_label = "Amount"
        p.xaxis.axis_label = "Pizza Toppings"

    def render(self) -> None:
        """棒グラフを表示します。"""
        return super().render()


if __name__ == "__main__":
    # データと設定
    data = ChartData(
        x=["Pepperoni", "Cheese", "Mixed Veggies", "Bacon"],
        y=[221, 212, 152, 72],
        colors=["red", "darkorange", "darkgreen", "hotpink"],
    )

    # 円グラフ設定
    pie_config = PIChartConfig(
        title="Pizza Orders - Pie Chart",
        label_position_adjust=1.3,
    )

    # 棒グラフ設定
    bar_config = BarChartConfig(
        title="Pizza Orders - Bar Chart",
    )

    # 円グラフを表示
    pie_chart = PIChart(data, pie_config)
    pie_figure = pie_chart.render()

    # 棒グラフを表示
    bar_chart = BarChart(data, bar_config)
    bar_figure = bar_chart.render()

    # 並べて表示
    show(row(pie_figure, bar_figure))
