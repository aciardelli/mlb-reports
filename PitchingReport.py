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
        url = f"https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&stats=pit&lg=all&season={season}&season1={season}&player={fangraphs_pitcher_id}&ind=0&qual=0&type=8&month=0&pageitems=500000"
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

        table_fg = ax.table(cellText=df_formatted.values, colLabels=stats, cellLoc='center',
                        bbox=[0.00, 0.0, 1, 1])

        invert_colors = ['WHIP', 'ERA', 'FIP', 'BB%']
        for col_idx in range(7):
            header_cell = table_fg[0, col_idx]
            stat = stats[col_idx]
            if stat not in self.FANGRAPHS_STATS.keys():
                continue
            x = df_fangraphs_pitcher[stat].iloc[0]
            mean = self.FANGRAPHS_STATS[stat]['mean']
            std = self.FANGRAPHS_STATS[stat]['std']
            z_score = (x - mean) / std
            value_cell = table_fg[1, col_idx]

            invert = False
            if stat in invert_colors:
                invert = True

            color = self.get_color(z_score, invert)
            value_cell.set_facecolor(color)
        
        # apply color
        for col_idx in range(7):
            header_cell = table_fg[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor("#1a1a2e")
            header_cell.get_text().set_color('#FFF')
            header_cell.set_edgecolor('none')
        
        ax.axis('off')

    def plot_short_form(self, df: pd.DataFrame, ax: Axes, fontsize=10):
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
        ax.set_title("Movement Plot", fontsize=fontsize)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="both", which="major", labelsize=fontsize-2)

        left_patch = Rectangle((-27.5, 22.5), 10, 5, fill=False, color='black', linewidth=1)
        right_patch = Rectangle((17.5, 22.5), 10, 5, fill=False, color='black', linewidth=1)

        if handedness == 'L':
            ax.text(-22.5, 25, "Arm Side", ha='center', va='center', fontsize=fontsize-2)
            ax.text(22.5, 25, "Glove Side", ha='center', va='center', fontsize=fontsize-2)
        else:
            ax.text(-22.5, 25, "Glove Side", ha='center', va='center', fontsize=fontsize-2)
            ax.text(22.5, 25, "Arm Side", ha='center', va='center', fontsize=fontsize-2)

        
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

    def add_zone_and_plate(self, ax):
        """adds the zone and home plate patches"""
        zone_width = 17 / 12
        zone_height = 24 / 12
        
        zone = Rectangle((-zone_width/2, 1.5), zone_width, zone_height, 
                             fill=False, color='black', linewidth=2, zorder=10)
        ax.add_patch(zone)
        
        plate_width = 17 / 12
        home_plate = Polygon([
            (-plate_width/2 + 0.2, 0.5),
            (plate_width/2 - 0.2, 0.5),
            (plate_width/2, 0),
            (0, -0.3),
            (-plate_width/2, 0.0)
        ], closed=True, fill=False, edgecolor='black', linewidth=2, zorder=10)
        ax.add_patch(home_plate)
        
        ax.set_xlim(-2, 2)
        ax.set_ylim(-0.5, 5)
        ax.set_aspect('equal')
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

    def plot_pitch_table(self, df, ax):
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

        display_df = df.copy()
        display_df.columns = [column_mapping.get(col, col) for col in display_df.columns]
        
        # Define the columns we want to display in order
        cols = [
            'PitchType',
            'Count',
            'Usage',
            'Velo',
            'IVB',
            'HB',
            'Spin',
            # 'Rel_X',
            # 'Rel_Y',
            'Ext',
            'Zone%',
            'Chase%',
            'Whiff%',
            'Z-Whiff%',
            'xwOBA'
        ]
        
        # Select only those columns in the right order
        display_df = display_df[[col for col in cols if col in display_df.columns]]
        
        # Calculate column widths
        colWidths = [1.5] + [1] * (len(display_df.columns) - 1)
        
        # Create the table
        table_plot = ax.table(cellText=display_df.values,
                             colLabels=display_df.columns,
                             cellLoc='center', 
                            #  bbox=[0, -0.1, 1, 1],
                             bbox=[0, 0, 1, 1],
                             colWidths=colWidths)
        
        # Add color to pitch type cells
        for idx, pitch in enumerate(df['pitch_type']):
            if pitch in self.PITCH_COLORS:
                table_plot[(idx+1, 0)].set_facecolor(self.PITCH_COLORS[pitch]['color'])
        
        # Format table
        table_plot.auto_set_font_size(True)
        table_plot.scale(1, 0.5)

        for row_idx in range(len(df['pitch_type'].unique())):
            # Get pitch type
            pitch_type_cell = table_plot[row_idx + 1, 0]
            pitch_type = pitch_type_cell.get_text().get_text()
            # velo (column 3)
            velo_mean = config.pitch_type_stats[('velo', 'mean')][pitch_type]
            velo_std = config.pitch_type_stats[('velo', 'std')][pitch_type]
            velo_cell = table_plot[row_idx + 1, 3]
            velo_value = velo_cell.get_text().get_text()
            velo_float = float(velo_value) if velo_value != '—' else np.nan
            velo_z_score = (velo_float - velo_mean) / velo_std
            velo_color = self.get_color(velo_z_score)
            velo_cell.set_facecolor(velo_color)
            # ext (column 7)
            ext_mean = config.pitch_type_stats[('extension', 'mean')][pitch_type]
            ext_std = config.pitch_type_stats[('extension', 'std')][pitch_type]
            ext_cell = table_plot[row_idx + 1, 7]
            ext_value = ext_cell.get_text().get_text()
            ext_float = float(ext_value) if ext_value != '—' else np.nan
            ext_z_score = (ext_float - ext_mean) / ext_std
            ext_color = self.get_color(ext_z_score)
            ext_cell.set_facecolor(ext_color)
            # spin (column 6)
            spin_mean = config.pitch_type_stats[('spin_rate', 'mean')][pitch_type]
            spin_std = config.pitch_type_stats[('spin_rate', 'std')][pitch_type]
            spin_cell = table_plot[row_idx + 1, 6]
            spin_value = spin_cell.get_text().get_text()
            spin_float = float(spin_value) if spin_value != '—' else np.nan
            spin_z_score = (spin_float - spin_mean) / spin_std
            spin_color = self.get_color(spin_z_score)
            spin_cell.set_facecolor(spin_color)
            # zone (column 8)
            zone_mean = config.pitch_type_stats[('zone_pct', 'mean')][pitch_type]
            zone_std = config.pitch_type_stats[('zone_pct', 'std')][pitch_type]
            zone_cell = table_plot[row_idx + 1, 8]
            zone_value = zone_cell.get_text().get_text()
            zone_float = float(zone_value) if zone_value != '—' else np.nan
            zone_z_score = (zone_float - zone_mean) / zone_std
            zone_color = self.get_color(zone_z_score)
            zone_cell.set_facecolor(zone_color)
            # chase (column 9)
            chase_mean = config.pitch_type_stats[('chase_pct', 'mean')][pitch_type]
            chase_std = config.pitch_type_stats[('chase_pct', 'std')][pitch_type]
            chase_cell = table_plot[row_idx + 1, 9]
            chase_value = chase_cell.get_text().get_text()
            chase_float = float(chase_value) if chase_value != '—' else np.nan
            chase_z_score = (chase_float - chase_mean) / chase_std
            chase_color = self.get_color(chase_z_score)
            chase_cell.set_facecolor(chase_color)
            # whiff (column 10)
            whiff_mean = config.pitch_type_stats[('whiff_pct', 'mean')][pitch_type]
            whiff_std = config.pitch_type_stats[('whiff_pct', 'std')][pitch_type]
            whiff_cell = table_plot[row_idx + 1, 10]
            whiff_value = whiff_cell.get_text().get_text()
            whiff_float = float(whiff_value) if whiff_value != '—' else np.nan
            whiff_z_score = (whiff_float - whiff_mean) / whiff_std
            whiff_color = self.get_color(whiff_z_score)
            whiff_cell.set_facecolor(whiff_color)
            # z whiff (column 11)
            zone_whiff_mean = config.pitch_type_stats[('zone_whiff_pct', 'mean')][pitch_type]
            zone_whiff_std = config.pitch_type_stats[('zone_whiff_pct', 'std')][pitch_type]
            zone_whiff_cell = table_plot[row_idx + 1, 11]
            zone_whiff_value = zone_whiff_cell.get_text().get_text()
            zone_whiff_float = float(zone_whiff_value) if zone_whiff_value != '—' else np.nan
            zone_whiff_z_score = (zone_whiff_float - zone_whiff_mean) / zone_whiff_std
            zone_whiff_color = self.get_color(zone_whiff_z_score)
            zone_whiff_cell.set_facecolor(zone_whiff_color)
            # xwoba (column 12)
            xwoba_mean = config.pitch_type_stats[('xwoba', 'mean')][pitch_type]
            xwoba_std = config.pitch_type_stats[('xwoba', 'std')][pitch_type]
            xwoba_cell = table_plot[row_idx + 1, 12]
            xwoba_value = xwoba_cell.get_text().get_text()
            xwoba_float = float(xwoba_value) if xwoba_value != '—' else np.nan
            xwoba_z_score = (xwoba_float - xwoba_mean) / xwoba_std
            xwoba_color = self.get_color(xwoba_z_score, invert=True)
            xwoba_cell.set_facecolor(xwoba_color)
        # apply color
        for col_idx in range(13):
            header_cell = table_plot[0, col_idx]
            header_cell.get_text().set_weight('bold')
            header_cell.set_facecolor("#1a1a2e")
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

    def construct_pitching_summary(self, pitcher_ids: Dict, start_date='2025-03-27', end_date='2025-10-01'):

        mlbam_pitcher_id = pitcher_ids["mlbam_id"] 
        fangraphs_pitcher_id = pitcher_ids["fangraphs_id"]

        """assembles the entire pitching summary"""
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
        
        ax_name = fig.add_subplot(gs[1, 1:3])
        ax_game_table = fig.add_subplot(gs[2, 1:3])
        ax_short_form = fig.add_subplot(gs[3, 1:2])
        ax_usages = fig.add_subplot(gs[3, 2:3])
        ax_pitch_table = fig.add_subplot(gs[4, 1:3])
        ax_loc_left = fig.add_subplot(gs[5, 1:2])
        ax_loc_right = fig.add_subplot(gs[5, 2:3])

        # assign the axis values to their plots
        self.plot_header(mlbam_pitcher_id, ax_name)
        self.plot_stat_line(fangraphs_pitcher_id, 2025, ax_game_table)
        self.plot_short_form(df_player, ax_short_form)
        self.plot_usage_pies(df_player, ax_usages)
        self.plot_pitch_table(df_player, ax_pitch_table)
        self.plot_pitch_locations(df_player, ax_loc_left, 'L')
        self.plot_pitch_locations(df_player, ax_loc_right, 'R')

        # add footer text
        ax_footer.text(0.25, 0.5, 'Made by Anthony Ciardelli', ha='center', va='center', fontsize=10)
        ax_footer.text(0.75, 0.5, 'Data from MLB and Fangraphs', ha='center', va='center', fontsize=10)

        fig.tight_layout()

        return fig
