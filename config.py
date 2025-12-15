mlb_teams = {
    "AZ": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/ari.png&h=500&w=500",
    "ATL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/atl.png&h=500&w=500",
    "BAL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bal.png&h=500&w=500",
    "BOS": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/bos.png&h=500&w=500",
    "CHC": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chc.png&h=500&w=500",
    "CWS": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/chw.png&h=500&w=500",
    "CIN": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cin.png&h=500&w=500",
    "CLE": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/cle.png&h=500&w=500",
    "COL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/col.png&h=500&w=500",
    "DET": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/det.png&h=500&w=500",
    "HOU": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/hou.png&h=500&w=500",
    "KC": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/kc.png&h=500&w=500",
    "LAA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/laa.png&h=500&w=500",
    "LAD": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/lad.png&h=500&w=500",
    "MIA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mia.png&h=500&w=500",
    "MIL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/mil.png&h=500&w=500",
    "MIN": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/min.png&h=500&w=500",
    "NYM": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nym.png&h=500&w=500",
    "NYY": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/nyy.png&h=500&w=500",
    "OAK": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/oak.png&h=500&w=500",
    "PHI": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/phi.png&h=500&w=500",
    "PIT": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/pit.png&h=500&w=500",
    "SD": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sd.png&h=500&w=500",
    "SF": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sf.png&h=500&w=500",
    "SEA": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/sea.png&h=500&w=500",
    "STL": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/stl.png&h=500&w=500",
    "TB": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tb.png&h=500&w=500",
    "TEX": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tex.png&h=500&w=500",
    "TOR": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/tor.png&h=500&w=500",
    "WSH": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/mlb/500/scoreboard/wsh.png&h=500&w=500"
}

pitch_colors = {
    ## Fastballs ##
    'FF': {'color': '#FF9999', 'name': 'Fastball'},
    'FA': {'color': '#FF9999', 'name': 'Fastball'},
    'SI': {'color': '#FFB366', 'name': 'Fastball'},
    'FC': {'color': '#FFDB4D', 'name': 'Fastball'},

    ## Offspeed ##
    'CH': {'color': '#FF99FF', 'name': 'Changeup'},
    'FS': {'color': '#FF8C66', 'name': 'Splitter'},
    'SC': {'color': '#F08223', 'name': 'Screwball'},
    'FO': {'color': '#FFB000', 'name': 'Forkball'},

    ## Sliders ##
    'SL': {'color': '#99FF99', 'name': 'Slider'},
    'ST': {'color': '#1BB999', 'name': 'Sweeper'},
    'SV': {'color': '#376748', 'name': 'Slurve'},

    ## Curveballs ##
    'KC': {'color': '#311D8B', 'name': 'Knuckle Curve'},
    'CU': {'color': '#66B2FF', 'name': 'Curveball'},
    'CS': {'color': '#274BFC', 'name': 'Slow Curve'},
    'EP': {'color': '#648FFF', 'name': 'Eephus'},

    ## Others ##
    'KN': {'color': '#867A08', 'name': 'Knuckleball'},
    'PO': {'color': '#472C30', 'name': 'Pitch Out'},
    'UN': {'color': '#9C8975', 'name': 'Unknown'},
}

fangraphs_stats = {
    'WHIP': {'mean': 1.24, 'std': 0.19}, 
    'ERA': {'mean': 3.85, 'std': 1.17}, 
    'FIP': {'mean': 3.95, 'std': 0.87}, 
    'K%': {'mean': 23.14, 'std': 5.26}, 
    'BB%': {'mean': 8.15, 'std': 2.25}, 
    'K-BB%': {'mean': 15.0, 'std': 5.56}
}


