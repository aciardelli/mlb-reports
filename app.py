import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from PitchingReport import PitchingReport
from BattingReport import BattingReport
from helpers import get_pitcher_names, get_batter_names
import io
from matplotlib.backends.backend_pdf import PdfPages

pr = PitchingReport()
br = BattingReport()

st.title('MLB Reports')

report_type = st.selectbox(
    "Report Type",
    ['Pitching', 'Batting'],
    index=None,
    placeholder="Select a report type"
)

if report_type is not None:
    date_mode = st.radio("Date Range", ["Season", "Custom"], horizontal=True)

    if date_mode == "Season":
        season = st.selectbox("Season", list(range(2025, 2014, -1)), index=0)
        start_date = None
        end_date = None
        player_season = season
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2025, 3, 27))
        with col2:
            end_date = st.date_input("End Date", value=date(2025, 10, 1))
        season = None
        player_season = start_date.year

if report_type == 'Pitching':
    df_pitcher_names = get_pitcher_names(season=player_season)

    player_name = st.selectbox(
        "Players",
        (df_pitcher_names['PlayerName']),
        index=None,
        placeholder="Select a player",
    )

if report_type == 'Batting':
    df_batter_names = get_batter_names(season=player_season)

    player_name = st.selectbox(
        "Players",
        (df_batter_names['PlayerName']),
        index=None,
        placeholder="Select a player",
    )

if report_type == 'Pitching' and player_name:
    mlbam_player_id = df_pitcher_names[df_pitcher_names['PlayerName'] == player_name]['xMLBAMID'].values[0]
    fangraphs_player_id = df_pitcher_names[df_pitcher_names['PlayerName'] == player_name]['playerid'].values[0]

    player_ids = {
        "mlbam_id": mlbam_player_id,
        "fangraphs_id": fangraphs_player_id
    }

    with st.spinner("Generating pitching report..."):
        if date_mode == "Season":
            fig = pr.construct_pitching_summary(player_ids, start_date=f'{season}-03-01', end_date=f'{season}-11-01', season=season)
        else:
            fig = pr.construct_pitching_summary(player_ids, start_date=str(start_date), end_date=str(end_date))
    st.pyplot(fig)

    # create pdf
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
            pdf.savefig(fig, bbox_inches="tight")
    pdf_buffer.seek(0)


    st.download_button(
        label="Download Report (PDF)",
        data=pdf_buffer,
        file_name=f"pitching_report.pdf",
        mime="application/pdf"
    )

if report_type == 'Batting' and player_name:
    mlbam_player_id = df_batter_names[df_batter_names['PlayerName'] == player_name]['xMLBAMID'].values[0]
    fangraphs_player_id = df_batter_names[df_batter_names['PlayerName'] == player_name]['playerid'].values[0]


    player_ids = {
        "mlbam_id": mlbam_player_id,
        "fangraphs_id": fangraphs_player_id
    }

    with st.spinner("Generating batting report..."):
        if date_mode == "Season":
            fig = br.construct_batting_summary(player_ids, start_date=f'{season}-03-01', end_date=f'{season}-11-01', season=season)
        else:
            fig = br.construct_batting_summary(player_ids, start_date=str(start_date), end_date=str(end_date))
    st.pyplot(fig)

    # create pdf
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
            pdf.savefig(fig, bbox_inches="tight")
    pdf_buffer.seek(0)


    st.download_button(
        label="Download Report (PDF)",
        data=pdf_buffer,
        file_name=f"batting_report.pdf",
        mime="application/pdf"
    )
