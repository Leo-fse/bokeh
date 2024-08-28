import io
import os
import tempfile
import traceback
import webbrowser
from datetime import datetime
from pprint import pformat
from typing import Any, Dict, List, Optional, Tuple

import ipywidgets as widgets
import numpy as np
import pandas as pd
from IPython.display import HTML, display

from bokeh.embed import components, file_html
from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    DataRange1d,
    DatetimeTickFormatter,
    HoverTool,
    Legend,
    LinearAxis,
)
from bokeh.plotting import figure, output_file, save
from bokeh.resources import CDN


# 定数の整理
class Constants:
    MACHINE_OPTIONS: List[str] = ["machine1", "machine2", "machine3"]
    INTERVAL_OPTIONS: List[str] = ["1s", "1m", "1d"]
    WIDGET_STYLE: Dict[str, Any] = {
        "layout": widgets.Layout(width="300px", height="32px"),
        "style": {"description_width": "100px"},
    }
    REQUIRED_SHEETS: List[str] = ["tag", "period", "param"]
    BUTTON_LAYOUT = widgets.Layout(width="180px", height="32px")


# ダミーデータ生成用のAPI関数
def dummy_data_fetch_api(
    tags: List[str], start_time: datetime, end_time: datetime, interval: str
) -> pd.DataFrame:
    """ダミーデータを生成するAPI関数"""
    time_range = pd.date_range(start=start_time, end=end_time, freq=interval)
    data = {"time": time_range}
    for tag in tags:
        data[tag] = np.random.randn(len(time_range))
    return pd.DataFrame(data)


class SettingsError(Exception):
    """設定ファイルに関するエラーを表すカスタム例外"""

    pass


