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