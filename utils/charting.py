# utils/charting.py

import altair as alt
from .logging_config import logger

def create_altair_candlestick_chart(df, filename):
    try:
        base = alt.Chart(df).encode(
            x='Date:T'
        )

        candlestick = base.mark_rule().encode(
            y='Low:Q',
            y2='High:Q'
        ).properties(width=800, height=400).mark_bar().encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Close:Q', title='Price', scale=alt.Scale(domain=[df['Low'].min(), df['High'].max()])),
            color=alt.condition(
                "datum.Open <= datum.Close", alt.value("green"), alt.value("red")
            ),
            tooltip=['Date:T', 'Open:Q', 'High:Q', 'Low:Q', 'Close:Q', 'Volume:Q']
        )

        volume = base.mark_bar().encode(
            y=alt.Y('Volume:Q', title='Volume', scale=alt.Scale(domain=[0, df['Volume'].max() * 1.1])),
            color=alt.value('blue')
        ).properties(width=800, height=150)

        chart = alt.vconcat(candlestick, volume).resolve_scale(y='independent')

        # Save the chart as an image
        chart.save(filename, format='png')
        logger.info(f"Chart saved as {filename}")
        return chart
    
    except Exception as e:
        logger.exception(f"Error creating or saving chart: {str(e)}")
        return None