class DataWidget:
    """データ取得用ウィジェットを管理するクラス"""

    def __init__(self):
        self.widgets: Dict[str, widgets.Widget] = self._create_widgets()
        self.output = widgets.Output(layout={"border": "1px solid black"})
        self.log_output = widgets.Output()
        self.log_accordion = self._create_log_accordion()
        self.temp_dir = tempfile.mkdtemp()
        self.graph_file: Optional[str] = None
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.layout = self._create_layout()
        self._create_event_handlers()
        self._set_initial_state()
        self.fetched_data = None

    def _create_widgets(self) -> Dict[str, widgets.Widget]:
        """すべてのウィジェットを作成し、辞書として返す"""
        return {
            "machine": self._create_single_widget(
                widgets.Dropdown, options=Constants.MACHINE_OPTIONS, description="Machine:"
            ),
            "start_time": self._create_single_widget(
                widgets.NaiveDatetimePicker, description="Start Time:"
            ),
            "end_time": self._create_single_widget(
                widgets.NaiveDatetimePicker, description="End Time:"
            ),
            "interval": self._create_single_widget(
                widgets.Dropdown, options=Constants.INTERVAL_OPTIONS, description="Interval:"
            ),
            "uploader": self._create_single_widget(
                widgets.FileUpload, description="Upload File:", layout=Constants.BUTTON_LAYOUT
            ),
            "data_fetch": widgets.Button(description="データ取得", layout=Constants.BUTTON_LAYOUT),
            "data_fetch_status": widgets.HTML(value=""),
            "file_error": widgets.HTML(value="", layout=widgets.Layout(width="auto")),
            "status": widgets.HTML(
                value="",
                layout=widgets.Layout(width="auto", height="32px", margin="10px 0 0 0"),
            ),
            "time_error": widgets.HTML(
                value="",
                layout=widgets.Layout(width="auto", height="32px", margin="0 0 0 10px"),
            ),
            "graph_create": widgets.Button(
                description="グラフ作成", layout=Constants.BUTTON_LAYOUT
            ),
            "graph_status": widgets.HTML(value=""),
        }

    def _create_single_widget(self, widget_type: type, **kwargs) -> widgets.Widget:
        """単一のウィジェットを作成する"""
        widget_kwargs = Constants.WIDGET_STYLE.copy()
        widget_kwargs.update(kwargs)
        widget = widget_type(**widget_kwargs)
        widget.add_class("custom-widget")
        return widget

    def _create_log_accordion(self) -> widgets.Accordion:
        """ログアコーディオンを作成する"""
        log_accordion = widgets.Accordion(children=[self.log_output])
        log_accordion.set_title(0, "ログ")
        log_accordion.selected_index = None  # 初期状態では閉じておく
        return log_accordion

    def _create_layout(self) -> widgets.VBox:
        """ウィジェットのレイアウトを作成する"""
        layout = widgets.VBox(
            [
                self._create_file_upload_section(),
                self._create_data_fetch_section(),
                self._create_graph_section(),
                self._create_data_settings_section(),
                self.log_accordion,
                self.output,
            ]
        )
        print("レイアウトが作成されました")  # デバッグ用
        return layout

    def _create_file_upload_section(self) -> widgets.VBox:
        """ファイルアップロードセクションを作成する"""
        return widgets.HBox(
            [
                self.widgets["uploader"],
                self.widgets["file_error"],
            ],
            layout=widgets.Layout(width="100%", align_items="flex-start"),
        )

    def _create_data_fetch_section(self) -> widgets.HBox:
        """データ取得セクションを作成する"""
        section = widgets.HBox(
            [
                self.widgets["data_fetch"],
                self.widgets["data_fetch_status"],
            ],
            layout=widgets.Layout(align_items="center", margin="10px 0"),
        )
        print("データ取得セクションが作成されました")  # デバッグ用
        return section

    def _create_graph_section(self) -> widgets.HBox:
        """グラフ作成セクションを作成する"""
        section = widgets.HBox(
            [
                self.widgets["graph_create"],
                self.widgets["graph_status"],
            ],
            layout=widgets.Layout(align_items="center", margin="10px 0"),
        )
        print("グラフ作成セクションが作成されました")  # デバッグ用
        return section

    def _create_data_settings_section(self) -> widgets.Accordion:
        """データ設定セクションを作成する"""
        return widgets.Accordion(
            children=[
                widgets.VBox(
                    [
                        self.widgets["machine"],
                        widgets.HBox(
                            [self.widgets["start_time"], self.widgets["time_error"]],
                            layout=widgets.Layout(width="100%"),
                        ),
                        self.widgets["end_time"],
                        self.widgets["interval"],
                        widgets.HBox(
                            [
                                widgets.Box(layout=widgets.Layout(width="140px")),
                                self.widgets["data_fetch"],
                            ],
                            layout=widgets.Layout(
                                margin="20px 0 0 0", justify_content="flex-start"
                            ),
                        ),
                    ],
                    layout=widgets.Layout(width="auto", padding="10px"),
                )
            ],
            selected_index=None,
            layout=widgets.Layout(width="auto"),
            titles=["データ取得設定"],
        )

    def _create_event_handlers(self) -> None:
        """イベントハンドラを作成し、ウィジェットに設定する"""
        self.widgets["data_fetch"].on_click(self._on_data_fetch_click)
        for widget_name in ["machine", "start_time", "end_time", "interval", "uploader"]:
            self.widgets[widget_name].observe(self._on_value_change, names="value")
        self.widgets["uploader"].observe(self._update_widgets_with_file_data, names="value")
        self.widgets["graph_create"].on_click(self._on_graph_create_click)

    def validate_inputs(self) -> bool:
        """入力値を検証し、エラーメッセージを更新する"""
        is_valid = True
        error_messages = []

        if not self.widgets["uploader"].value:
            error_messages.append("設定ファイルをアップロードしてください")
            is_valid = False

        if not self.widgets["machine"].value:
            error_messages.append("マシンを選択してください")
            is_valid = False

        if not self.widgets["start_time"].value or not self.widgets["end_time"].value:
            error_messages.append("開始時刻と終了時刻を設定してください")
            is_valid = False
        elif self.widgets["start_time"].value > self.widgets["end_time"].value:
            error_messages.append("開始時刻は終了時刻より前である必要があります")
            is_valid = False

        if not self.widgets["interval"].value:
            error_messages.append("インターバルを選択してください")
            is_valid = False

        self._update_error_message(error_messages, is_valid)
        self.widgets["data_fetch"].disabled = not is_valid
        return is_valid

    def _update_error_message(self, error_messages: List[str], is_valid: bool) -> None:
        """エラーメッセージを更新する"""
        if error_messages:
            self.widgets["file_error"].value = (
                '<span style="color: red;">' + "<br>".join(error_messages) + "</span>"
            )
        elif is_valid:
            self.widgets[
                "file_error"
            ].value = '<span style="color: green;">設定ファイルは正常です</span>'
        else:
            self.widgets[
                "file_error"
            ].value = '<span style="color: blue;">設定ファイルをアップロードしてください</span>'

    @staticmethod
    def apply_custom_css() -> None:
        """カスタムCSSを適用する"""
        custom_css = """
        <style>
        .custom-widget {
            height: 32px !important;
        }
        .custom-widget input[type="datetime-local"] {
            width: 100%;
            box-sizing: border-box;
            height: 28px !important;
            line-height: 28px !important;
            padding: 0 4px !important;
        }
        .custom-widget .widget-dropdown select,
        .custom-widget .widget-upload input[type="file"] {
            height: 28px !important;
            line-height: 28px !important;
        }
        .custom-widget .widget-label {
            line-height: 32px !important;
        }
        .widget-upload {
            width: 180px !important;
        }
        .widget-upload .jupyter-button {
            width: 100% !important;
            height: 32px !important;
            line-height: 32px !important;
            padding: 0 4px !important;
        }
        </style>
        """
        display(widgets.HTML(custom_css))

    def _on_data_fetch_click(self, b):
        """データ取得ボタンがクリックされたときの処理"""
        self._log("データ取得ボタンがクリックされました")
        self.widgets["data_fetch_status"].value = "データ取得中..."
        self._log(f"ステータス: {self.widgets['data_fetch_status'].value}")

        # ... データ取得の処理 ...
        self.fetched_data = self.fetch_data()

        self.widgets["data_fetch_status"].value = "データ取得完了"
        self._log(f"ステータス: {self.widgets['data_fetch_status'].value}")

    def fetch_data(self) -> pd.DataFrame:
        """設定ファイルから読み込んだデータとウィジェットの値を使用してデータを取得する"""
        self._log("データ取得を開始します")
        setting_data = self._get_setting_data()
        widget_data = {
            "machine": self.widgets["machine"].value,
            "start_time": self.widgets["start_time"].value,
            "end_time": self.widgets["end_time"].value,
            "interval": self.widgets["interval"].value,
        }

        # ここでデータ取得のロジックを実装
        # target_param_listのparamとtag名称をWidgetsに設定された値をつかって紐づける
        param_tag_dict = dict(
            zip(
                setting_data["tags_setting_df"]["項目名"],
                setting_data["tags_setting_df"][widget_data["machine"]],
            )
        )

        tags = list(param_tag_dict.values())
        start_time = widget_data["start_time"]
        end_time = widget_data["end_time"]
        interval = widget_data["interval"]

        df = dummy_data_fetch_api(tags, start_time, end_time, interval)
        self._log(f"取得したデータ:\n{df.head()}")
        self._log(f"データフレームの列: {df.columns}")
        self._log("データ取得が完了しました")
        return df

    def _on_value_change(self, change: Dict[str, Any]) -> None:
        """ウィジェット値変更時のイベントハンドラ"""
        with self.output:
            self.validate_inputs()

    def _update_widgets_with_file_data(self, change: Dict[str, Any]) -> None:
        """ファイルアップロード時のイベントハンドラ"""
        if change["type"] == "change" and change["name"] == "value":
            if not self.widgets["uploader"].value:
                self._set_initial_message()
                self._disable_widgets()  # ファイルが削除された場合、ウィジェットを無効化
                return

            try:
                setting_data = self._get_setting_data()

                # machineの設定
                self.widgets["machine"].options = setting_data["machine_list"]
                self.widgets["machine"].value = setting_data["machine"]

                # 時間の設定
                self.widgets["start_time"].value = setting_data["start_time"]
                self.widgets["end_time"].value = setting_data["end_time"]

                # intervalの設定
                self.widgets["interval"].value = setting_data["interval"]

                self._enable_widgets()  # ファイルが正常に読み込まれた場合、ウィジェットを有効化
                self.validate_inputs()
                if self.validate_inputs():
                    self.widgets[
                        "file_error"
                    ].value = (
                        '<span style="color: green;">設定ファイルを正常に読み込みました</span>'
                    )
                self.widgets["status"].value = ""  # ステータスメッセージをクリア
            except Exception as e:
                self.widgets[
                    "file_error"
                ].value = f'<span style="color: red;">エラー: {str(e)}</span>'
                self.widgets["status"].value = ""  # ステータスメッセージをクリア
                self._disable_widgets()  # エラーが発生した場合、ウィジェットを無効化

    def _get_setting_data(self) -> Dict[str, Any]:
        """設定ファイルを読み込み、設定データを取得する"""
        try:
            uploaded_file = self.widgets["uploader"].value[0]
            uploaded_file_content = uploaded_file["content"]

            # バイトストリームを作成
            excel_data = io.BytesIO(uploaded_file_content)

            # pd.read_excelにバイトストリームを渡す
            setting_df_dict = pd.read_excel(excel_data, engine="openpyxl", sheet_name=None)

            # 必要なシートが存在するか確認
            if not all(sheet in setting_df_dict for sheet in Constants.REQUIRED_SHEETS):
                raise SettingsError(
                    f"必要なシート {', '.join(Constants.REQUIRED_SHEETS)} が見つかりません"
                )

            # 各シートのデータを取得
            tags_setting_df = setting_df_dict["tag"]
            machine_list = tags_setting_df.columns[2:].tolist()
            tag_dict = tags_setting_df.set_index("項目名").T.to_dict()

            period_setting_df = setting_df_dict["period"]
            period_setting = period_setting_df.iloc[0].to_dict()
            machine = period_setting["Machine"]
            start_time = period_setting["開始日時"]
            end_time = period_setting["終了日時"]
            interval = period_setting["インターバル"]

            param_setting_df = setting_df_dict["param"]
            target_param_list = param_setting_df["項目名"].tolist()

            axis_setting_df = setting_df_dict["axis"]

            # データの検証
            if not machine_list:
                raise SettingsError("マシンリストが空です")
            if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
                raise SettingsError("開始時刻または終了時刻が正しい日時形式ではありません")
            if interval not in Constants.INTERVAL_OPTIONS:
                raise SettingsError(f"無効なインターバル値です: {interval}")

            return {
                "machine": machine,
                "machine_list": machine_list,
                "start_time": start_time,
                "end_time": end_time,
                "interval": interval,
                "tag_dict": tag_dict,
                "tags_setting_df": tags_setting_df,
                "target_param_list": target_param_list,
                "param_setting_df": param_setting_df,
                "axis_setting_df": axis_setting_df,
            }

        except Exception as e:
            self._log(f"設定データの取得中にエラーが発生しました: {str(e)}")
            raise

    def _set_initial_message(self):
        """初期メッセージを設定する"""
        self.widgets[
            "file_error"
        ].value = '<span style="color: red;">設定ファイルをアップロードしてください</span>'

    def _disable_widgets(self):
        """ウィジェットを無効化する"""
        for widget_name in ["machine", "start_time", "end_time", "interval", "data_fetch"]:
            self.widgets[widget_name].disabled = True

    def _enable_widgets(self):
        """ウィジェットを有効化する"""
        for widget_name in ["machine", "start_time", "end_time", "interval", "data_fetch"]:
            self.widgets[widget_name].disabled = False

    def _set_initial_state(self):
        """初期状態を設定する"""
        self._set_initial_message()
        self._disable_widgets()

    def _log(self, message: str) -> None:
        """ログメッセージを追加する"""
        with self.log_output:
            print(message)

    def _on_graph_create_click(self, b):
        """グラフ作成ボタンがクリックされたときの処理"""
        self._log("グラフ作成ボタンがクリックされました")
        self.widgets["graph_status"].value = "グラフ作成中..."
        self._log(f"ステータス: {self.widgets['graph_status'].value}")

        if self.fetched_data is None or self.fetched_data.empty:
            self.widgets["graph_status"].value = "データが取得されていないか、空です"
            return

        try:
            self._create_graph()
            self.widgets["graph_status"].value = "グラフ作成完了。ブラウザで開きました。"
        except Exception as e:
            self._log(f"グラフ作成中にエラーが発生しました: {str(e)}")
            self.widgets["graph_status"].value = f"グラフ作成エラー: {str(e)}"
            self._log(traceback.format_exc())  # スタックトレースをログに記録

        self._log(f"ステータス: {self.widgets['graph_status'].value}")

    def _create_graph(self):
        """Bokehを使用してGraph_Noごとにグラフを作成し、HTMLファイルとして保存する"""
        self._log("グラフ作成を開始します")
        setting_data = self._get_setting_data()
        param_setting_df = setting_data["param_setting_df"]
        tag_dict = setting_data["tag_dict"]
        machine = setting_data["machine"]

        # axis_setting_dfを取得
        axis_setting_df = setting_data["axis_setting_df"]

        # 共通のX軸範囲を設定
        x_range = DataRange1d()

        # 自動色設定用のカラーパレット
        color_palette = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

        # グラフ作成ループの前に最大凡例長を計算
        max_legend_length = 0
        for _, row in param_setting_df.iterrows():
            legend_name = row["凡例表示名"]
            max_legend_length = max(max_legend_length, len(legend_name))

        # 文字数に基づいて幅を計算（1文字あたり約6ピクセルと仮定）
        label_width = max_legend_length * 6

        # Graph_Noごとにグラフを作成
        graphs = []
        for graph_no in param_setting_df["Graph_No"].unique():
            p = figure(
                title=f"データグラフ (Graph_No: {graph_no})",
                x_axis_label="時間",
                x_axis_type="datetime",
                width=800,
                height=400,
                x_range=x_range,  # 共通のX軸範囲を使用
                tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"],
            )

            params_for_graph = param_setting_df[param_setting_df["Graph_No"] == graph_no]

            # Y軸の設定
            y_ranges = {}
            for i, axis_no in enumerate(params_for_graph["Axis_No"].unique()):
                axis_settings = axis_setting_df[
                    (axis_setting_df["Graph_No"] == graph_no)
                    & (axis_setting_df["Axis_No"] == axis_no)
                ].iloc[0]

                # Y軸のレンジ設定
                y_range = DataRange1d()
                if pd.notna(axis_settings["レンジ下限"]) and pd.notna(axis_settings["レンジ上限"]):
                    y_range.start = axis_settings["レンジ下限"]
                    y_range.end = axis_settings["レンジ上限"]

                y_ranges[axis_no] = y_range
                axis_name = f"Axis_{axis_no}"
                if i == 0:
                    p.yaxis.axis_label = axis_settings["軸ラベル"]
                    p.y_range = y_range
                else:
                    p.extra_y_ranges[axis_name] = y_range
                    new_axis = LinearAxis(
                        y_range_name=axis_name, axis_label=axis_settings["軸ラベル"]
                    )
                    p.add_layout(new_axis, "left")

            # 全てのパラメータのデータを1つのColumnDataSourceにまとめる
            source_data = {"x": self.fetched_data["time"]}
            for _, row in params_for_graph.iterrows():
                param = row["項目名"]
                col_name = tag_dict[param][machine]
                if col_name in self.fetched_data.columns:
                    source_data[param] = self.fetched_data[col_name]

            source = ColumnDataSource(data=source_data)

            # 各パラメータの線をプロット
            for i, (_, row) in enumerate(params_for_graph.iterrows()):
                param = row["項目名"]
                color = row["色"] if pd.notna(row["色"]) else color_palette[i % len(color_palette)]
                legend_name = row["凡例表示名"]
                line_style = row["線種"] if pd.notna(row["線種"]) else "solid"
                line_width = row["線幅"] if pd.notna(row["線幅"]) else 1
                axis_no = row["Axis_No"]

                y_range_name = (
                    f"Axis_{axis_no}"
                    if axis_no != params_for_graph["Axis_No"].unique()[0]
                    else "default"
                )
                p.line(
                    "x",
                    param,
                    source=source,
                    legend_label=legend_name,
                    color=color,
                    line_dash=line_style,
                    line_width=line_width,
                    y_range_name=y_range_name,
                )

            # HoverToolの設定
            tooltips = [
                (row["凡例表示名"], f"@{{{row['項目名']}}}{{0.00}}")
                for _, row in params_for_graph.iterrows()
            ]
            tooltips.insert(0, ("日時", "@x{%Y-%m-%d %H:%M:%S}"))

            hover = HoverTool(tooltips=tooltips, formatters={"@x": "datetime"}, mode="mouse")
            p.add_tools(hover)

            # 凡例の設定
            if p.legend and p.legend.items:
                new_legend = Legend(items=p.legend.items, label_width=label_width)
                p.legend.visible = False
                p.add_layout(new_legend, "right")

            p.xaxis.formatter = DatetimeTickFormatter(
                hours="%Y-%m-%d %H:%M",
                days="%Y-%m-%d %H:%M",
            )
            p.xaxis.major_label_orientation = 0.7
            p.min_border_bottom = 100

            graphs.append(p)

        # 全てのグラフを縦に並べる
        layout = column(graphs)

        # HTMLファイルとして保存
        output_file_path = os.path.join(self.output_dir, "graphs.html")
        output_file(output_file_path, title="データグラフ")  # タイトルを設定
        save(layout, filename=output_file_path, title="データグラフ", resources=CDN)
        self._log(f"グラフを保存しました: {output_file_path}")

        # ブラウザでHTMLファイルを開く
        webbrowser.open("file://" + os.path.realpath(output_file_path))


def show_widgets():
    """ウィジェットを表示する"""
    data_widget = DataWidget()
    DataWidget.apply_custom_css()
    display(data_widget.layout, data_widget.output)
