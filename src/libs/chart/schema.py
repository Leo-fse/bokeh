from typing import List

from pydantic import BaseModel, Field, model_validator


class ChartData(BaseModel):
    """グラフ作成に必要なデータを保持するデータ構造"""

    x: List[str] = Field(
        ...,  # 必須パラメータ
        description="各セクションのラベル",
        min_length=1,  # 少なくとも1つの要素が必要
    )
    y: List[int] = Field(
        ...,
        description="各セクションの数量",
        min_length=1,
    )
    colors: List[str] = Field(
        ...,
        description="各セクションの色",
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_lists(self) -> "ChartData":
        """全てのリストの長さが同じであることを確認"""
        x_len = len(self.x)
        if len(self.y) != x_len or len(self.colors) != x_len:
            raise ValueError("全てのリストは同じ長さである必要があります")

        if any(val < 0 for val in self.y):
            raise ValueError("数量は0以上である必要があります")

        return self

    class Config:
        frozen = True  # イミュータブルに設定
