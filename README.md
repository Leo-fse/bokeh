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

```
Public Sub UpdateCellColor(Target As Range)
    Dim wsName As String
    Dim targetRange As Range
    Dim colorCode As String
    Dim cell As Range
    Dim r As Long, g As Long, b As Long  ' RGB値を格納する変数
    Dim brightness As Double             ' 明るさ（輝度）の計算結果を格納

    ' 色名とRGBのマッピング
    Dim colorMap As Object
    Set colorMap = CreateObject("Scripting.Dictionary")
    Call InitializeColorMap(colorMap)

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
            colorCode = Trim(cell.Value)
            
            ' 色名からRGBに変換
            If colorMap.exists(LCase(colorCode)) Then
                r = colorMap(LCase(colorCode))(0)
                g = colorMap(LCase(colorCode))(1)
                b = colorMap(LCase(colorCode))(2)
            ElseIf Left(colorCode, 1) = "#" Then
                colorCode = Mid(colorCode, 2) ' 先頭の # を取り除く
                If Len(colorCode) = 6 Then
                    On Error Resume Next
                    r = CLng("&H" & Mid(colorCode, 1, 2)) ' 赤
                    g = CLng("&H" & Mid(colorCode, 3, 2)) ' 緑
                    b = CLng("&H" & Mid(colorCode, 5, 2)) ' 青
                    On Error GoTo 0
                Else
                    GoTo ResetCell
                End If
            Else
                GoTo ResetCell
            End If

            ' RGB値から背景色を設定
            cell.Interior.Color = RGB(r, g, b)

            ' 明るさ（輝度）を計算
            brightness = (0.299 * r + 0.587 * g + 0.114 * b)

            ' 輝度に応じてテキスト色を変更
            If brightness < 128 Then
                cell.Font.Color = RGB(255, 255, 255) ' 白い文字
            Else
                cell.Font.Color = RGB(0, 0, 0) ' 黒い文字
            End If
        Else
ResetCell:
            ' セルが空、または無効な値の場合は背景とフォントをリセット
            cell.Interior.ColorIndex = xlNone
            cell.Font.Color = RGB(0, 0, 0)
        End If
    Next cell
    Application.EnableEvents = True
End Sub

' 色名と対応するRGB値を設定
Private Sub InitializeColorMap(colorMap As Object)
    colorMap.Add "red", Array(255, 0, 0)
    colorMap.Add "green", Array(0, 128, 0)
    colorMap.Add "blue", Array(0, 0, 255)
    colorMap.Add "yellow", Array(255, 255, 0)
    colorMap.Add "pink", Array(255, 192, 203)
    colorMap.Add "orange", Array(255, 165, 0)
    colorMap.Add "purple", Array(128, 0, 128)
    colorMap.Add "cyan", Array(0, 255, 255)
    colorMap.Add "magenta", Array(255, 0, 255)
    colorMap.Add "lime", Array(0, 255, 0)
    colorMap.Add "black", Array(0, 0, 0)
    colorMap.Add "white", Array(255, 255, 255)
    colorMap.Add "gray", Array(128, 128, 128)
    colorMap.Add "grey", Array(128, 128, 128) ' 米国・英国英語両方対応
    colorMap.Add "brown", Array(165, 42, 42)
    colorMap.Add "gold", Array(255, 215, 0)
    colorMap.Add "silver", Array(192, 192, 192)
    colorMap.Add "navy", Array(0, 0, 128)
    colorMap.Add "teal", Array(0, 128, 128)
    colorMap.Add "olive", Array(128, 128, 0)
    ' 必要に応じて他の色も追加可能
End Sub

```
