from math import pi

import numpy as np
from bokeh.plotting import figure

from ..base import Chart
from ..config import PieChartConfig
from ..schema import ChartData


class PieChart(Chart):
    """Bokehを使用して円グラフを作成するクラス。"""

    def __init__(self, data: ChartData, config: PieChartConfig = PieChartConfig()):
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