pitch_type_stats = {
    ('velo', 'mean'): {'CH': 86.03, 'CS': 72.56, 'CU': 79.86, 'FA': 62.57, 'FC': 89.68, 'FF': 94.47, 'FO': 82.51, 'FS': 86.66, 'KC': 82.55, 'SI': 93.84, 'SL': 86.24, 'ST': 82.25, 'SV': 81.7}, 
    ('velo', 'std'): {'CH': 3.28, 'CS': 2.02, 'CU': 3.23, 'FA': None, 'FC': 2.49, 'FF': 2.3, 'FO': None, 'FS': 3.13, 'KC': 3.73, 'SI': 2.56, 'SL': 2.61, 'ST': 2.7, 'SV': 2.23}, 
    ('extension', 'mean'): {'CH': 6.42, 'CS': 5.81, 'CU': 6.37, 'FA': 4.08, 'FC': 6.38, 'FF': 6.47, 'FO': 6.31, 'FS': 6.59, 'KC': 6.36, 'SI': 6.39, 'SL': 6.41, 'ST': 6.34, 'SV': 6.13}, 
    ('extension', 'std'): {'CH': 0.38, 'CS': 0.15, 'CU': 0.43, 'FA': None, 'FC': 0.36, 'FF': 0.41, 'FO': None, 'FS': 0.43, 'KC': 0.34, 'SI': 0.42, 'SL': 0.42, 'ST': 0.41, 'SV': 0.46}, 
    ('spin_rate', 'mean'): {'CH': 1782.44, 'CS': 2579.72, 'CU': 2593.17, 'FA': 1579.27, 'FC': 2402.06, 'FF': 2317.77, 'FO': 1192.62, 'FS': 1333.59, 'KC': 2526.0, 'SI': 2203.32, 'SL': 2434.5, 'ST': 2601.34, 'SV': 2559.97}, 
    ('spin_rate', 'std'): {'CH': 289.09, 'CS': 70.15, 'CU': 268.4, 'FA': None, 'FC': 176.06, 'FF': 140.65, 'FO': None, 'FS': 331.25, 'KC': 261.2, 'SI': 135.17, 'SL': 216.82, 'ST': 239.03, 'SV': 358.21}, 
    ('zone_pct', 'mean'): {'CH': 39.49, 'CS': 51.14, 'CU': 43.55, 'FA': 43.45, 'FC': 53.89, 'FF': 55.92, 'FO': 27.49, 'FS': 38.54, 'KC': 41.54, 'SI': 57.45, 'SL': 47.0, 'ST': 45.52, 'SV': 44.29}, 
    ('zone_pct', 'std'): {'CH': 8.2, 'CS': 2.1, 'CU': 7.78, 'FA': None, 'FC': 6.67, 'FF': 5.26, 'FO': None, 'FS': 8.13, 'KC': 7.2, 'SI': 6.01, 'SL': 6.73, 'ST': 6.47, 'SV': 4.39}, 
    ('chase_pct', 'mean'): {'CH': 19.79, 'CS': 9.49, 'CU': 15.98, 'FA': 14.88, 'FC': 12.4, 'FF': 10.19, 'FO': 33.21, 'FS': 21.0, 'KC': 18.84, 'SI': 10.76, 'SL': 16.5, 'ST': 16.39, 'SV': 15.98}, 
    ('chase_pct', 'std'): {'CH': 5.55, 'CS': 2.7, 'CU': 4.85, 'FA': None, 'FC': 3.91, 'FF': 2.66, 'FO': None, 'FS': 5.05, 'KC': 5.5, 'SI': 3.73, 'SL': 4.45, 'ST': 4.72, 'SV': 2.41}, 
    ('whiff_pct', 'mean'): {'CH': 15.25, 'CS': 9.93, 'CU': 12.83, 'FA': 5.36, 'FC': 11.02, 'FF': 10.47, 'FO': 22.69, 'FS': 17.54, 'KC': 15.08, 'SI': 6.32, 'SL': 15.82, 'ST': 14.31, 'SV': 12.89}, 
    ('whiff_pct', 'std'): {'CH': 5.3, 'CS': 3.32, 'CU': 4.36, 'FA': None, 'FC': 3.38, 'FF': 3.4, 'FO': None, 'FS': 5.16, 'KC': 4.87, 'SI': 2.64, 'SL': 4.75, 'ST': 4.39, 'SV': 3.33}, 
    ('zone_whiff_pct', 'mean'): {'CH': 6.33, 'CS': 7.24, 'CU': 4.01, 'FA': 2.38, 'FC': 6.06, 'FF': 6.95, 'FO': 3.14, 'FS': 6.6, 'KC': 3.87, 'SI': 3.59, 'SL': 6.2, 'ST': 5.38, 'SV': 4.41}, 
    ('zone_whiff_pct', 'std'): {'CH': 3.1, 'CS': 3.41, 'CU': 1.9, 'FA': None, 'FC': 1.92, 'FF': 2.57, 'FO': None, 'FS': 2.82, 'KC': 1.47, 'SI': 1.77, 'SL': 2.19, 'ST': 2.47, 'SV': 1.6}
}
