import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from PIL import Image, ImageFilter
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import matplotlib.colors as mcolors
from io import BytesIO
import requests
import config


class Report():
    MLB_TEAMS = config.mlb_teams
    MLB_TEAM_COLORS = config.mlb_team_colors
    PITCH_COLORS = config.pitch_colors
    FANGRAPHS_PITCHING_STATS = config.fangraphs_pitching_stats
    FANGRAPHS_BATTING_STATS = config.fangraphs_batting_stats
    TEAM_ABB_TO_STADIUM = config.team_abb_to_stadium

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
        bat_side = data['people'][0]['batSide']['code']
        age = data['people'][0]['currentAge']
        height = data['people'][0]['height']
        weight = data['people'][0]['weight']
        team_link = data['people'][0]['currentTeam']['link']

        return {
            "player_name" : player_name,
            "pitcher_hand" : pitcher_hand,
            "bat_side" : bat_side,
            "age" : age,
            "height" : height,
            "weight" : weight,
            "team_link": team_link
        }

    def get_team_info(self, team_link: str):
        """gets the logo image and team abbreviation for the team the player plays for"""
        url_team = 'https://statsapi.mlb.com/' + team_link
        data_team = requests.get(url_team).json()

        team_abb = data_team['teams'][0]['abbreviation']
        logo_url = self.MLB_TEAMS[team_abb]
        response = requests.get(logo_url)

        img = Image.open(BytesIO(response.content))

        return img, team_abb

    def plot_header(self, mlbam_player_id: int, ax: Axes, report_type: str = 'pitching', season: int = None, start_date: str = None, end_date: str = None):
        """constructs the header to be plotted"""
        bio = self.get_bio(mlbam_player_id)
        headshot = self.get_headshot(mlbam_player_id)
        logo, team_abb = self.get_team_info(bio['team_link'])

        team_colors = self.MLB_TEAM_COLORS.get(team_abb, {"primary": self.COL_HEADING_COLOR, "accent": "#4fc3f7"})
        primary_color = team_colors["primary"]
        accent_color = team_colors["accent"]

        ax.set_facecolor(primary_color)

        # set image configs
        img_width = 0.15
        img_height = 0.9
        margin = 0.02

        headshot_outlined = self.add_outline(headshot, outline_width=5)
        ax_headshot = ax.inset_axes([margin, 0.05, img_width, img_height])
        ax_headshot.imshow(headshot_outlined)
        ax_headshot.axis('off')

        logo_outlined = self.add_outline(logo, outline_width=4)
        logo_x = 1 - img_width - margin
        ax_logo = ax.inset_axes([logo_x, 0.05, img_width, img_height])
        ax_logo.imshow(logo_outlined)
        ax_logo.axis('off')

        # player name - bold and white for contrast
        ax.text(0.5, 0.95, bio["player_name"],
                va='top', ha='center', fontsize=22, fontweight='bold',
                color='white', transform=ax.transAxes)

        # bio info - lighter color
        hand_label = f'{bio["pitcher_hand"]}HP' if report_type == 'pitching' else f'{bio["bat_side"]}HB'
        ax.text(0.5, 0.48, f'{hand_label}  •  Age {bio["age"]}  •  {bio["height"]}  •  {bio["weight"]} lbs',
                va='top', ha='center', fontsize=12,
                color='white', transform=ax.transAxes)

        # season/date label - accent color
        if season is not None:
            date_label = f'{season} MLB Season'
        elif start_date and end_date:
            date_label = f'{start_date} to {end_date}'
        else:
            date_label = ''
        ax.text(0.5, 0.22, date_label,
                va='top', ha='center', fontsize=11, fontstyle='italic',
                color='white', transform=ax.transAxes)

        # accent line under the name
        ax.axhline(y=0.58, xmin=0.3, xmax=0.7, color=accent_color, linewidth=2)

        rect = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                      facecolor=primary_color, zorder=-1)
        ax.add_patch(rect)
        ax.axis("off")

    def add_outline(self, img: Image.Image, outline_width: int = 5, outline_color=(255, 255, 255, 255)):
        """adds a white outline around a PNG image using its alpha channel"""
        img = img.convert('RGBA')

        # extract alpha channel and dilate it to create the outline mask
        alpha = img.split()[3]
        dilated = alpha.filter(ImageFilter.MaxFilter(size=outline_width * 2 + 1))

        # create a solid white image the same size
        outline_layer = Image.new('RGBA', img.size, outline_color)
        outline_layer.putalpha(dilated)

        # composite: outline behind, original on top
        result = Image.alpha_composite(outline_layer, img)
        return result

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

    _CUSTOM_CMAP = mcolors.LinearSegmentedColormap.from_list(
        'blue_white_red', ['#4a86c8', '#ffffff', '#cc4444'])

    def get_color(self, z_score: float, invert=False, vmin=-3, vmax=3):
        """returns the color given the z score"""
        z = max(vmin, min(vmax, z_score))

        if invert:
            z = -z

        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        rgba = self._CUSTOM_CMAP(norm(z))

        return mcolors.to_hex(rgba)

