import streamlit as st
import pandas as pd
import numpy as np
from PitchingReport import PitchingReport
from BattingReport import BattingReport
from helpers import get_pitcher_names, get_batter_names
import io
from matplotlib.backends.backend_pdf import PdfPages

pr = PitchingReport()
br = BattingReport()
df_batter_names = None
df_pitcher_names = None

st.title('MLB Reports')

report_type = st.selectbox(
    "Report Type",
    ['Pitching', 'Batting'],
    index=None,
    placeholder="Select a report type"
)

start_date = st.date_input(
    "Start Date",
    "2025-03-27",
)

end_date = st.date_input(
    "End Date",
    "2025-10-01",
)

if report_type == 'Pitching':
    if df_pitcher_names is None:
        df_pitcher_names = get_pitcher_names()

    player_name = st.selectbox(
        "Players",
        (df_pitcher_names['PlayerName']),
        index=None,
        placeholder="Select a player",
    )

if report_type == 'Batting':
    if df_batter_names is None:
        df_batter_names = get_batter_names()

    player_name = st.selectbox(
        "Players",
        (df_batter_names['PlayerName']),
        index=None,
        placeholder="Select a player",
    )

if report_type == 'Pitching' and player_name:
    mlbam_player_id = df_pitcher_names[df_pitcher_names['PlayerName'] == player_name]['xMLBAMID'].values[0]
    fangraphs_player_id = df_pitcher_names[df_pitcher_names['PlayerName'] == player_name]['FangraphsID'].values[0]

    player_ids = {
        "mlbam_id": mlbam_player_id,
        "fangraphs_id": fangraphs_player_id
    }

    fig = pr.construct_pitching_summary(player_ids)
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
    fangraphs_player_id = df_pitcher_names[df_pitcher_names['PlayerName'] == player_name]['FangraphsID'].values[0]


    player_ids = {
        "mlbam_id": mlbam_player_id,
        "fangraphs_id": fangraphs_player_id
    }

    fig = br.construct_batting_summary(player_ids)
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
