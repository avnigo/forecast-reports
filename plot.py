import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as io

from typing import Iterator
from itertools import pairwise
from pathlib import Path
from datetime import date, datetime

from extract import Area, Process
from pull import Period
from reference import species_name, quant_name, fig_defaults


def make_traces(df: pd.DataFrame, fig: go.Figure, process: Process) -> dict:
    def get_colors(df: pd.DataFrame, level:int = 0) -> dict:
        return dict(
            zip(df.columns.levels[level].to_list(), px.colors.qualitative.D3)
        )

    def hex_to_rgb(hex_color: str) -> tuple:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = hex_color * 2
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    def quant_options():
        return {
            "name": f"{species_name.get(species, species)} ({quant_name[sub]})",
            "showlegend": True if sub == 0.5 else False,
            "line": {
                "color": trace_colors[species],
                "dash": "dashdot" if sub in (0.25, 0.75) 
                    else "solid" if sub == 0.5 else "dot",
                "shape": "spline",
                "smoothing": 0.9,
                "width": 2 if sub == 0.5 else 0.5,
            },
            "hovertemplate": "<b>%{y:.1f}</b> μg/m³",
            "fill": "tonexty" if sub != 0 else "none",
            "fillcolor": f"rgba{(*hex_to_rgb(trace_colors[species]), 0.1)}",
        }

    def point_options():
        return {
            "name": species_name.get(species, species),
            "showlegend": True if sub == df.columns.levels[1][0] else False,
            "line": {
                "color": trace_colors[sub], 
                "shape": "spline",
                "smoothing": 0.9,
                "width": 1.5,
            },
            "hovertemplate": f"<b>{sub}</b>" \
                + "<br>%{x:%A}<br><b>%{y:.1f}</b> μg/m³",
        }

    trace_colors = get_colors(df, 0 if process == Process.QUANTILE else 1)

    for species, sub in df.columns:
        match process:
            case Process.QUANTILE:
                options = quant_options()
            case Process.POINTS:
                options = point_options()

        fig.add_scatter(
            **{
                "uid": process.name,
                "legendgroup": f"{process.name}.{species}",
                "x": df.index,
                "y": df[species][sub],
                "mode": "lines",
                "visible": True if "PM10" in species else "legendonly",
                "legendgrouptitle": {
                    "text": " " if species == "Dust" else None,
                    "font": {"size": 14},
                },
                **options
            }
        )

    return fig


def publish(
        fig: go.Figure,
        datestamp: date,
        out_dir: Path = Path(__file__).parent.absolute() / "out"
    ) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.write_html(
        out_dir / f"forecast.html",
        config={
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"{datestamp}_forecast"},
            "displaylogo": False
        },
        include_plotlyjs="cdn",
        # auto_open=True,
        # full_html=True,
    )


def get_updates(views: dict) -> dict:
    return {
        "xanchor": "left",
        "yanchor": "bottom",
        "x": 1.0,
        "y": 1.0,
        "pad": {"r": 20, "b": 27},
        "direction": "down",
        # "type": "buttons",
        # "font_size": 14,
        "active": 0,
        "buttons": [
            {
                "label": "<b>CAMS</b>-<i>Cyprus</i>",
                "method": "update",
                "args": [
                    {
                        "visible": views[0],
                    },
                    {
                        "title": "<b>CAMS Air Quality Forecast:</b><br> — <i>Distribution over Cyprus</i>",
                        "hovermode": "x unified",
                        "yaxis": {
                            "title": "Concentration (μg/m³)",
                            **fig_defaults["yaxis"],
                        },
                        "xaxis": {
                            "nticks": 9,
                            **fig_defaults["xaxis"],
                        },
                        "legend": {
                            "font": {"size": 16},
                            "itemsizing": "constant",
                        }
                    },
                ],
            },
            {
                "label": "<b>CAMS</b>-<i>Stations</i>",
                "method": "update",
                "args": [
                    {
                        "visible": views[1],
                    },
                    {
                        "title": "<b>CAMS Air Quality Forecast:</b><br> — <i>Station Trends</i>",
                        "hovermode": "closest",
                        "yaxis_title": "Concentration (μg/m³)",
                        "yaxis": {
                            "title": "Concentration (μg/m³)",
                            **fig_defaults["yaxis"],
                        },
                        "xaxis": {
                            "nticks": 9,
                            **fig_defaults["xaxis"],
                        },
                        "legend": {
                            "font": {"size": 16},
                            "itemsizing": "constant",
                        }
                    },
                ],
            },
            {
                "label": "<b>AEMET</b>-<i>Cyprus</i>",
                "method": "update",
                "args": [
                    {
                        "visible": views[2],
                    },
                    {
                        "title": "<b>WMO/AEMET Forecast:</b><br> — <i>Dust Surface Concentration over Cyprus</i>",
                        "hovermode": "x unified",
                        "yaxis": {
                            "title": "Concentration (μg/m³)",
                            **fig_defaults["yaxis"],
                        },
                        "xaxis": {
                            "nticks": 9,
                            **fig_defaults["xaxis"],
                        },
                        "legend": {
                            "font": {"size": 12},
                            "x": 1.00,
                        }
                    },
                ],
            },
            {
                "label": "<b>AEMET</b>-<i>EP</i>",
                "method": "update",
                "args": [
                    {
                        "visible": views[3],
                    },
                    {
                        "title": "<b>WMO/AEMET Forecast:</b><br> — <i>Daily Dust Exceedance Probabilities (EP) over Cyprus</i>",
                        "yaxis": {
                            "title": "Daily exceedance probabilites over value (%)",
                            "range": [0, 100],
                            **fig_defaults["yaxis"],
                        },
                        "hovermode": "closest",
                        "xaxis": {
                            "dtick": "1D",
                            **fig_defaults["xaxis"],
                        },
                    },
                ],
            },
            {
                "label": "<b>View all</b>",
                "method": "update",
                "args": [
                    {
                        "visible": views[4],
                    },
                    {
                        "title": "<b>CAMS—WMO/AEMET Forecast Comparison:</b><br> — <i>All available traces</i>",
                        "hovermode": "closest",
                        "yaxis": {
                            "title": "Concentration (μg/m³)",
                            **fig_defaults["yaxis"],
                        },
                        "xaxis": {
                            "nticks": 9,
                            **fig_defaults["xaxis"],
                        },
                        "legend": {
                            "font": {"size": 12},
                            "x": 1.00,
                        }
                    },
                ],
            },
        ]
    }


