from extract import Area

stations = Area.combine(
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

quant_name = {0: 'min', 0.25: 'Q₁', 0.5: 'x̃', 0.75: 'Q₃', 1: 'max'}

species_name = {
    'Nitrogen Dioxide': 'NO₂',
    'Nitrogen Monoxide': 'NO',
    'Ozone': 'O₃',
    'Sulphur Dioxide': 'SO₂',
    'PM10 Aerosol': 'PM₁₀',
    'PM2.5 Aerosol': 'PM₂.₅',
}

fig_defaults = {
    'yaxis': {
        'showgrid': True,
        'gridwidth': 0.1,
        'gridcolor': "#f1f1f1",
        'zerolinecolor': 'black',
        'zerolinewidth': 0.5,
        'rangemode': 'normal',
    },
    'xaxis': {
        'showgrid': True,
        'gridwidth': 0.1,
        'gridcolor': "#f1f1f1",
    },
}
