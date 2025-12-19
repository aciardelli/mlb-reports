import streamlit as st
import pandas as pd
import numpy as np
from PitchingReport import PitchingReport
from helpers import get_player_names
import io
from matplotlib.backends.backend_pdf import PdfPages

df_player_names = get_player_names()
pr = PitchingReport()

st.title('Pitching Reports')

player_name = st.selectbox(
    "Players",
    (df_player_names['PlayerName']),
    index=None,
    placeholder="Select a player",
)

if player_name:
    player_id = df_player_names[df_player_names['PlayerName'] == player_name]['xMLBAMID'].values[0]

    fig = pr.construct_pitching_summary(player_id)
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
