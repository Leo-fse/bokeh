from typing import Optional, Tuple

from pydantic import BaseModel, Field


class FigureConfig(BaseModel):
    """グラフの共通設定を保持するデータ構造"""

    title: str = Field(default="Chart Title", description="グラフのタイトル")
    plot_width: int = Field(default=500, description="グラフの幅")
    plot_height: int = Field(default=500, description="グラフの高さ")
    toolbar_location: Optional[str] = Field(default="above", description="ツールバーの位置")
    show_grid: bool = Field(default=True, description="グリッドの表示/非表示")
    show_axis: bool = Field(default=True, description="軸の表示/非表示")
    legend_location: Optional[str] = Field(default="top_left", description="凡例の位置")

    class Config:
        frozen = True  # イミュータブルに設定


class PieChartConfig(FigureConfig):
    """円グラフのプロット設定を保持するデータ構造"""

    title: str = Field(default="Pie Chart", description="円グラフのタイトル")
    x_range: Tuple[float, float] = Field(default=(-1.5, 1.5), description="X軸の表示範囲")
    y_range: Tuple[float, float] = Field(default=(-1.5, 1.5), description="Y軸の表示範囲")
    show_grid: bool = Field(default=False, description="グリッドの表示/非表示")
    show_axis: bool = Field(default=False, description="軸の表示/非表示")
    label_position_adjust: float = Field(
        default=0.65,
        description="ラベルの位置調整係数",
        ge=0,  # 0以上の値のみ許可
    )


class BarChartConfig(FigureConfig):
    """棒グラフのプロット設定を保持するデータ構造"""

    title: str = Field(default="Bar Chart", description="棒グラフのタイトル")
    y_label: Optional[str] = Field(default=None, description="Y軸のラベル")
    x_label: Optional[str] = Field(default=None, description="X軸のラベル")
