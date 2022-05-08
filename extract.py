from __future__ import annotations
import pandas as pd
import xarray as xr
import pull

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Iterator


class Process(Enum):
    QUANTILE = "quantile"
    POINTS = "points"


@dataclass()
class Area:
    name : str|dict = 'Cyprus'
    lat : slice|xr.DataArray|float = slice(35.7, 34.2)
    lon : slice|xr.DataArray|float = slice(32.2, 34.7)
    lev : int = 0
    method : None|str = field(init=False)
    process : Process = Process.QUANTILE
    data : pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.method = None if isinstance(self.lat, slice) else 'nearest'

    @staticmethod
    def combine(*args: Area) -> Area:
        all = pd.DataFrame(
            [{'name': x.name, 'lon': x.lon, 'lat': x.lat} for x in args]
        )
        return Area(
            name=all.name.to_dict(),
            lat=xr.DataArray(all.lat.to_list(), dims=Process.POINTS.value),
            lon=xr.DataArray(all.lon.to_list(), dims=Process.POINTS.value),
            process=Process.POINTS
        )


def read_data(nc_file: Path) -> xr.Dataset:
    return xr.open_dataset(nc_file)


def file_complete(nc_file: Path, time_len: int = 97) -> bool:
    return read_data(nc_file).dropna("time", how="any").time.size == time_len if nc_file.exists() else False


def rename_vars(nc: xr.Dataset) -> xr.Dataset:
    return nc.rename_vars({var: nc[var].species for var in list(nc.data_vars)})


def data_selection(data: xr.Dataset, slices: Area) -> xr.Dataset:
    return data.sel(
        latitude=slices.lat,
        longitude=slices.lon,
        level=slices.lev,
        method=slices.method,  # type: ignore # xr.dataset.sel issue
    )


def get_quantiles(data: xr.Dataset) -> pd.DataFrame:
    return data.quantile(
        [0, 0.25, 0.5, 0.75, 1],
        dim=["longitude", "latitude"]
    ).to_dataframe().reset_index()


def get_summary(data: xr.Dataset, points_name: str|dict) -> pd.DataFrame:
    return (
        data.to_dataframe()
            .reset_index()
            .replace({"points": points_name})
        .drop(columns=["longitude", "latitude", "level"])  # type: ignore
    )


def format_date(data: pd.DataFrame, ref_date: date, pivot_on: str) -> pd.DataFrame:
    def fix_tz(timeseries: pd.Series) -> pd.DatetimeIndex:
        return pd.DatetimeIndex(
            pd.to_datetime(timeseries, utc=True)
        ).tz_convert("Asia/Nicosia")

    data.time = fix_tz(data.time + datetime.combine(ref_date, datetime.min.time()))
    return data.pivot(index="time", columns=pivot_on)


def pipeline(data: xr.Dataset, slices: Area, date: date) -> pd.DataFrame:
    data = data_selection(data, slices)
    match slices.process:
        case Process.QUANTILE:
            df = get_quantiles(data)
        case Process.POINTS:
            df = get_summary(data, points_name=slices.name)
    return format_date(df, date, pivot_on=slices.process.value)


def process_nc(
        file: Path,
        date: date,
        slices: list[Area] = [Area()],
    ) -> Iterator[Area]:

    data = read_data(file)
    data = rename_vars(data)

    for slice in slices:
        slice.data = pipeline(data, slice, date)
        yield slice


if __name__ == "__main__":
    # downloads = get_cds_forecast()
    downloads = pull.get_cds_forecast(pull.Period(date(2022, 4, 9), date(2022, 4, 9)))

    points = Area.combine(
        Area("LARTRA", lon=33.62750, lat=34.91666),
        Area("MARIND", lon=33.29920, lat=34.73722),
        Area("PARTRA", lon=33.97770, lat=35.04583),
        Area("NICTRA", lon=33.34777, lat=35.15194),
        Area("NICRES", lon=33.33166, lat=35.12694),
        Area("LIMTRA", lon=33.03555, lat=34.68611),
        Area("PAFTRA", lon=32.42194, lat=34.77527),
        Area("ZYGIND", lon=33.33753, lat=34.72944),
        Area("AYMBGR", lon=33.05777, lat=35.03805),
    )
    areas = [Area(), points]

    df = process_nc(**downloads, slices=areas)

