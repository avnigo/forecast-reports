import grequests
import json
import requests

from datetime import date, timedelta
from itertools import cycle, product
from pathlib import Path
from pull import cleanup_downloads
from shutil import copyfileobj
from typing import Iterator


def get_probability_maps(
        root: str = "https://dust.aemet.es/daily_dashboard",
        api_path: str = "assets/geojsons/prob/sconc_dust",
        levels: list[int] = [50, 100, 200, 500],
        day: str = f'{date.today() - timedelta(days=1):%Y%m%d}',
        out_path: Path = Path(__file__).parent / "data/AEMET",
    ) -> Iterator[bool]:

    def write_geojson(rs: requests.Response, level: int) -> None:
        file = out_path / day / f'{Path(rs.url).stem}_{level}{Path(rs.url).suffix}'
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open('w') as f:
            f.write(rs.text)

    if any((out_path / day).glob("*.geojson")):
        return

    urls = [
        grequests.get(
            f"{root}/{api_path}/{level}/geojson/{day}/"
            f"{day_no}_{day}_SCONC_DUST.geojson"
        )
        for day_no, level in product(['00', '01'], levels)
    ]

    responses = grequests.map(urls)

    for rs, level in zip(responses, cycle(levels)):
        if rs.status_code == 200:
            write_geojson(rs, level)
            yield True
        else:
            yield False


def get_timeseries_plot(
        root: str = "https://dust.aemet.es/daily_dashboard",
        api_path: str = "_dash-update-component",
        template_request: Path = Path(__file__).parent.absolute() \
            / "data/ref/fig-template-payload.json",
        day: str = f'{date.today() - timedelta(days=1):%Y%m%d}',
        lat_lon: list[float] = [35.03581217039174, 33.21716308593751],
        out_path: Path = Path(__file__).parent / "data/AEMET",
    ) -> Path|str|None:

    def write_json(file: Path, payload: str) -> Path:
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("w") as f:
            f.write(json.dumps(payload))
        return file

    if (file := out_path / day / f"{day}_fig.json").exists():
        return file 

    with template_request.open('r') as f:
        payload = json.loads(f.read())

    payload["state"][1]["value"] = day
    payload["state"][3]["value"] = lat_lon

    response = requests.post(f"{root}/{api_path}", json=payload)

    if response.status_code == 200:
        fig_payload = (
            response
                .json()
                .get('response')
                .get('ts-modal')
                .get('children')
                .get('props')
                .get('children')
                .get('props')
                .get('figure')
        )
        file = write_json(file, fig_payload)
        return file


def get_map_gif(
        url: str = "https://dust.aemet.es/daily_dashboard/assets/comparison/median/sconc_dust",
        day: date = date.today() - timedelta(days=1),
        out_path: Path = Path(__file__).parent / "data/AEMET",
    ):

    day_str = f"{day:%Y%m%d}"
    api_path = f"{day.year}/{day:%m}/{day_str}_median_loop.gif"
    
    if (out_file := out_path / day_str / f"{day_str}_median.gif").exists():
        return out_file

    response = requests.get(f"{url}/{api_path}", stream=True)
    if response.status_code == 200:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file,'wb') as f:
            copyfileobj(response.raw, f)
        return out_file


def scrape() -> dict[str, Path|str|None]:
    fig_file = get_timeseries_plot()
    list(get_probability_maps())
    gif_file = get_map_gif()
    cleanup_downloads(Path(__file__).parent / "data/AEMET", dirmode=True)
    return {"fig": fig_file, "gif": gif_file}


if __name__ == "__main__":
    scrape()
