from dataclasses import dataclass, field


@dataclass
class Data:
    x: list[int] = field(default_factory=list)
    y: list[int] = field(default_factory=list)


@dataclass
class FigureSettings:
    width: int
    height: int
    x_range: tuple[int, int]
    y_range: tuple[int, int]
    title: str


# 軸の設定をするクラス
@dataclass
class AxisSettings:
    x_range: tuple[int, int]
    y_range: tuple[int, int]
    title: str
    label_font_size: str
    tick_label_font_size: str


data1 = Data(x=[1, 2, 3, 4, 5], y=[6, 7, 2, 4, 5])
data2 = Data(x=[1, 2, 3, 4, 5], y=[6000, 7000, 2000, 4000, 5000])

figure_settings1 = FigureSettings(
    width=250,
    height=250,
    x_range=(0, 10),
    y_range=(0, 10),
    title="Sample 1",
)

axis_settings1 = AxisSettings(
    x_range=(0, 10),
    y_range=(0, 10),
    title="Sample 1",
    label_font_size="10pt",
    tick_label_font_size="10pt",
)

figure_settings2 = FigureSettings(
    width=500,
    height=250,
    x_range=(0, 10),
    y_range=(0, 10000),
    title="Sample 2",
)

axis_settings2 = AxisSettings(
    x_range=(0, 10),
    y_range=(0, 10000),
    title="Sample 2",
    label_font_size="10pt",
    tick_label_font_size="10pt",
)