def load_json_fig(fig_path: Path) -> go.Figure:
    return io.read_json(fig_path)


def add_fig_group(fig: go.Figure, other: go.Figure, uuid: str = None) -> go.Figure:
    def add_meta(f: go.Figure, **kwargs) -> go.Figure:
        if kwargs["uuid"]:
            f["uid"] = kwargs["uuid"]
            return f

        if f["visible"] == True:
            f["fill"] = "tozeroy"
            f["line"]["color"] = "black"
            f["fillcolor"] = "rgba(0, 0, 0, 0.1)"
        f["uid"] = "AEMET"
        f["name"] = f["name"].split(" ")[0]
        f["line"] = dict(shape="spline", dash="solid", smoothing=0.7)
        f["legendgrouptitle_text"] = " " if i == 0 else None
        f["legendgrouptitle"]["font"]["size"] = 14
        f["x"] = pd.DatetimeIndex(
            f["x"],
            tz="UTC"
        ).tz_convert("Asia/Nicosia").strftime("%Y-%m-%dT%H:%M:00").to_list()
        return f

    for i, f in enumerate(other.data):
        add_meta(f, uuid=uuid)
        fig.add_trace(f)
    return fig


def make_fig_collection(
        df: Area,
        fig: go.Figure,
        more_figs: list[go.Figure],
    ) -> tuple[go.Figure, dict]:

    def make_views(views: list, sizes: list) -> dict:
        all_views = {}
        for i, val_range in enumerate([range(x, y) for x,y in pairwise(sizes)]):
            array = np.array(views)
            array[list(set(range(sizes[-1])) - set(val_range))] = False
            all_views[i] = [
                True if x == "True"
                else False if x == "False"
                else x
                for x in array
            ]
        return {
            **all_views,
            4: list(
                map(lambda x: y[0] if len(y:=list(filter(bool, x)))>0 else False,
                zip(all_views[0], all_views[1], all_views[2]))
            )
        }

    def mark_current_time() -> list[dict]:
        return [
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'paper',
                'x0': datetime.now(),
                'y0': 0,
                'x1': datetime.now(),
                'y1': 1,
                'opacity': 0.07,
                'line': {
                    'color': 'grey',
                    'width': 5,
                    'dash': 'dot',
                }
            }
        ]



    sizes = [0]
    for tbl in df:
        fig = make_traces(tbl.data, fig, tbl.process)
        sizes.append((len(fig.data)))

    for other_fig in more_figs:
        fig = add_fig_group(
            fig,
            other_fig,
            uuid="PROBS" if not other_fig.layout.title.text else None
        )
        sizes.append((len(fig.data)))

    views = make_views([f.visible for f in fig.data], sizes)
    [fig.add_shape(**shape) for shape in mark_current_time()]

    return fig, views


def create_plots(
        df: Area|Iterator[Area],
        more_figs: list[go.Figure],
        datestamp: date = Period().end_date
    ) -> go.Figure:

    fig = go.Figure()

    fig, views = make_fig_collection(df, fig, more_figs)

    fig.update_layout(
        yaxis_title="Concentration (μg/m³)",
        title="<b>CAMS Air Quality Forecast:</b><br> — <i>Distribution over Cyprus</i>",
        hovermode="x unified",
        legend=dict(font_size=16, itemsizing="constant"),
        hoverlabel=dict(font_size=16),
        plot_bgcolor="white",
        xaxis=fig_defaults["xaxis"],
        yaxis=fig_defaults["yaxis"],
        updatemenus=[
            get_updates(views)
        ]
    )

    for uuid in ["POINTS", "AEMET", "PROBS"]:
        fig.update_traces(selector=dict(uid=uuid), patch=dict(visible=False), overwrite=True)

    publish(fig, datestamp)

    return fig

