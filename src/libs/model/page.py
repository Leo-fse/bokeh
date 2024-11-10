from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from .data import DataCondition
from .graph import GraphCondition


class GraphLayout(BaseModel):
    """タブレイアウトの設定を保持するデータ構造"""

    tabname: str = Field(description="タブの名前")
    columns: int = Field(description="列数")
    rows: int = Field(description="行数")


class Tab(BaseModel):
    """タブのデータ構造を保持するデータ構造"""

    tabname: str = Field(description="タブの名前")
    tabtitle: str = Field(description="タブページに表示するタイトル")
    layout: GraphLayout
    data_conditions: List[DataCondition]
    graph_conditions: List[GraphCondition]


class Page(BaseModel):
    """ページのデータ構造を保持するデータ構造"""

    output_file_name: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S"),
        description="出力ファイル名",
    )
    page_title: str = Field(description="ページのタイトル")
    tabs: List[Tab]
