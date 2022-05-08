import scrape

from exceedance import get_exceedance_plot
from extract import Area, process_nc
from mapviz import plot_map
from pathlib import Path
from plot import load_json_fig, create_plots
from pull import get_cds_forecast
from reference import stations
from shutil import copy

PATH = Path(__file__).parent

def run_plot() -> None:
    def copy_gif_out(
        gif_path: Path,
        out_dir: Path = PATH / "out" / "dust_forecast.gif"
    ) -> None:
        out_dir.parent.mkdir(parents=True, exist_ok=True)
        copy(gif_path, out_dir)

    aemet_paths = scrape.scrape()
    copy_gif_out(aemet_paths["gif"])

    return create_plots(
        process_nc(**get_cds_forecast(), slices=[Area(), stations]),
        [load_json_fig(aemet_paths["fig"]), get_exceedance_plot()],
    )


def run_map() -> None:
    return plot_map(
        **get_cds_forecast(
            out_dir=PATH / "data" / "CDS-map",
            variable= ['dust'],
            area=[39.33, 9.02, 30, 45],
        )
    )


if __name__ == "__main__":
    run_plot()
    run_map()
