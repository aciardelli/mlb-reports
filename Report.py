import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import matplotlib.colors as mcolors
from io import BytesIO
import requests
import config


class Report():
    MLB_TEAMS = config.mlb_teams
    PITCH_COLORS = config.pitch_colors
    FANGRAPHS_PITCHING_STATS = config.fangraphs_pitching_stats
    FANGRAPHS_BATTING_STATS = config.fangraphs_batting_stats

    REPORT_WIDTH = 8.5
    REPORT_HEIGHT = 11

    COL_HEADING_COLOR = '#1a1a2e'

    def process_df_base(self, df: pd.DataFrame):
        """clean the dataframe and setup new metrics for use"""
        swing_desc = ['foul_bunt','foul','hit_into_play','swinging_strike', 'foul_tip',
                    'swinging_strike_blocked','missed_bunt','bunt_foul_tip']
        whiff_desc = ['swinging_strike', 'foul_tip', 'swinging_strike_blocked']

        df['swing'] = (df['description'].isin(swing_desc))
        df['whiff'] = (df['description'].isin(whiff_desc))
        df['in_zone'] = (df['zone'] < 10)
        df['out_zone'] = (df['zone'] > 10)
        df['chase'] = (df.in_zone==False) & (df.swing == 1)
        df['zone_swing'] = (df['in_zone']) & (df['swing'])
        df['zone_whiff'] = (df['in_zone']) & (df['whiff'])

        # Convert the pitch type to a categorical variable
        df['pfx_z'] = df['pfx_z'] * 12
        df['pfx_x'] = df['pfx_x'] * 12
        return df[df['pitch_type'].notna() & (df['pitch_type'] != 'PO')]

    def get_headshot(self, mlbam_player_id: int):
        """gets player headshot from mlbstatic"""
        url = f'https://img.mlbstatic.com/mlb-photos/image/'\
              f'upload/d_people:generic:headshot:67:current.png'\
              f'/w_640,q_auto:best/v1/people/{mlbam_player_id}/headshot/silo/current.png'
        
        response = requests.get(url)
        
        img = Image.open(BytesIO(response.content))

        return img

    def get_bio(self, mlbam_player_id: int):
        """gets player information from mlb stats api"""
        url = f"https://statsapi.mlb.com/api/v1/people?personIds={mlbam_player_id}&hydrate=currentTeam"

        data = requests.get(url).json()

        player_name = data['people'][0]['fullName']
        pitcher_hand = data['people'][0]['pitchHand']['code']
        age = data['people'][0]['currentAge']
        height = data['people'][0]['height']
        weight = data['people'][0]['weight']
        team_link = data['people'][0]['currentTeam']['link']

        return {
            "player_name" : player_name,
            "pitcher_hand" : pitcher_hand,
            "age" : age,
            "height" : height,
            "weight" : weight,
            "team_link": team_link
        }

    def get_logo(self, team_link: str):
        """gets the logo image for the team the player plays for"""
        url_team = 'https://statsapi.mlb.com/' + team_link 
        data_team = requests.get(url_team).json()

        team_abb = data_team['teams'][0]['abbreviation']
        logo_url = self.MLB_TEAMS[team_abb] 
        response = requests.get(logo_url)

        img = Image.open(BytesIO(response.content))

        return img

    def plot_header(self, mlbam_player_id: int, ax: Axes):
        """constructs the header to be plotted"""
        bio = self.get_bio(mlbam_player_id)
        headshot = self.get_headshot(mlbam_player_id)
        logo = self.get_logo(bio['team_link'])

        ax.set_facecolor(self.COL_HEADING_COLOR)
        
        # set image configs
        img_width = 0.15
        img_height = 0.9
        margin = 0.02

        ax_headshot = ax.inset_axes([margin, 0.05, img_width, img_height])  # left 20% of ax
        ax_headshot.imshow(headshot)
        ax_headshot.axis('off')
        
        ax_logo = ax.inset_axes([1-img_width-margin, 0.05, img_width, img_height])  # right 20% of ax
        ax_logo.imshow(logo)
        ax_logo.axis('off')
        
        # player name - bold and white for contrast
        ax.text(0.5, 0.95, bio["player_name"],
                va='top', ha='center', fontsize=22, fontweight='bold',
                color='white', transform=ax.transAxes)

        # bio info - lighter color
        ax.text(0.5, 0.48, f'{bio["pitcher_hand"]}HP  •  Age {bio["age"]}  •  {bio["height"]}  •  {bio["weight"]} lbs',
                va='top', ha='center', fontsize=12,
                color='#b8b8b8', transform=ax.transAxes)

        # season label - accent color
        ax.text(0.5, 0.22, '2025 MLB Season',
                va='top', ha='center', fontsize=11, fontstyle='italic',
                color='#4fc3f7', transform=ax.transAxes)

        # accent line under the name
        ax.axhline(y=0.58, xmin=0.3, xmax=0.7, color='#4fc3f7', linewidth=2)
        
        rect = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                      facecolor=self.COL_HEADING_COLOR, zorder=-1)
        ax.add_patch(rect)
        ax.axis("off")

    def add_zone_and_plate(self, ax: Axes):
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

    def fix_labels(self, mylabels, tooclose=0.1, sepfactor=2):
        """helper function used to fix the labels in plot_usage_pies whenever they get too close and overlap"""
        vecs = np.zeros((len(mylabels), len(mylabels), 2))
        dists = np.zeros((len(mylabels), len(mylabels)))
        for i in range(0, len(mylabels)-1):
            for j in range(i+1, len(mylabels)):
                a = np.array(mylabels[i].get_position())
                b = np.array(mylabels[j].get_position())
                dists[i,j] = np.linalg.norm(a-b)
                vecs[i,j,:] = a-b
                if dists[i,j] < tooclose:
                    mylabels[i].set_x(a[0] + sepfactor*vecs[i,j,0])
                    mylabels[i].set_y(a[1] + sepfactor*vecs[i,j,1])
                    mylabels[j].set_x(b[0] - sepfactor*vecs[i,j,0])
                    mylabels[j].set_y(b[1] - sepfactor*vecs[i,j,1])

    def get_color(self, z_score: float, invert=False, vmin=-3, vmax=3, cmap='coolwarm'):
        """returns the color given the z score"""
        z = max(vmin, min(vmax, z_score))
        
        if invert:
            z = -z
        
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        
        colormap = plt.get_cmap(cmap)
        rgba = colormap(norm(z))
        
        return mcolors.to_hex(rgba)

