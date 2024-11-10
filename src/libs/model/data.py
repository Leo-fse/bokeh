from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel, Field, ValidationError, model_validator


class DataCondition(BaseModel):
    """データの取得条件を保持するデータ構造"""

    id: str = Field(description="データのID")
    tabname: str = Field(description="タブの名前")
    unit: str = Field(description="号機")
    start_date: datetime = Field(description="開始日時")
    end_date: datetime = Field(description="終了日時")
    interval: str = Field(description="間隔")
    data_source: str = Field(description="データ取得先")
    graph_color: str = Field(
        description="グラフの色/GraphConditionで指定されている場合はそちらを優先"
    )

    @model_validator(mode="before")
    @classmethod
    def check_date_order(cls, values):
        start_date = values.get("start_date")
        end_date = values.get("end_date")
        if start_date and end_date and start_date >= end_date:
            raise ValidationError("開始日時は終了日時よりも前でなければなりません")
        return values
