# Bokeh Chart Library

## 概要
Bokehを使用した、シンプルで使いやすい円グラフ・棒グラフ作成ライブラリです。データ構造の検証やグラフのカスタマイズが容易に行えます。

## 機能
- 円グラフ（PieChart）の作成
- 棒グラフ（BarChart）の作成
- Pydanticを使用したデータ構造の検証
- 豊富なグラフカスタマイズオプション

## インストール方法

```bash
git clone [リポジトリURL]
cd [リポジトリ名]
pip install -r requirements.txt
```

## 使用例
notebooks/bokeh.ipynbを参照ください
```python
from src.libs.chart import PieChart, BarChart, ChartData, PieChartConfig, BarChartConfig
```

### データの準備
```python
data = ChartData(
x=["Pepperoni", "Cheese", "Mixed Veggies", "Bacon"],
y=[221, 212, 152, 72],
colors=["red", "darkorange", "darkgreen", "hotpink"]
```

### 円グラフの作成
```python
pie_config = PieChartConfig(
    title="Pizza Orders - Pie Chart", 
    label_position_adjust=1.3
)
pie_chart = PieChart(data, pie_config)
pie_figure = pie_chart.render()
```

### 棒グラフの作成
```python
bar_config = BarChartConfig(title="Pizza Orders - Bar Chart")
bar_chart = BarChart(data, bar_config)
bar_figure = bar_chart.render()
```

## 設定オプション

### 共通設定 (FigureConfig)
- `title`: グラフのタイトル
- `plot_width`: グラフの幅
- `plot_height`: グラフの高さ
- `toolbar_location`: ツールバーの位置
- `show_grid`: グリッドの表示/非表示
- `show_axis`: 軸の表示/非表示
- `legend_location`: 凡例の位置

### 円グラフ設定 (PieChartConfig)
- `label_position_adjust`: ラベルの位置調整係数
- その他、FigureConfigの設定を継承

### 棒グラフ設定 (BarChartConfig)
- `y_label`: Y軸のラベル
- `x_label`: X軸のラベル
- その他、FigureConfigの設定を継承

## 必要要件
- Python 3.11以上
- 主な依存パッケージ:
  - bokeh==2.4.3
  - pydantic==2.9.2
  - numpy==1.22.4

## ライセンス

## 開発環境
- Visual Studio Code
- Jupyter Notebook
- Ruff (コードフォーマッター)

Public Sub UpdateCellColor(Target As Range)
    Dim wsName As String
    Dim targetRange As Range
    Dim colorCode As String
    Dim cell As Range
    Dim r As Long, g As Long, b As Long  ' RGB値を格納する変数

    ' シート名を取得
    wsName = Target.Worksheet.Name

    ' 適用範囲が設定されているか確認
    If SheetRanges Is Nothing Then Exit Sub
    If Not SheetRanges.Exists(wsName) Then Exit Sub

    ' 適用範囲を取得
    Set targetRange = Intersect(Target, Target.Worksheet.Range(SheetRanges(wsName)))
    If targetRange Is Nothing Then Exit Sub

    ' セルごとに背景色を設定
    Application.EnableEvents = False
    For Each cell In targetRange
        If Not IsEmpty(cell.Value) Then
            colorCode = cell.Value
            If Left(colorCode, 1) = "#" Then
                colorCode = Mid(colorCode, 2) ' 先頭の # を取り除く
            End If

            ' カラーコードをRGBに分解
            If Len(colorCode) = 6 Then
                On Error Resume Next
                r = CLng("&H" & Mid(colorCode, 1, 2)) ' 赤 (先頭2桁)
                g = CLng("&H" & Mid(colorCode, 3, 2)) ' 緑 (次の2桁)
                b = CLng("&H" & Mid(colorCode, 5, 2)) ' 青 (最後の2桁)
                On Error GoTo 0

                ' RGB値から色を設定（順序を考慮）
                cell.Interior.Color = RGB(r, g, b)
            Else
                ' 不正なカラーコードの場合は色をリセット
                cell.Interior.ColorIndex = xlNone
            End If
        Else
            ' セルが空の場合は背景色をリセット
            cell.Interior.ColorIndex = xlNone
        End If
    Next cell
    Application.EnableEvents = True
End Sub