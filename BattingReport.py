import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.axes import Axes
import seaborn as sns
import pybaseball as pyb
import requests
from Report import Report
from typing import Dict

class BattingReport(Report):

    def construct_batting_summary(self, batter_ids: Dict, start_date='2025-03-27', end_date='2025-10-01'):

        mlbam_batter_id = batter_ids["mlbam_id"] 
        fangraphs_batter_id = batter_ids["fangraphs_id"]

        df_player = pyb.statcast_batter(start_date, end_date, mlbam_batter_id)
        df_player = self.process_df(df_player)
        
        fig = plt.figure(figsize=(8.5, 11), dpi=300)


        gs = gridspec.GridSpec(7, 4,
                            height_ratios=[0.25,12,12,20,32,24,3],  # sum to 110
                            width_ratios=[0.25, 41.5, 41.5, 0.25], # sum to 85
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
        ax_bat_speed_dist = fig.add_subplot(gs[3, 1:2])
        ax_launch_angle_dist = fig.add_subplot(gs[3, 2:3])
        ax_pitch_table = fig.add_subplot(gs[4, 1:3])
        ax_monthly_xwoba = fig.add_subplot(gs[5, 1:3])

        # assign the axis values to their plots
        self.plot_header(mlbam_batter_id, ax_header)
        self.plot_stat_line(fangraphs_batter_id, 2025, ax_stat_line)
        self.plot_bat_speed_dist(df_player, mlbam_batter_id, ax_bat_speed_dist)
        self.plot_launch_angle_dist(df_player, mlbam_batter_id, ax_launch_angle_dist)
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

    def get_fangraphs_batting_stats(self, fangraphs_batter_id: int, season: int):
        # month = 13 is vs lhp
        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=bat&lg=all&season={season}&season1={season}&players={fangraphs_batter_id}&ind=0&qual=0&type=8&month=13&pageitems=500000"
        data = requests.get(url).json()
        df_left = pd.DataFrame(data=data['data'])
        df_left['Split'] = 'vs L'

        # month = 14 is vs rhp
        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=bat&lg=all&season={season}&season1={season}&players={fangraphs_batter_id}&ind=0&qual=0&type=8&month=14&pageitems=500000"
        data = requests.get(url).json()
        df_right = pd.DataFrame(data=data['data'])
        df_right['Split'] = 'vs R'

        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=bat&lg=all&season={season}&season1={season}&players={fangraphs_batter_id}&ind=0&qual=0&type=8&month=0&pageitems=500000"
        data = requests.get(url).json()
        df_all = pd.DataFrame(data=data['data'])
        df_all['Split'] = 'All'

        df_fangraphs_batter = pd.concat((df for df in [df_left, df_right, df_all] if not df.empty), axis=0)
        
        return df_fangraphs_batter

    def plot_stat_line(self, fangraphs_batter_id: int, season: int, ax: Axes):
        stats = ['Split', 'PA', 'AVG', 'OBP', 'SLG', 'OPS', 'K%', 'BB%', 'wRC+', 'HR']
        df_fangraphs_batter = self.get_fangraphs_batting_stats(fangraphs_batter_id, season = season)

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
        
        # apply color
        invert_colors = ['K%']
        for col_idx in range(len(format_specs)+1):
            header_cell = table_fg[0, col_idx]
            stat = stats[col_idx]
            if stat not in self.FANGRAPHS_BATTING_STATS.keys():
                continue
            x = df_fangraphs_batter[stat].iloc[2]
            mean = self.FANGRAPHS_BATTING_STATS[stat]['mean']
            std = self.FANGRAPHS_BATTING_STATS[stat]['std']
            z_score = (x - mean) / std
            value_cell = table_fg[3, col_idx]

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

    def plot_bat_speed_dist(self, df: pd.DataFrame, batter_id: int, ax: Axes):
        df_batter = df[(df['batter'] == batter_id) & (df['swing'] == True)]
        sns.kdeplot(data=df_batter['bat_speed'], bw_adjust=0.5, fill=True, ax=ax)

        mean_bat_speed = df_batter['bat_speed'].mean()
        ax.axvline(x=mean_bat_speed, color='r', linestyle='--', label=f'Mean: {mean_bat_speed:.2f}')

        ax.set_xlim(45, 90)
        
        ax.set_title("Bat Speed Distribution (mph)")
        ax.set(xlabel=None, ylabel=None, yticklabels=[])
        ax.legend(loc='upper left')

    def plot_launch_angle_dist(self, df: pd.DataFrame, batter_id: int, ax: Axes):
        df_batter = df[(df['batter'] == batter_id) & (df['swing'] == True)]

        sns.kdeplot(data=df_batter['launch_angle'], bw_adjust=0.5, fill=False, ax=ax)
        
        line = ax.lines[0]
        x = line.get_xdata()
        y = line.get_ydata()
        
        ax.fill_between(x, y, where=(x >= 8) & (x <= 32), color='red', alpha=0.5)
        ax.fill_between(x, y, where=(x < 8) | (x > 32), color='steelblue', alpha=0.5)

        ax.set_xlim(-90,90)

        ax.set_title("Launch Angle Distribution")
        ax.set(xlabel=None)
        ax.set(ylabel=None)
        ax.set(yticklabels=[])

    def get_pitch_groupings(self, df: pd.DataFrame):
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
        df_group['pitch_usage'] = df_group['pitch_count'] / total_pitches * 100 if total_pitches > 0 else np.nan

        df_group = df_group[df_group['pitch_usage'] >= 3]
        
        # Other rate calculations with safe division
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

        # Sort and reset index before formatting
        df_group = df_group.sort_values(by='pitch_usage', ascending=False)
        df_group = df_group.reset_index()
        
        # Create a formatted version if needed
        df_formatted = df_group.copy()
        
        for col, fmt in format_specs.items():
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: '—' if pd.isna(x) else f"{x:{fmt}}")
        
        return df_formatted

    def plot_pitch_table(self, df: pd.DataFrame, ax: Axes):
        df = self.get_pitch_groupings(df)

        # df = df[df['pitch_usage'] > 5]
        
        column_mapping = {
            'pitch_type': 'PitchType',
            'pitch_usage': 'Usage',
            'zone_swing_rate': 'Z-Swing%',
            'zone_contact_rate': 'Z-Con%',
            # add o contact
            'chase_rate': 'Chase%',
            'whiff_rate': 'Whiff%',
            # add la sweet spot
            'hard_hit_rate': 'HardHit%',
            'exit_velo': 'AvgEV',
            'ev90': 'EV90',
            'xwoba': 'xwOBA'
        }

        display_df = df.copy()
        display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]
        display_df = display_df[[col for _, col in column_mapping.items() if col in display_df.columns]]

        colWidths = [1.5] + [1] * (len(display_df.columns) - 1)
        
        table_plot = ax.table(cellText=display_df.values,
                             colLabels=display_df.columns,
                             cellLoc='center', 
                             bbox=[0, 0, 1, 1],
                             colWidths=colWidths)
        
        # Add color to pitch type cells
        for idx, pitch in enumerate(df['pitch_type']):
            if pitch in self.PITCH_COLORS:
                table_plot[(idx+1, 0)].set_facecolor(self.PITCH_COLORS[pitch]['color'])
        
        # Format table
        table_plot.auto_set_font_size(True)
        table_plot.scale(1, 0.5)

        # apply color
        for col_idx in range(len(column_mapping)):
            header_cell = table_plot[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor(self.COL_HEADING_COLOR)
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')

        ax.axis('off')

    def plot_xwoba_by_month(self, df: pd.DataFrame, ax: Axes):
        df_monthly = df.groupby(pd.to_datetime(df['game_date']).dt.month)['estimated_woba_using_speedangle'].mean()
        
        sns.lineplot(data=df_monthly, ax=ax, marker='o', markersize=8, linewidth=2, color='steelblue')
        
        league_avg = 0.315
        ax.axhline(y=league_avg, color='gray', linestyle='--', linewidth=1, label='League Avg')
        
        x = df_monthly.index
        y = df_monthly.values
        
        for month, val in df_monthly.items():
            ax.annotate(f'{val:.3f}', (month, val), textcoords='offset points', 
                        xytext=(0, 8), ha='center', fontsize=8)
        
        month_names = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
        ax.set_xticks(range(4, 10))
        ax.set_xticklabels(month_names)
        
        ax.set_ylim(0, .6)
        ax.set_xlim(2.5, 9.5)
        ax.set_title("xwOBA by Month", fontweight='bold')
        ax.set(xlabel=None, ylabel=None, yticklabels=[])
        ax.legend(loc='upper right', fontsize=8)

