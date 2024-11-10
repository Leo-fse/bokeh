from typing import List, Tuple

from pydantic import BaseModel, Field


class YAxis(BaseModel):
    """Y軸の設定を保持するデータ構造"""

    param: str = Field(description="項目")
    unit: str = Field(description="単位")
    range: Tuple[int, int] = Field(description="範囲 (最小値, 最大値)")
    color: str = Field(description="色")
    label: str = Field(description="ラベル")


class XAxis(BaseModel):
    """X軸の設定を保持するデータ構造"""

    param: str = Field(description="項目")
    unit: str = Field(description="単位")
    range: Tuple[int, int] = Field(description="範囲 (最小値, 最大値)")
    label: str = Field(description="ラベル")


class GraphCondition(BaseModel):
    """グラフの設定を保持するデータ構造"""

    id: str = Field(description="グラフのID")
    tabname: str = Field(description="タブの名前")
    x_axis: XAxis = Field(description="X軸")
    y_axes: List[YAxis] = Field(description="Y軸のリスト")
