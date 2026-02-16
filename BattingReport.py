import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle, Polygon
from matplotlib.axes import Axes
import seaborn as sns
import pybaseball as pyb
import requests
from scipy.interpolate import Rbf
from pybaseball.plotting import plot_stadium
from Report import Report
from typing import Dict

class BattingReport(Report):

    def construct_batting_summary(self, batter_ids: Dict, start_date='2025-03-27', end_date='2025-10-01', season: int = None):

        mlbam_batter_id = batter_ids["mlbam_id"]
        fangraphs_batter_id = batter_ids["fangraphs_id"]

        df_player = pyb.statcast_batter(start_date, end_date, mlbam_batter_id)
        df_player = self.process_df(df_player)

        is_season_mode = season is not None
        if season is None:
            season = int(start_date[:4])
        
        fig = plt.figure(figsize=(8.5, 11), dpi=300)


        stat_line_height = 12 if is_season_mode else 5
        remaining = 32 - stat_line_height + 12
        gs = gridspec.GridSpec(7, 4,
                            height_ratios=[0.25, 12, stat_line_height, 20, remaining, 20, 3],
                            width_ratios=[0.25, 41.5, 41.5, 0.25],
        )

        # create margins along the side
        ax_header = fig.add_subplot(gs[0, 1:3])
        ax_left = fig.add_subplot(gs[:, 0])
        ax_right = fig.add_subplot(gs[:, -1])
        ax_footer = fig.add_subplot(gs[-1, 1:3])

        # turn axis values off
        for ax in [ax_header, ax_left, ax_right, ax_footer]:
            ax.axis('off')
        
        ax_header = fig.add_subplot(gs[1, 1:3])
        ax_stat_line = fig.add_subplot(gs[2, 1:3])
        gs_row3 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[3, 1:3], wspace=0.3)
        ax_xwoba_vs_lhp = fig.add_subplot(gs_row3[0, 0])
        ax_batted_ball_grid = fig.add_subplot(gs_row3[0, 1])
        ax_xwoba_vs_rhp = fig.add_subplot(gs_row3[0, 2])
        ax_pitch_table = fig.add_subplot(gs[4, 1:3])
        ax_monthly_xwoba = fig.add_subplot(gs[5, 1:3])

        # assign the axis values to their plots
        if is_season_mode:
            self.plot_header(mlbam_batter_id, ax_header, report_type='batting', season=season)
        else:
            self.plot_header(mlbam_batter_id, ax_header, report_type='batting', start_date=start_date, end_date=end_date)
        if is_season_mode:
            self.plot_stat_line(fangraphs_batter_id, season, ax_stat_line)
        else:
            self.plot_stat_line(fangraphs_batter_id, season, ax_stat_line, start_date=start_date, end_date=end_date)
        bio = self.get_bio(mlbam_batter_id)
        _, team_abb = self.get_team_info(bio['team_link'])
        team_stadium = self.TEAM_ABB_TO_STADIUM.get(team_abb, 'generic')

        self.plot_xwoba_heatmap(df_player, ax_xwoba_vs_lhp, p_throws='L')
        self.plot_spray_chart(df_player, ax_batted_ball_grid, team_stadium)
        self.plot_xwoba_heatmap(df_player, ax_xwoba_vs_rhp, p_throws='R')
        self.plot_pitch_table(df_player, ax_pitch_table)
        self.plot_xwoba_by_month(df_player, ax_monthly_xwoba)

        # add footer text
        ax_footer.text(0.25, 0.5, 'Made by Anthony Ciardelli', ha='center', va='center', fontsize=10)
        ax_footer.text(0.75, 0.5, 'Data from MLB and Fangraphs', ha='center', va='center', fontsize=10)

        fig.tight_layout()

        return fig

    def process_df(self, df: pd.DataFrame):
        df = self.process_df_base(df)

        df['hard_hit'] = df['launch_speed'] >= 95
        df['batted_ball'] = (df['launch_speed'].notna())

        # map pitch category
        fastballs = ['FF', 'FA', 'SI', 'FC']
        breaking = ['SL', 'ST', 'SV', 'KC', 'CU', 'CS', 'EP']
        offspeed = ['CH', 'FS', 'SC', 'FO']
        
        pitch_map = {}
        for pitch in fastballs:
            pitch_map[pitch] = 'fastball'
        for pitch in breaking:
            pitch_map[pitch] = 'breaking'
        for pitch in offspeed:
            pitch_map[pitch] = 'offspeed'

        df['pitch_category'] = df['pitch_type'].map(pitch_map)

        return df

    def get_fangraphs_batting_stats(self, fangraphs_batter_id: int, season: int, start_date: str = None, end_date: str = None):
        if start_date and end_date:
            date_params = f"&month=1000&startdate={start_date}&enddate={end_date}"
        else:
            date_params = "&month=0"

        base_url = (f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=bat&lg=all"
                    f"&season={season}&season1={season}&players={fangraphs_batter_id}&ind=0&qual=0&type=8&pageitems=500000")

        if start_date and end_date:
            url_all = base_url + date_params
            data = requests.get(url_all).json()
            df_all = pd.DataFrame(data=data['data'])
            df_all['Split'] = 'All'
            df_left = pd.DataFrame()
            df_right = pd.DataFrame()
        else:
            # month = 13 is vs lhp
            url = base_url + "&month=13"
            data = requests.get(url).json()
            df_left = pd.DataFrame(data=data['data'])
            df_left['Split'] = 'vs L'

            # month = 14 is vs rhp
            url = base_url + "&month=14"
            data = requests.get(url).json()
            df_right = pd.DataFrame(data=data['data'])
            df_right['Split'] = 'vs R'

            url = base_url + "&month=0"
            data = requests.get(url).json()
            df_all = pd.DataFrame(data=data['data'])
            df_all['Split'] = 'All'

        df_fangraphs_batter = pd.concat((df for df in [df_left, df_right, df_all] if not df.empty), axis=0)
        
        return df_fangraphs_batter

    def plot_stat_line(self, fangraphs_batter_id: int, season: int, ax: Axes, start_date: str = None, end_date: str = None):
        stats = ['Split', 'PA', 'AVG', 'OBP', 'SLG', 'OPS', 'K%', 'BB%', 'wRC+', 'HR']
        df_fangraphs_batter = self.get_fangraphs_batting_stats(fangraphs_batter_id, season=season, start_date=start_date, end_date=end_date)

        df_fangraphs_batter['K%'] *= 100
        df_fangraphs_batter['BB%'] *= 100

        format_specs = {
            'PA' : '.0f',
            'AVG' : '.3f',
            'OBP' : '.3f',
            'SLG' : '.3f',
            'OPS' : '.3f',
            'K%' : '.1f',
            'BB%' : '.1f',
            'wRC+' : '.0f',
            'HR' : '.0f',
        }

        df_formatted = df_fangraphs_batter.copy()
        
        for col, fmt in format_specs.items():
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: '—' if pd.isna(x) else f"{x:{fmt}}")
                
        colWidths = [1] * (len(df_formatted.columns))

        table_fg = ax.table(cellText=df_formatted[stats].values, colLabels=stats, cellLoc='center',
                    bbox=[0.00, 0.0, 1, 1], colWidths=colWidths)
        
        # apply color to the combined row
        invert_colors = ['K%']
        num_rows = len(df_fangraphs_batter)
        all_row_idx = num_rows - 1  # "All" is always the last row in the dataframe
        for col_idx in range(len(format_specs)+1):
            header_cell = table_fg[0, col_idx]
            stat = stats[col_idx]
            if stat not in self.FANGRAPHS_BATTING_STATS.keys():
                continue
            x = df_fangraphs_batter[stat].iloc[all_row_idx]
            mean = self.FANGRAPHS_BATTING_STATS[stat]['mean']
            std = self.FANGRAPHS_BATTING_STATS[stat]['std']
            z_score = (x - mean) / std
            value_cell = table_fg[num_rows, col_idx]

            invert = False
            if stat in invert_colors:
                invert = True

            color = self.get_color(z_score, invert)
            value_cell.set_facecolor(color)

        for col_idx in range(len(format_specs)+1):
            header_cell = table_fg[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor(self.COL_HEADING_COLOR)
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')
        
        ax.axis('off')

    def plot_xwoba_heatmap(self, df: pd.DataFrame, ax: Axes, p_throws: str = 'R'):
        """Plots a Savant-style xwOBA heatmap with heart/shadow/chase zones"""
        zone_width = 17 / 12
        zone_left = -zone_width / 2
        zone_right = zone_width / 2
        zone_bot = 1.5
        zone_top = 3.5
        influence_buffer = 0.5

        df_hand = df[(df['p_throws'] == p_throws) & (df['estimated_woba_using_speedangle'].notna())].copy()

        if len(df_hand) < 15:
            ax.set_title(f"xwOBA vs {p_throws}HP", fontweight='bold', fontsize=9)
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center', transform=ax.transAxes, fontsize=8)
            ax.set_aspect('equal')
            ax.axis('off')
            return

        # Filter to pitches within influence distance of the zone
        mask = (
            (df_hand['plate_x'] >= zone_left - influence_buffer) &
            (df_hand['plate_x'] <= zone_right + influence_buffer) &
            (df_hand['plate_z'] >= zone_bot - influence_buffer) &
            (df_hand['plate_z'] <= zone_top + influence_buffer)
        )
        df_local = df_hand[mask]

        if len(df_local) < 15:
            ax.set_title(f"xwOBA vs {p_throws}HP", fontweight='bold', fontsize=9)
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center', transform=ax.transAxes, fontsize=8)
            ax.set_aspect('equal')
            ax.axis('off')
            return

        x = df_local['plate_x'].values
        z = df_local['plate_z'].values
        v = df_local['estimated_woba_using_speedangle'].values

        render_pad = 0.25
        grid_x, grid_z = np.mgrid[zone_left-render_pad:zone_right+render_pad:50j, zone_bot-render_pad:zone_top+render_pad:50j]

        rbf = Rbf(x, z, v, function='multiquadric', smooth=2)
        v_smooth = rbf(grid_x, grid_z)

        norm = mcolors.Normalize(vmin=0.150, vmax=0.450)
        levels = np.linspace(0.150, 0.450, 20)

        cntr = ax.contourf(grid_x, grid_z, v_smooth, levels=levels,
                           cmap=self._CUSTOM_CMAP, norm=norm, extend='both', alpha=0.8)

        for c in cntr.collections:
            c.set_edgecolor("face")

        zone = Rectangle((zone_left, zone_bot), zone_width, zone_top - zone_bot,
                          fill=False, edgecolor='black', linewidth=2, zorder=10)
        ax.add_patch(zone)

        plate_width = zone_width
        home_plate = Polygon([
            (-plate_width/2 + 0.2, 0.5),
            (plate_width/2 - 0.2, 0.5),
            (plate_width/2, 0),
            (0, -0.3),
            (-plate_width/2, 0.0)
        ], closed=True, fill=False, edgecolor='black', linewidth=2, zorder=10)
        ax.add_patch(home_plate)

        ax.set_xlim(zone_left - render_pad - 0.05, zone_right + render_pad + 0.05)
        ax.set_ylim(-0.5, zone_top + render_pad + 0.05)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"xwOBA vs {p_throws}HP", fontweight='bold', fontsize=9)

    def plot_spray_chart(self, df: pd.DataFrame, ax: Axes, team_stadium: str = 'generic'):
        """Plots a spray chart of hits (1B, 2B, 3B, HR) on the player's home stadium"""
        hit_events = {
            'single': '1B',
            'double': '2B',
            'triple': '3B',
            'home_run': 'HR',
        }
        hit_colors = {
            '1B': '#FE6100',
            '2B': '#785EF0',
            '3B': '#FFB000',
            'HR': '#DC267F',
        }

        df_hits = df[df['events'].isin(hit_events.keys()) & df['hc_x'].notna() & df['hc_y'].notna()].copy()
        df_hits['hit_type'] = df_hits['events'].map(hit_events)

        if len(df_hits) == 0:
            ax.axis('off')
            ax.text(0.5, 0.5, 'Not enough data', ha='center', va='center', transform=ax.transAxes, fontsize=8)
            return

        plot_stadium(team_stadium, title='', axis=ax)

        draw_order = ['1B', '2B', '3B', 'HR']
        for hit_type in draw_order:
            subset = df_hits[df_hits['hit_type'] == hit_type]
            if len(subset) > 0:
                ax.scatter(subset['hc_x'], subset['hc_y'].mul(-1),
                           s=25, c=hit_colors[hit_type], label=hit_type,
                           alpha=1.0, edgecolors='black', linewidths=0.3, zorder=5)

        ax.set_xlim(0, 250)
        ax.set_ylim(-250, 0)
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title('')
        ax.legend(loc='lower left', fontsize=6, framealpha=0.8, markerscale=1.5)

    def get_pitch_groupings(self, df: pd.DataFrame):
        EXPLICIT_PITCHES = ['FF', 'SI', 'FC', 'SL', 'ST', 'CU', 'CH', 'FS']

        df_group = df.groupby(['pitch_type']).agg(
            pitch_count = ('pitch_type', 'count'),
            whiff = ('whiff', 'sum'),
            zone_whiff = ('zone_whiff', 'sum'),
            swing = ('swing', 'sum'),
            zone_swing = ('zone_swing', 'sum'),
            in_zone = ('in_zone', 'sum'),
            out_zone = ('out_zone', 'sum'),
            chase = ('chase', 'sum'),
            exit_velo = ('launch_speed', 'mean'),
            ev90 = ('launch_speed', lambda x: x.quantile(0.9)),
            xwoba = ('estimated_woba_using_speedangle', 'mean'),
            hard_hit = ('hard_hit', 'sum'),
            batted_ball = ('batted_ball', 'sum')
        )

        total_pitches = df_group['pitch_count'].sum()

        # only want certain pitches
        df_group = df_group.reset_index()
        df_group = df_group[df_group['pitch_type'].isin(EXPLICIT_PITCHES)]
        df_group = df_group[df_group['pitch_count'] > 0]

        df_group['pitch_usage'] = df_group['pitch_count'] / total_pitches * 100 if total_pitches > 0 else np.nan

        # rate calculations with safe division
        df_group['whiff_rate'] = df_group.apply(lambda x: (x['whiff'] / x['swing'] * 100) if x['swing'] > 0 else np.nan, axis=1)
        df_group['contact_rate'] = 100 - df_group['whiff_rate']
        df_group['zone_swing_rate'] = df_group.apply(lambda x: (x['zone_swing'] / x['pitch_count'] * 100) if x['pitch_count'] > 0 else np.nan, axis=1)
        df_group['chase_rate'] = df_group.apply(lambda x: (x['chase'] / x['out_zone'] * 100) if x['out_zone'] > 0 else np.nan, axis=1)
        df_group['zone_whiff_rate'] = df_group.apply(lambda x: (x['zone_whiff'] / x['zone_swing'] * 100) if x['zone_swing'] > 0 else np.nan, axis=1)
        df_group['zone_contact_rate'] = 100 - df_group['zone_whiff_rate']
        df_group['SEAGER'] = df_group['zone_swing_rate'] - df_group['chase_rate']

        df_group['hard_hit_rate'] = df_group.apply(lambda x: (x['hard_hit'] / x['batted_ball'] * 100) if (x['batted_ball'] > 0) else np.nan, axis=1)

        format_specs = {
            'pitch_count': '.0f',
            'pitch_usage': '.1f',
            'zone_swing_rate': '.1f',
            'zone_contact_rate': '.1f',
            'zone_whiff_rate': '.1f',
            'chase_rate': '.1f',
            'whiff_rate': '.1f',
            'SEAGER': '.1f',
            'exit_velo': '.1f',
            'ev90': '.1f',
            'hard_hit_rate': '.1f',
            'xwoba': '.3f'
        }

        # sort by descending usage
        df_group = df_group.sort_values(by='pitch_usage', ascending=False).reset_index(drop=True)

        df_formatted = df_group.copy()

        for col, fmt in format_specs.items():
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: '—' if pd.isna(x) else f"{x:{fmt}}")

        return df_formatted

    def plot_pitch_table(self, df: pd.DataFrame, ax: Axes):
        df = self.get_pitch_groupings(df)

        column_mapping = {
            'pitch_type': 'Pitch',
            'pitch_usage': 'Usage',
            'zone_swing_rate': 'Z-Sw%',
            'zone_contact_rate': 'Z-Con%',
            # add o contact
            'chase_rate': 'Chase%',
            'whiff_rate': 'Whiff%',
            # add la sweet spot
            'hard_hit_rate': 'HH%',
            'exit_velo': 'AvgEV',
            'ev90': 'EV90',
            'xwoba': 'xwOBA'
        }

        display_df = df.copy()
        display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]
        display_df = display_df[[col for _, col in column_mapping.items() if col in display_df.columns]]

        table_plot = ax.table(cellText=display_df.values,
                             colLabels=display_df.columns,
                             cellLoc='center', 
                             bbox=[0, 0, 1, 1])
        
        # add colors to pitch type cells
        for idx, pitch in enumerate(df['pitch_type']):
            if pitch in self.PITCH_COLORS:
                table_plot[(idx+1, 0)].set_facecolor(self.PITCH_COLORS[pitch]['color'])
        
        table_plot.auto_set_font_size(True)

        # apply color
        for col_idx in range(len(column_mapping)):
            header_cell = table_plot[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor(self.COL_HEADING_COLOR)
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')

        ax.axis('off')

    def plot_xwoba_by_month(self, df: pd.DataFrame, ax: Axes):
        ROLLING_WINDOW = 50

        df_pa = df[df['estimated_woba_using_speedangle'].notna()].copy()
        df_pa = df_pa.sort_values('game_date').reset_index(drop=True)

        if len(df_pa) < ROLLING_WINDOW:
            ax.set_title(f"Rolling xwOBA ({ROLLING_WINDOW} PA)", fontweight='bold')
            ax.text(0.5, 0.5, 'Not enough PAs', ha='center', va='center', transform=ax.transAxes)
            return

        df_pa['rolling_xwoba'] = df_pa['estimated_woba_using_speedangle'].rolling(window=ROLLING_WINDOW, min_periods=ROLLING_WINDOW).mean()
        df_pa = df_pa.dropna(subset=['rolling_xwoba']).reset_index(drop=True)

        x = range(ROLLING_WINDOW, ROLLING_WINDOW + len(df_pa))
        ax.plot(x, df_pa['rolling_xwoba'], linewidth=2, color='steelblue')
        ax.fill_between(x, df_pa['rolling_xwoba'], alpha=0.15, color='steelblue')

        ax.axhline(y=0.250, color='#d9534f', linestyle='--', linewidth=2, alpha=0.6, label='Poor (.250)')
        ax.axhline(y=0.315, color='gray', linestyle='--', linewidth=2, alpha=0.6, label='Lg Avg (.315)')
        ax.axhline(y=0.400, color='#5cb85c', linestyle='--', linewidth=2, alpha=0.6, label='Great (.400)')

        ax.set_ylim(0, 0.6)
        ax.set_xlim(ROLLING_WINDOW, ROLLING_WINDOW + len(df_pa) - 1)
        ax.set_title(f"Rolling xwOBA ({ROLLING_WINDOW} PA)", fontweight='bold')
        ax.set(xlabel=None, ylabel=None, yticklabels=[])
        ax.legend(loc='upper right', fontsize=7)

