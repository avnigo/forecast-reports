import holoviews as hv
import pandas as pd
import xarray as xr
import hvplot.xarray

from cartopy import crs
from datetime import date, datetime
from pathlib import Path


def read_data(nc_file: Path):
    return xr.open_dataset(nc_file).sel(level=0)


def format_date(data: pd.DataFrame, ref_date: date) -> pd.DatetimeIndex:
    def fix_tz(timeseries: pd.Series) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(
            pd.to_datetime(timeseries, utc=True)
        ).tz_convert("Asia/Nicosia")
    data.time = fix_tz(data.time + datetime.combine(ref_date, datetime.min.time()))
    return data.time


def plot_map(file: Path, date: date, out_file: Path = Path(__file__).parent / "out") -> None:
    ds = read_data(file)
    ds["time"] = format_date(ds.time.to_dataframe(), date)
    hv.output(widget_location="bottom")
    hv.save(
        ds.hvplot(
            x="longitude",
            y="latitude",
            z="dust",
            clim=(0,200),
            crs=crs.PlateCarree(),
            coastline="10m",
            alpha=0.6,
            cmap="inferno",
            tiles="CartoLight",
        ).options(
            frame_width=900,
            frame_height=400,
            xlim=(1800000, 4250000),
            ylim=(4000000, 4100000),
            title="CAMS Dust Forecast",
            active_tools=["pan","wheel_zoom"],
        ),
        out_file / "dust-forecast-map.html"
    )

