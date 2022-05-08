import pandas as pd
import geopandas as gp
import plotly.express as px
import plotly.graph_objects as go

from datetime import date, datetime, timedelta
from pathlib import Path

def read_files(
        data_path: Path = Path(__file__).parent.absolute() / "data/AEMET",
        day: date = date.today() - timedelta(days=1),
        join_on_shp: Path = Path(__file__).parent.absolute() / "data/ref/cyprus.geojson",
    ) -> list[pd.DataFrame]:

    def format_df(name: str, df: pd.DataFrame) -> pd.DataFrame:
        (day_no, date, *_, level) = name.split('_')
        df['day'] = datetime.strptime(date, "%Y%m%d") + timedelta(days=int(day_no))
        df['level'] = int(level)
        df['probability'] = df['value'].astype(int) - 5
        return df

    return [
        format_df(
            name=file.stem,
            df=gp.read_file(
                file,
                mask=gp.read_file(join_on_shp),
                ignore_geometry=True
            )
        )
        for file in (data_path / f"{day:%Y%m%d}").glob('*.geojson')
    ]


def get_probability_df(tbls: list[pd.DataFrame]) -> pd.DataFrame:
    return (
        # gp.GeoDataFrame(pd.concat(tbls))
        pd.concat(tbls)
            .drop(columns=['id', 'value'])
            .set_index(['day', 'level'])
            .sort_index()
            .groupby(['day', 'level'])
            .max()
            # .unstack()
            .reset_index()
    )


def make_plot(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="day",
        y="probability",
        barmode="group",
        color="level",
        color_discrete_sequence=["khaki", "chocolate", "firebrick", "maroon"]
    )
    fig.for_each_trace(
        lambda t: t.update(
                texttemplate=f'> {t.legendgroup} μg/m³',
                hovertemplate='<b>%{y}%</b> ' \
                    + f'probability:<br><i>Daily average > {t.legendgroup} μg/m³' \
                    + '<br></i>%{x}<extra></extra>',
                showlegend=False,
            )
    )
    return fig


def get_exceedance_plot() -> go.Figure:
    tbls = read_files()
    df = get_probability_df(tbls)
    return make_plot(df)


if __name__ == "__main__":
    fig = get_exceedance_plot()
