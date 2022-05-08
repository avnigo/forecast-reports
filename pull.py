import cdsapi
import yaml
import extract

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from shutil import rmtree


@dataclass
class Period:
    start_date: date = date.today()
    end_date: date = date.today()


@dataclass
class ForecastFile(Mapping):
    date: date
    file: Path

    def __getitem__(self, x):
        return self.__dict__[x]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


def load_credentials(yaml_file: Path = Path(__file__).parent / 'secrets.yaml') -> dict:
    with open(yaml_file, 'r') as f:
        return yaml.safe_load(f)


def load_client(credentials: dict) -> cdsapi.Client:
    return cdsapi.Client(
        url=credentials['url'],
        key=credentials['key'],
        verify=True
    )


def format_request(
        dates: Period,
        step: int = 1,
        hours: int = 97,
        variable: list[str] = [
            'dust',
            'particulate_matter_10um',
            'particulate_matter_2.5um',
            'nitrogen_dioxide',
            'nitrogen_monoxide',
            'ozone',
            'sulphur_dioxide',
        ],
        area: list[float|int] = [36.54, 30.24, 33.63, 36.43]
    ) -> dict:
    return {
        'model': 'ensemble',
        'format': 'netcdf',
        'type': 'forecast',
        'level': '0',
        'area': area,
        'time': '00:00',
        'leadtime_hour': [str(i) for i in range(0, hours, step)],
        'date': f'{dates.start_date}/{dates.end_date}',
        'variable': variable,
    }


def set_filename(out_dir: Path, dates: Period) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'CDS_{dates.start_date}.nc'
    if dates.start_date != dates.end_date:
        out_file = out_file.parent / f'{out_file.stem}_{dates.end_date}.zip'
    return out_file


def make_request(
        client: cdsapi.Client,
        dataset: str,
        request_obj: dict,
        out_file: Path,
        dry_run: bool = False,
        hours: int = 97,
    ) -> None:
    if not dry_run and not extract.file_complete(out_file, hours):
        client.retrieve(dataset, request_obj, out_file)


def get_latest_complete(dates: Period, out_file: Path, hours: int = 97) -> ForecastFile:
    def get_previous_available(dir_path: Path) -> ForecastFile:
         # Always gives previous available, even if considered incomplete
        return (
            ForecastFile(
                file=latest[-1],
                date=date.fromisoformat(latest[-1].stem.split("_")[1]),
            )
            if (latest := get_sorted_dir(dir_path)[:2]) else
            ForecastFile(file=out_file, date=dates.end_date)
        )
    return (
        ForecastFile(file=out_file, date=dates.end_date)
        if extract.file_complete(out_file, hours) else 
        get_previous_available(out_file.parent)
    )


def get_sorted_dir(dir_path: Path) -> list:
    return sorted(
        [f for f in dir_path.glob("*")],
        key=lambda item: item.stat().st_ctime,
        reverse=True
    )


def cleanup_downloads(path: Path, max_file_count: int = 5, dirmode=False) -> bool:
    sorted_files = get_sorted_dir(path)
    delete_files = set(sorted_files) - set(sorted_files[:max_file_count])

    return bool(len([rmtree(f) if dirmode else f.unlink(missing_ok=True) for f in delete_files]))


def get_cds_forecast(
        dates: Period = Period(),
        dataset: str = 'cams-europe-air-quality-forecasts',
        out_dir: Path = Path(__file__).parent / 'data' / 'CDS',
        hours: int = 97,
        **opts,
    ) -> ForecastFile:

    credentials = load_credentials()
    cds = load_client(credentials)
    request_obj = format_request(dates, hours=hours, **opts)
    out_file = set_filename(out_dir, dates)

    make_request(cds, dataset, request_obj, out_file, dry_run=False, hours=hours)
    latest_forecast = get_latest_complete(dates, out_file, hours)

    cleanup_downloads(out_dir)

    return latest_forecast


if __name__ == "__main__":
    # Forecast availability:
    # D0 (00-24h) 05:50 UTC guaranteed by 08:00 UTC
    # D1 (25-48h) 05:55 UTC guaranteed by 08:00 UTC
    # D2 (49-72h) 07:30 UTC guaranteed by 10:00 UTC
    # D3 (73-96h) 08:00 UTC guaranteed by 10:00 UTC
    data = get_cds_forecast()
