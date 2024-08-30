import io
import os
import tempfile
import traceback
import webbrowser
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import ipywidgets as widgets
import numpy as np
import pandas as pd
import pi_data_fetch as pi
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

debug = True


class Constants:
    MACHINE_OPTIONS: List[str] = ["machine1", "machine2", "machine3"]
    INTERVAL_OPTIONS: List[str] = ["1s", "1m", "1d"]
    WIDGET_STYLE: Dict[str, Any] = {
        "layout": widgets.Layout(width="300px", height="32px"),
        "style": {"description_width": "100px"},
    }
    REQUIRED_SHEETS: List[str] = ["tag", "period", "param", "axis"]
    BUTTON_LAYOUT = widgets.Layout(width="180px", height="32px")
    COLOR_PALETTE: List[str] = [
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


# ダミーデータ生成用のAPI関数
def dummy_data_fetch_api(
    tags: List[str], start_time: datetime, end_time: datetime, interval: str
) -> pd.DataFrame:
    """ダミーデータを生成するAPI関数"""
    if debug:
        time_range = pd.date_range(start=start_time, end=end_time, freq=interval)
        data = {}
        for tag in tags:
            data[tag] = np.random.randn(len(time_range))
        return pd.DataFrame(data, index=time_range)
    else:
        return pi.fetch_data(tags, start_time, end_time, interval)


class SettingsError(Exception):
    pass


class SettingsManager:
    def __init__(self):
        self.setting_data = None

    def load_settings(self, file_content):
        try:
            excel_data = io.BytesIO(file_content)
            setting_df_dict = pd.read_excel(excel_data, engine="openpyxl", sheet_name=None)

            if not all(sheet in setting_df_dict for sheet in Constants.REQUIRED_SHEETS):
                raise SettingsError(
                    f"必要なシート {', '.join(Constants.REQUIRED_SHEETS)} が見つかりません"
                )

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

            if not machine_list:
                raise SettingsError("マシンリストが空です")
            if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
                raise SettingsError("開始時刻または終了時刻が正しい日時形式ではありません")
            if interval not in Constants.INTERVAL_OPTIONS:
                raise SettingsError(f"無効なインターバル値です: {interval}")

            self.setting_data = {
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
            raise SettingsError(f"設定データの取得中にエラーが発生しました: {str(e)}")

    def get_setting_data(self):
        return self.setting_data


class DataFetcher:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def _parse_interval(self, interval):
        if interval.endswith("s"):
            return pd.Timedelta(seconds=int(interval[:-1]))
        elif interval.endswith("m"):
            return pd.Timedelta(minutes=int(interval[:-1]))
        elif interval.endswith("d"):
            return pd.Timedelta(days=int(interval[:-1]))
        else:
            raise ValueError(f"不正なインターバル形式: {interval}")

    def estimate_data_size(self, start_time, end_time, interval):
        # インターバルをTimedeltaに変換
        interval_timedelta = self._parse_interval(interval)

        # データポイントの数を計算
        time_range = end_time - start_time
        num_data_points = int(time_range / interval_timedelta) + 1

        # タグの数を取得
        setting_data = self.settings_manager.get_setting_data()
        param_tag_dict = dict(
            zip(
                setting_data["tags_setting_df"]["項目名"],
                setting_data["tags_setting_df"][setting_data["machine"]],
            )
        )
        num_tags = len(param_tag_dict)

        # 予想されるデータフレームのサイズを計算（バイト単位）
        estimated_size_bytes = num_data_points * (
            8 + 8 * num_tags
        )  # 8バイトはタイムスタンプ用、8バイトは各タグの値用

        return num_data_points, num_tags, estimated_size_bytes

    def fetch_data(self, start_time, end_time, interval):
        # データサイズの見積もり
        num_data_points, num_tags, estimated_size_bytes = self.estimate_data_size(
            start_time, end_time, interval
        )
        self.workbench._log(f"予想されるデータポイント数: {num_data_points}")
        self.workbench._log(f"タグの数: {num_tags}")
        self.workbench._log(f"予想されるデータサイズ: {estimated_size_bytes / (1024*1024):.2f} MB")

        setting_data = self.settings_manager.get_setting_data()
        param_tag_dict = dict(
            zip(
                setting_data["tags_setting_df"]["項目名"],
                setting_data["tags_setting_df"][setting_data["machine"]],
            )
        )

        tags = list(param_tag_dict.values())
        self.workbench._log(f"取得するタグ: {tags}")
        self.workbench._log(
            f"開始時間: {start_time}, 終了時間: {end_time}, インターバル: {interval}"
        )

        try:
            df = dummy_data_fetch_api(tags, start_time, end_time, interval)
            self.workbench._log(f"取得したデータの形状: {df.shape}")
            self.workbench._log(f"データのカラム: {df.columns}")
            self.workbench._log(f"データのサンプル:\n{df.head()}")

            # 実際のデータサイズを計算
            actual_size_bytes = df.memory_usage(deep=True).sum()
            self.workbench._log(f"実際のデータサイズ: {actual_size_bytes / (1024*1024):.2f} MB")

            return df
        except Exception as e:
            self.workbench._log(f"データ取得中にエラーが発生しました: {str(e)}")
            raise


class GraphCreator:
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def create_graph(self, data):
        setting_data = self.settings_manager.get_setting_data()
        param_setting_df = setting_data["param_setting_df"]
        tag_dict = setting_data["tag_dict"]
        machine = setting_data["machine"]
        axis_setting_df = setting_data["axis_setting_df"]

        x_range = DataRange1d()
        max_legend_length = self._calculate_max_legend_length(param_setting_df)
        label_width = max_legend_length * 6

        graphs = []
        for graph_no in param_setting_df["Graph_No"].unique():
            p = self._create_figure(graph_no, x_range)
            params_for_graph = param_setting_df[param_setting_df["Graph_No"] == graph_no]
            y_ranges = self._setup_y_axes(p, params_for_graph, axis_setting_df, graph_no)
            source = self._create_data_source(params_for_graph, tag_dict, machine, data)
            self._plot_lines(p, params_for_graph, source, y_ranges)
            self._setup_hover_tool(p, params_for_graph)
            self._setup_legend(p, label_width)
            self._format_axes(p)
            graphs.append(p)

        self._save_and_open_graphs(graphs)

    def _calculate_max_legend_length(self, param_setting_df: pd.DataFrame) -> int:
        return max(len(row["凡例表示名"]) for _, row in param_setting_df.iterrows())

    def _create_figure(self, graph_no: int, x_range: DataRange1d) -> figure:
        return figure(
            title=f"データグラフ (Graph_No: {graph_no})",
            x_axis_label="時間",
            x_axis_type="datetime",
            width=1200,  # 横幅を800から1200に変更
            height=400,
            x_range=x_range,
            tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"],
        )

    def _setup_y_axes(
        self,
        p: figure,
        params_for_graph: pd.DataFrame,
        axis_setting_df: pd.DataFrame,
        graph_no: int,
    ) -> Dict[int, DataRange1d]:
        y_ranges = {}
        for i, axis_no in enumerate(params_for_graph["Axis_No"].unique()):
            axis_settings = axis_setting_df[
                (axis_setting_df["Graph_No"] == graph_no) & (axis_setting_df["Axis_No"] == axis_no)
            ].iloc[0]
            y_range = self._create_y_range(axis_settings)
            y_ranges[axis_no] = y_range
            self._add_y_axis(p, y_range, axis_settings, i == 0)
        return y_ranges

    def _create_y_range(self, axis_settings: pd.Series) -> DataRange1d:
        y_range = DataRange1d()
        if pd.notna(axis_settings["レンジ下限"]) and pd.notna(axis_settings["レンジ上限"]):
            y_range.start = axis_settings["レンジ下限"]
            y_range.end = axis_settings["レンジ上限"]
        return y_range

    def _add_y_axis(
        self, p: figure, y_range: DataRange1d, axis_settings: pd.Series, is_primary: bool
    ) -> None:
        if is_primary:
            p.yaxis.axis_label = axis_settings["軸ラベル"]
            p.y_range = y_range
        else:
            axis_name = f"Axis_{axis_settings['Axis_No']}"
            p.extra_y_ranges[axis_name] = y_range
            new_axis = LinearAxis(y_range_name=axis_name, axis_label=axis_settings["軸ラベル"])
            p.add_layout(new_axis, "left")

    def _create_data_source(
        self,
        params_for_graph: pd.DataFrame,
        tag_dict: Dict[str, Any],
        machine: str,
        data: pd.DataFrame,
    ) -> ColumnDataSource:
        source_data = {"x": data.index}
        for _, row in params_for_graph.iterrows():
            param = row["項目名"]
            col_name = tag_dict[param][machine]
            if col_name in data.columns:
                source_data[param] = data[col_name]
        return ColumnDataSource(data=source_data)

    def _plot_lines(
        self,
        p: figure,
        params_for_graph: pd.DataFrame,
        source: ColumnDataSource,
        y_ranges: Dict[int, DataRange1d],
    ) -> None:
        for i, (_, row) in enumerate(params_for_graph.iterrows()):
            param = row["項目名"]
            color = (
                row["色"]
                if pd.notna(row["色"])
                else Constants.COLOR_PALETTE[i % len(Constants.COLOR_PALETTE)]
            )
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

    def _setup_hover_tool(self, p: figure, params_for_graph: pd.DataFrame) -> None:
        tooltips = [
            (row["凡例表示名"], f"@{{{row['項目名']}}}{{0.00}}")
            for _, row in params_for_graph.iterrows()
        ]
        tooltips.insert(0, ("日時", "@x{%Y-%m-%d %H:%M:%S}"))
        hover = HoverTool(tooltips=tooltips, formatters={"@x": "datetime"}, mode="mouse")
        p.add_tools(hover)

    def _setup_legend(self, p: figure, label_width: int) -> None:
        if p.legend and p.legend.items:
            new_legend = Legend(items=p.legend.items, label_width=label_width)
            p.legend.visible = False
            p.add_layout(new_legend, "right")

    def _format_axes(self, p: figure) -> None:
        p.xaxis.formatter = DatetimeTickFormatter(
            hours="%Y-%m-%d %H:%M",
            days="%Y-%m-%d %H:%M",
        )
        p.xaxis.major_label_orientation = 0.7
        p.min_border_bottom = 100

    def _save_and_open_graphs(self, graphs: List[figure]) -> None:
        layout = column(graphs, sizing_mode="stretch_width")  # sizing_modeを追加
        output_file_path = os.path.join("output", "graphs.html")
        output_file(output_file_path, title="データグラフ")
        save(layout, filename=output_file_path, title="データグラフ", resources=CDN)
        webbrowser.open("file://" + os.path.realpath(output_file_path))


class WidgetManager:
    def __init__(self):
        self.widgets = self._create_widgets()

    def _create_widgets(self) -> Dict[str, widgets.Widget]:
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
        widget_kwargs = Constants.WIDGET_STYLE.copy()
        widget_kwargs.update(kwargs)
        widget = widget_type(**widget_kwargs)
        widget.add_class("custom-widget")
        return widget

    def update_widgets(self, setting_data):
        self.widgets["machine"].options = setting_data["machine_list"]
        self.widgets["machine"].value = setting_data["machine"]
        self.widgets["start_time"].value = setting_data["start_time"]
        self.widgets["end_time"].value = setting_data["end_time"]
        self.widgets["interval"].value = setting_data["interval"]


class DataAnalysisWorkbench:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.data_fetcher = DataFetcher(self.settings_manager)
        self.data_fetcher.workbench = self
        self.graph_creator = GraphCreator(self.settings_manager)
        self.widget_manager = WidgetManager()

        self.output = widgets.Output(layout={"border": "1px solid black"})
        self.log_output = widgets.Output()
        self.log_accordion = self._create_log_accordion()
        self.layout = self._create_layout()
        self._create_event_handlers()
        self._set_initial_state()
        self.fetched_data = None

    def _create_layout(self) -> widgets.VBox:
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
        return layout

    def _create_file_upload_section(self) -> widgets.VBox:
        return widgets.HBox(
            [
                self.widget_manager.widgets["uploader"],
                self.widget_manager.widgets["file_error"],
            ],
            layout=widgets.Layout(width="100%", align_items="flex-start"),
        )

    def _create_data_fetch_section(self) -> widgets.HBox:
        section = widgets.HBox(
            [
                self.widget_manager.widgets["data_fetch"],
                self.widget_manager.widgets["data_fetch_status"],
            ],
            layout=widgets.Layout(align_items="center", margin="10px 0"),
        )
        return section

    def _create_graph_section(self) -> widgets.HBox:
        section = widgets.HBox(
            [
                self.widget_manager.widgets["graph_create"],
                self.widget_manager.widgets["graph_status"],
            ],
            layout=widgets.Layout(align_items="center", margin="10px 0"),
        )
        return section

    def _create_data_settings_section(self) -> widgets.Accordion:
        return widgets.Accordion(
            children=[
                widgets.VBox(
                    [
                        self.widget_manager.widgets["machine"],
                        widgets.HBox(
                            [
                                self.widget_manager.widgets["start_time"],
                                self.widget_manager.widgets["time_error"],
                            ],
                            layout=widgets.Layout(width="100%"),
                        ),
                        self.widget_manager.widgets["end_time"],
                        self.widget_manager.widgets["interval"],
                        widgets.HBox(
                            [
                                widgets.Box(layout=widgets.Layout(width="140px")),
                                self.widget_manager.widgets["data_fetch"],
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
        self.widget_manager.widgets["data_fetch"].on_click(self.on_data_fetch_click)
        for widget_name in ["machine", "start_time", "end_time", "interval", "uploader"]:
            self.widget_manager.widgets[widget_name].observe(self.on_value_change, names="value")
        self.widget_manager.widgets["uploader"].observe(self.on_file_upload, names="value")
        self.widget_manager.widgets["graph_create"].on_click(self.on_graph_create_click)

    def validate_inputs(self) -> bool:
        is_valid = True
        error_messages = []

        if not self.widget_manager.widgets["uploader"].value:
            error_messages.append("設定ファイルをアップロードしてください")
            is_valid = False

        if not self.widget_manager.widgets["machine"].value:
            error_messages.append("マシンを選択してください")
            is_valid = False

        if (
            not self.widget_manager.widgets["start_time"].value
            or not self.widget_manager.widgets["end_time"].value
        ):
            error_messages.append("開始時刻と終了時刻を設定してください")
            is_valid = False
        elif (
            self.widget_manager.widgets["start_time"].value
            > self.widget_manager.widgets["end_time"].value
        ):
            error_messages.append("開始時刻は終了時刻より前である必要があります")
            is_valid = False

        if not self.widget_manager.widgets["interval"].value:
            error_messages.append("インターバルを選択してください")
            is_valid = False

        self._update_error_message(error_messages, is_valid)
        self.widget_manager.widgets["data_fetch"].disabled = not is_valid
        return is_valid

    def _update_error_message(self, error_messages: List[str], is_valid: bool) -> None:
        if error_messages:
            self.widget_manager.widgets["file_error"].value = (
                '<span style="color: red;">' + "<br>".join(error_messages) + "</span>"
            )
        elif is_valid:
            self.widget_manager.widgets[
                "file_error"
            ].value = '<span style="color: green;">設定ファイルは正常です</span>'
        else:
            self.widget_manager.widgets[
                "file_error"
            ].value = '<span style="color: blue;">設定ファイルをアップロードしてください</span>'

    @staticmethod
    def apply_custom_css() -> None:
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

    def on_data_fetch_click(self, b):
        self._log("データ取得ボタンがクリックされました")
        self.widget_manager.widgets["data_fetch_status"].value = "データ取得中..."
        self._log(f"ステータス: {self.widget_manager.widgets['data_fetch_status'].value}")

        start_time = self.widget_manager.widgets["start_time"].value
        end_time = self.widget_manager.widgets["end_time"].value
        interval = self.widget_manager.widgets["interval"].value

        # データサイズの見積もり
        num_data_points, num_tags, estimated_size_bytes = self.data_fetcher.estimate_data_size(
            start_time, end_time, interval
        )
        self._log(f"予想されるデータポイント数: {num_data_points}")
        self._log(f"タグの数: {num_tags}")
        self._log(f"予想されるデータサイズ: {estimated_size_bytes / (1024*1024):.2f} MB")

        try:
            self.fetched_data = self.data_fetcher.fetch_data(start_time, end_time, interval)
            self.widget_manager.widgets["data_fetch_status"].value = "データ取得完了"
            self._log(f"取得したデータの形状: {self.fetched_data.shape}")

            # 実際のデータサイズを計算
            actual_size_bytes = self.fetched_data.memory_usage(deep=True).sum()
            self._log(f"実際のデータサイズ: {actual_size_bytes / (1024*1024):.2f} MB")

            # 予想サイズと実際のサイズの差を計算
            size_difference = actual_size_bytes - estimated_size_bytes
            self._log(f"サイズの差異: {size_difference / (1024*1024):.2f} MB")

        except Exception as e:
            self.widget_manager.widgets["data_fetch_status"].value = f"データ取得エラー: {str(e)}"
            self._log(f"データ取得中にエラーが発生しました: {str(e)}")

        self._log(f"ステータス: {self.widget_manager.widgets['data_fetch_status'].value}")

    def on_file_upload(self, change):
        if change["type"] == "change" and change["name"] == "value":
            if not self.widget_manager.widgets["uploader"].value:
                self._set_initial_message()
                self._disable_widgets()
                return

            try:
                uploaded_file = self.widget_manager.widgets["uploader"].value[0]
                uploaded_file_content = uploaded_file["content"]
                self.settings_manager.load_settings(uploaded_file_content)
                setting_data = self.settings_manager.get_setting_data()

                self.widget_manager.update_widgets(setting_data)
                self._enable_widgets()
                self.validate_inputs()
                if self.validate_inputs():
                    self.widget_manager.widgets[
                        "file_error"
                    ].value = (
                        '<span style="color: green;">設定ファイルを正常に読み込みました</span>'
                    )
                self.widget_manager.widgets["status"].value = ""
            except Exception as e:
                self.widget_manager.widgets[
                    "file_error"
                ].value = f'<span style="color: red;">エラー: {str(e)}</span>'
                self.widget_manager.widgets["status"].value = ""
                self._disable_widgets()

    def _set_initial_message(self):
        self.widget_manager.widgets[
            "file_error"
        ].value = '<span style="color: red;">設定ファイルをアップロードしてください</span>'

    def _disable_widgets(self):
        for widget_name in ["machine", "start_time", "end_time", "interval", "data_fetch"]:
            self.widget_manager.widgets[widget_name].disabled = True

    def _enable_widgets(self):
        for widget_name in ["machine", "start_time", "end_time", "interval", "data_fetch"]:
            self.widget_manager.widgets[widget_name].disabled = False

    def _set_initial_state(self):
        self._set_initial_message()
        self._disable_widgets()

    def _log(self, message: str) -> None:
        with self.log_output:
            print(message)

    def on_graph_create_click(self, b):
        self._log("グラフ作成ボタンがクリックされました")
        self.widget_manager.widgets["graph_status"].value = "グラフ作成中..."
        self._log(f"ステータス: {self.widget_manager.widgets['graph_status'].value}")

        if self.fetched_data is None or self.fetched_data.empty:
            self.widget_manager.widgets["graph_status"].value = "データが取得されていないか、空です"
            return

        try:
            self.graph_creator.create_graph(self.fetched_data)
            self.widget_manager.widgets[
                "graph_status"
            ].value = "グラフ作成完了。ブラウザで開きました。"
        except Exception as e:
            self._log(f"グラフ作成中にエラーが発生しました: {str(e)}")
            self.widget_manager.widgets["graph_status"].value = f"グラフ作成エラー: {str(e)}"
            self._log(traceback.format_exc())

        self._log(f"ステータス: {self.widget_manager.widgets['graph_status'].value}")

    def _create_log_accordion(self) -> widgets.Accordion:
        log_accordion = widgets.Accordion(children=[self.log_output])
        log_accordion.set_title(0, "ログ")
        log_accordion.selected_index = None
        return log_accordion

    def on_value_change(self, change: Dict[str, Any]) -> None:
        with self.output:
            self.validate_inputs()


def show_widgets():
    workbench = DataAnalysisWorkbench()
    DataAnalysisWorkbench.apply_custom_css()
    display(workbench.layout, workbench.output)
