import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, Polygon, Ellipse, Circle
from matplotlib.axes import Axes
import seaborn as sns
import pybaseball as pyb
import requests
import config
from Report import Report
from typing import Dict

class PitchingReport(Report):

    def construct_pitching_summary(self, pitcher_ids: Dict, start_date='2025-03-27', end_date='2025-10-01'):
        """assembles the entire pitching summary"""

        mlbam_pitcher_id = pitcher_ids["mlbam_id"] 
        fangraphs_pitcher_id = pitcher_ids["fangraphs_id"]

        df_player = pyb.statcast_pitcher(start_date, end_date, mlbam_pitcher_id)
        df_player = self.process_df(df_player)

        fig = plt.figure(figsize=(self.REPORT_WIDTH, self.REPORT_HEIGHT), dpi=300)


        gs = gridspec.GridSpec(7, 4,
                            height_ratios=[0.25,12,5,31,32,24,3],
                            width_ratios=[0.25, 41.5, 41.5, 0.25]
                            )
        
        # create margins along the side
        ax_header = fig.add_subplot(gs[0, 1:3])
        ax_left = fig.add_subplot(gs[:, 0])
        ax_right = fig.add_subplot(gs[:, -1])
        ax_footer = fig.add_subplot(gs[-1, 1:3])

        for ax in [ax_header, ax_left, ax_right, ax_footer]:
            ax.axis('off')
        
        ax_header = fig.add_subplot(gs[1, 1:3])
        ax_stat_line = fig.add_subplot(gs[2, 1:3])
        ax_short_form = fig.add_subplot(gs[3, 1:2])
        ax_usage_pies = fig.add_subplot(gs[3, 2:3])
        ax_pitch_table = fig.add_subplot(gs[4, 1:3])
        ax_loc_left = fig.add_subplot(gs[5, 1:2])
        ax_loc_right = fig.add_subplot(gs[5, 2:3])

        # assign the axis values to their plots
        self.plot_header(mlbam_pitcher_id, ax_header)
        self.plot_stat_line(fangraphs_pitcher_id, 2025, ax_stat_line)
        self.plot_short_form(df_player, ax_short_form)
        self.plot_usage_pies(df_player, ax_usage_pies)
        self.plot_pitch_table(df_player, ax_pitch_table)
        self.plot_pitch_locations(df_player, ax_loc_left, 'L')
        self.plot_pitch_locations(df_player, ax_loc_right, 'R')

        # add footer text
        ax_footer.text(0.25, 0.5, 'Made by Anthony Ciardelli', ha='center', va='center', fontsize=10)
        ax_footer.text(0.75, 0.5, 'Data from MLB and Fangraphs', ha='center', va='center', fontsize=10)

        fig.tight_layout()

        return fig

    def process_df(self, df: pd.DataFrame):
        """Process the dataframe for pitching metrics"""
        df = self.process_df_base(df)

        df['count_state'] = np.where(
            df['strikes'] > df['balls'], 'Ahead',
            np.where(df['balls'] > df['strikes'], 'Behind', 'Even')
        )

        return df

    def get_fangraphs_pitching_stats(self, fangraphs_pitcher_id: int, season: int):
        """fetches fangraphs pitching stats and returns them as a df"""
        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&players={fangraphs_pitcher_id}&ind=0&qual=0&type=8&month=0&pageitems=500000"
        data = requests.get(url).json()
        df = pd.DataFrame(data=data['data'])
        return df

    def plot_stat_line(self, fangraphs_pitcher_id: int, season: int, ax: Axes):
        """plots the statline pulled from fangraphs for the given date range"""
        stats = ['IP', 'WHIP', 'ERA', 'FIP', 'K%', 'BB%', 'K-BB%']
        df_fangraphs_pitcher = self.get_fangraphs_pitching_stats(fangraphs_pitcher_id, season = season)

        df_fangraphs_pitcher['K%'] *= 100
        df_fangraphs_pitcher['BB%'] *= 100
        df_fangraphs_pitcher['K-BB%'] *= 100

        print(df_fangraphs_pitcher)

        format_specs = {
            'IP' : '.0f',
            'WHIP' : '.2f',
            'ERA' : '.2f',
            'FIP' : '.2f',
            'K%' : '.1f',
            'BB%' : '.1f',
            'K-BB%' : '.1f',
        }

        df_formatted = df_fangraphs_pitcher.copy()
        
        for col, fmt in format_specs.items():
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: '—' if pd.isna(x) else f"{x:{fmt}}")

        table_fg = ax.table(cellText=df_formatted[stats].values, colLabels=stats, cellLoc='center',
                        bbox=[0.00, 0.0, 1, 1])

        invert_colors = ['WHIP', 'ERA', 'FIP', 'BB%']
        for col_idx in range(len(format_specs)):
            header_cell = table_fg[0, col_idx]
            stat = stats[col_idx]
            if stat not in self.FANGRAPHS_PITCHING_STATS.keys():
                continue
            x = df_fangraphs_pitcher[stat].iloc[0]
            mean = self.FANGRAPHS_PITCHING_STATS[stat]['mean']
            std = self.FANGRAPHS_PITCHING_STATS[stat]['std']
            z_score = (x - mean) / std
            value_cell = table_fg[1, col_idx]

            invert = False
            if stat in invert_colors:
                invert = True

            color = self.get_color(z_score, invert)
            value_cell.set_facecolor(color)
        
        # apply color
        for col_idx in range(len(format_specs)):
            header_cell = table_fg[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor(self.COL_HEADING_COLOR)
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')
        
        ax.axis('off')

    def plot_short_form(self, df: pd.DataFrame, ax: Axes):
        """short form movement plot of the player's pitches'"""
        sns.set_style("whitegrid")

        handedness = df['p_throws'].iloc[0]
        df['pfx_x'] *= -1

        # get arm angles
        df_angles = df.groupby(['pitch_type']).agg(
            avg_x = ('release_pos_x', 'mean'),
            avg_y = ('release_pos_z', 'mean')
        )
        
        df_sorted = df.sort_values('game_date', ascending=True)

        sns.scatterplot(
            data=df_sorted,
            x='pfx_x',
            y='pfx_z',
            hue='pitch_type',
            palette={p: self.PITCH_COLORS[p]['color'] for p in df['pitch_type'].unique()},
            linewidth=0.1,
            ax=ax,
            s=10
        )

        for pitch in df['pitch_type'].unique():
            rel_x = df_angles.loc[pitch, 'avg_x']
            rel_y = df_angles.loc[pitch, 'avg_y']

            ax.plot([0, rel_x * -20], [0, rel_y * 20],color=self.PITCH_COLORS[pitch]['color'], 
                        linestyle='--', 
                        linewidth=2,
                        alpha=1,
                        zorder=3)
        
        # Set axis limits
        ax.set_xlim(-27.5, 27.5)
        ax.set_ylim(-27.5, 27.5)
        
        # Add horizontal and vertical lines
        ax.axhline(y=0, color='black', linestyle='--', zorder=1)
        ax.axvline(x=0, color='black', linestyle='--', zorder=1)
        
        # Set title and labels
        ax.set_title("Movement Plot")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="both", which="major")

        left_patch = Rectangle((-27.5, 22.5), 15, 5, fill=False, color='black', linewidth=1)
        right_patch = Rectangle((12.5, 22.5), 15, 5, fill=False, color='black', linewidth=1)

        if handedness == 'L':
            ax.text(-20, 25, "<- Arm Side", ha='center', va='center', fontsize=8, clip_on=True)
            ax.text(20, 25, "Glove Side ->", ha='center', va='center', fontsize=8, clip_on=True)
        else:
            ax.text(-20, 25, "<- Glove Side", ha='center', va='center', fontsize=8, clip_on=True)
            ax.text(20, 25, "Arm Side ->", ha='center', va='center', fontsize=8, clip_on=True)

        
        ax.add_patch(left_patch)
        ax.add_patch(right_patch)

        ax.get_legend().remove()
        
        ax.grid(True, alpha=0.3)

    def find_usages(self, df):
        """finds usage rates based on the count_state being ahead, even, or behind"""
        df_usages = df.groupby(['pitch_type', 'stand', 'count_state']).agg(
           pitch_ct = ('pitch_type', 'count')
        ).reset_index()
        
        df_usages['usage_pct'] = df_usages.groupby(['stand', 'count_state'])['pitch_ct'].transform(
            lambda x: x / x.sum() * 100
        )
        
        # Round the percentage to 1 decimal place
        df_usages['usage_pct'] = df_usages['usage_pct'].round(1)
        
        return df_usages
        
    def plot_usage_pies(self, df: pd.DataFrame, ax: Axes, fontsize=10):
        """plots usage rates for behind, even, and head against lhb and rbh"""    
        df_usages = self.find_usages(df)
        
        gs = gridspec.GridSpecFromSubplotSpec(2, 3, subplot_spec=ax.get_subplotspec(), 
                                             wspace=0.4, hspace=0.6)
        
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        sub_axes = [plt.subplot(gs[pos]) for pos in positions]
        
        conditions_and_titles = [
            ((df_usages['stand'] == 'L') & (df_usages['count_state'] == 'Behind'), "Vs Left\nBehind"),
            ((df_usages['stand'] == 'L') & (df_usages['count_state'] == 'Even'), "Vs Left\nEven"),
            ((df_usages['stand'] == 'L') & (df_usages['count_state'] == 'Ahead'), "Vs Left\nAhead"),
            ((df_usages['stand'] == 'R') & (df_usages['count_state'] == 'Behind'), "Vs Right\nBehind"),
            ((df_usages['stand'] == 'R') & (df_usages['count_state'] == 'Even'), "Vs Right\nEven"),
            ((df_usages['stand'] == 'R') & (df_usages['count_state'] == 'Ahead'), "Vs Right\nAhead")
        ]
        
        for (condition, title), ax_sub in zip(conditions_and_titles, sub_axes):
            filtered_data = df_usages[condition]
            
            # Set the title for all positions, even empty ones
            ax_sub.set_title(title, fontsize=fontsize-2, pad=10)
            
            if not filtered_data.empty:
                data = pd.Series(
                    filtered_data['usage_pct'].values,
                    index=filtered_data['pitch_type'].values
                )
                
                colors = [self.PITCH_COLORS[pitch]['color'] for pitch in data.index]
            

                wedges, texts, autotexts = ax_sub.pie(
                    data.values,
                    colors=colors,
                    startangle=90,
                    wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'},
                    autopct='%1.1f%%',
                    textprops={'fontsize': fontsize-4},
                    pctdistance=0.7
                )
                
                # Apply fix_labels to the percentage labels (autotexts)
                if len(autotexts) > 1:  # Only fix if we have more than one label
                    self.fix_labels(autotexts, tooclose=0.5, sepfactor=1)
                
            else:
                ax_sub.set_frame_on(True)
                ax_sub.set_xticks([])
                ax_sub.set_yticks([])
                
            ax_sub.set_aspect('equal')

            plt.tight_layout()
        
        ax.axis('off')

    def get_pitch_groupings(self, df: pd.DataFrame):
        """gets metrics based the specific pitch to see how well that pitch plays"""
        df_group = df.groupby(['pitch_type']).agg(
            pitch_count = ('pitch_type', 'count'),
            rel_speed = ('release_speed', 'mean'),
            ivb = ('pfx_z', 'mean'),
            hb = ('pfx_x', 'mean'),
            spin_rate = ('release_spin_rate', 'mean'),
            rel_side = ('release_pos_x', 'mean'),
            rel_height = ('release_pos_z', 'mean'),
            extension = ('release_extension', 'mean'),
            whiff = ('whiff', 'sum'),
            zone_whiff = ('zone_whiff', 'sum'),
            swing = ('swing', 'sum'),
            zone_swing = ('zone_swing', 'sum'),
            in_zone = ('in_zone', 'sum'),
            out_zone = ('out_zone', 'sum'),
            chase = ('chase', 'sum'),
            xwoba = ('estimated_woba_using_speedangle', 'mean')
        ).reset_index()

        total_pitches = df_group['pitch_count'].sum()
        df_group['pitch_usage'] = df_group['pitch_count'] / total_pitches * 100 if total_pitches > 0 else np.nan
        
        # Other rate calculations with safe division
        df_group['whiff_rate'] = df_group.apply(lambda x: (x['whiff'] / x['swing'] * 100) if x['swing'] > 0 else np.nan, axis=1)
        df_group['zone_rate'] = df_group.apply(lambda x: (x['in_zone'] / x['pitch_count'] * 100) if x['pitch_count'] > 0 else np.nan, axis=1)
        df_group['chase_rate'] = df_group.apply(lambda x: (x['chase'] / x['out_zone'] * 100) if x['out_zone'] > 0 else np.nan, axis=1)
        df_group['zone_whiff_rate'] = df_group.apply(lambda x: (x['zone_whiff'] / x['zone_swing'] * 100) if x['zone_swing'] > 0 else np.nan, axis=1)

        format_specs = {
            'pitch_count': '.0f', 
            'pitch_usage': '.1f',
            'rel_speed': '.1f',
            'ivb': '.1f',
            'hb': '.1f',
            'spin_rate': '.0f',
            'rel_side': '.1f',
            'rel_height': '.1f',
            'extension': '.1f',
            'zone_rate': '.1f',
            'chase_rate': '.1f',
            'whiff_rate': '.1f',
            'zone_whiff_rate': '.1f',
            'xwoba': '.3f'
        }

        # Sort and reset index before formatting
        df_group = df_group.sort_values(by='pitch_usage', ascending=False)
        
        # Create a formatted version if needed
        df_formatted = df_group.copy()
        
        for col, fmt in format_specs.items():
            if col in df_formatted.columns:
                df_formatted[col] = df_formatted[col].apply(
                    lambda x: '—' if pd.isna(x) else f"{x:{fmt}}")
        
        return df_formatted

    def plot_pitch_table(self, df: pd.DataFrame, ax: Axes):
        """plots a table of every unique pitch the player threw and how well it did compared to average"""
        df = self.get_pitch_groupings(df)

        column_mapping = {
            'pitch_type': 'PitchType',
            'pitch_count': 'Count',
            'pitch_usage': 'Usage',
            'rel_speed': 'Velo',
            'ivb': 'IVB',
            'hb': 'HB',
            'spin_rate': 'Spin',
            # 'rel_side': 'Rel_X',
            # 'rel_height': 'Rel_Y',
            'extension': 'Ext',
            'zone_rate': 'Zone%',
            'chase_rate': 'Chase%',
            'whiff_rate': 'Whiff%',
            'zone_whiff_rate': 'Z-Whiff%',
            'xwoba': 'xwOBA'
        }

        display_df = df[[col for col in column_mapping.keys() if col in df.columns]].copy()
        display_df.columns = [column_mapping[col] for col in display_df.columns]
        print(display_df)
        
        colWidths = [1.5] + [1] * (len(display_df.columns) - 1)
        rowHeights = [0.75] + [1] * (len(display_df))

        table_plot = ax.table(cellText=display_df.values,
                             colLabels=display_df.columns,
                             cellLoc='center', 
                             bbox=[0, 0, 1, 1],
                             colWidths=colWidths)

        for i in range(len(display_df) + 1):
            for j in range(len(display_df.columns)):
                table_plot[i, j].set_height(rowHeights[i])
        
        # Add color to pitch type cells
        for idx, pitch in enumerate(df['pitch_type']):
            if pitch in self.PITCH_COLORS:
                table_plot[(idx+1, 0)].set_facecolor(self.PITCH_COLORS[pitch]['color'])
        
        # Format table
        table_plot.auto_set_font_size(False)
        table_plot.set_fontsize(8)
        table_plot.scale(1, 0.5)

        index_maps = {
            "velo": 3,
            "spin_rate": 6,
            "extension": 7,
            "zone_pct": 8,
            "chase_pct": 9,
            "whiff_pct": 10,
            "zone_whiff_pct": 11,
            "xwoba": 12
        }

        for row_idx in range(len(df['pitch_type'].unique())):
            # Get pitch type
            pitch_type_cell = table_plot[row_idx + 1, 0]
            pitch_type = pitch_type_cell.get_text().get_text()

            for metric, index in index_maps.items():
                metric_cell = table_plot[row_idx + 1, index]
                metric_value = metric_cell.get_text().get_text()
                metric_float = float(metric_value) if metric_value != '—' else np.nan

                if metric_float != np.nan:
                    metric_mean = config.pitch_type_stats[(metric, 'mean')][pitch_type]
                    metric_std = config.pitch_type_stats[(metric, 'std')][pitch_type] 
                    metric_z_score = (metric_float - metric_mean) / metric_std
                    if metric == 'xwoba':
                        metric_color = self.get_color(metric_z_score, invert=True)
                    else:
                        metric_color = self.get_color(metric_z_score)
                    metric_cell.set_facecolor(metric_color)

        # apply color
        for col_idx in range(len(column_mapping)):
            header_cell = table_plot[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor(self.COL_HEADING_COLOR)
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')
        
        # Remove axis
        ax.axis('off')

    def plot_pitch_locations(self, df: pd.DataFrame, ax: Axes, batter_hand='R'):
        """Plot pitch location zones with size-scaled circles for usage"""
        sns.set_style("white")
        
        plot_df = df[df['stand'] == batter_hand]
        pitch_types = plot_df['pitch_type'].unique()
        total_pitches = len(plot_df)
        
        for pitch in pitch_types:
            pitch_data = plot_df[plot_df['pitch_type'] == pitch]
            
            if len(pitch_data) < 5:
                continue
            
            # Calculate center (median location)
            center_x = pitch_data['plate_x'].median()
            center_z = pitch_data['plate_z'].median()
            
            # Calculate spread (IQR or std for the "zone" size)
            std_x = pitch_data['plate_x'].std()
            std_z = pitch_data['plate_z'].std()
            
            # Draw ellipse showing pitch location spread (1 std dev)
            ellipse = Ellipse(
                (center_x, center_z),
                width=std_x * 2,  # 1 std on each side
                height=std_z * 2,
                fill=False,
                edgecolor=self.PITCH_COLORS[pitch]['color'],
                linewidth=2,
                alpha=0.8,
                zorder=5
            )
            ax.add_patch(ellipse)
            
            # Calculate usage percentage for circle size
            usage = len(pitch_data) / total_pitches
            
            # Scale circle radius based on usage (adjust multiplier as needed)
            min_radius = 0.1
            max_radius = 0.4
            radius = min_radius + (max_radius - min_radius) * (usage / 0.5)  # Assumes max ~50% usage
            radius = min(radius, max_radius)  # Cap it
            
            # Draw filled circle showing usage
            circle = Circle(
                (center_x, center_z),
                radius=radius,
                facecolor=self.PITCH_COLORS[pitch]['color'],
                edgecolor='black',
                linewidth=1,
                alpha=0.7,
                zorder=6
            )
            ax.add_patch(circle)
            
        self.add_zone_and_plate(ax)
        
        hand_label = 'RHB' if batter_hand == 'R' else 'LHB'
        ax.set_title(f'{total_pitches} Pitches vs {hand_label}', fontsize=10)

