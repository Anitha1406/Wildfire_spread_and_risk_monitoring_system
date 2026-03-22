from dash import dcc, html, Input, Output, State
import pandas as pd
from pymongo import MongoClient
import numpy as np
import plotly.express as px
import dash_leaflet as dl

import dash
# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://chitti14065_db_user:anitha@cluster0.vcgahfw.mongodb.net/?appName=Cluster0"
DB_NAME = "wildfire_db"
COLLECTION_NAME = "fire_events_enriched"

MAPBOX_TOKEN = "YOUR_MAPBOX_TOKEN"  # Replace with your actual Mapbox token

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]
data = list(collection.find())
wildfire_df = pd.DataFrame(data)
client.close()

RISK_PALETTE = {
    "LOW": "#16a34a",      # green-teal
    "MEDIUM": "#f59e0b",   # amber
    "HIGH": "#ef6c00",     # deep orange
    "EXTREME": "#dc2626"   # red
}
app = dash.Dash(__name__, external_stylesheets=["https://fonts.googleapis.com/css?family=Montserrat:700,400", "https://codepen.io/chriddyp/pen/bWLwgP.css", "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"])
# Allow callbacks for components created dynamically inside tabs
app.config.suppress_callback_exceptions = True
app.title = "Wildfire Insights Dashboard"

app.layout = html.Div([
    html.Div([
                html.H1([html.I(className="fa fa-fire", style={"color": "#06b6d4", "margin-right": "10px"}), "Wildfire Insights Dashboard"], className="site-title", style={
                            "color": "#06b6d4",
                        "font-family": "Montserrat",
                        "font-weight": "700",
                        "font-size": "2.5em",
                        "background": "#0f1724",
                        "padding": "0.5em 1em",
                        "border-radius": "12px",
                            "box-shadow": "0 0 8px rgba(6,182,212,0.10)",
                        "margin-bottom": "1em"
                }),
                html.Div(dcc.Tabs(id="tabs", value="tab-map", children=[
                        dcc.Tab(label="Live Fire Map", value="tab-map", className="tab", style={"background": "#0f1724", "color": "#f3f4f6", "font-family": "Montserrat", "font-weight": "700"}),
                        dcc.Tab(label="Wildfire Risk Analysis", value="tab-risk", className="tab", style={"background": "#0f1724", "color": "#f3f4f6", "font-family": "Montserrat", "font-weight": "700"}),
                        dcc.Tab(label="Environmental Drivers", value="tab-env", className="tab", style={"background": "#0f1724", "color": "#f3f4f6", "font-family": "Montserrat", "font-weight": "700"}),
                        dcc.Tab(label="Fire Spread Insights", value="tab-spread", className="tab", style={"background": "#0f1724", "color": "#f3f4f6", "font-family": "Montserrat", "font-weight": "700"}),
                        dcc.Tab(label="Operational Watchlist", value="tab-watch", className="tab", style={"background": "#0f1724", "color": "#f3f4f6", "font-family": "Montserrat", "font-weight": "700"})
                ]), className="tabs-container"),
        html.Div(id="tab-content", style={
              "background": "#0b1220",
              "padding": "2em",
              "border-radius": "16px",
              "box-shadow": "0 0 12px rgba(56,189,248,0.10)",
              "margin-top": "2em"
        })
    ], style={
        "background": "#0f1724",
        "padding": "2em",
        "border-radius": "16px",
        "box-shadow": "0 0 12px rgba(56,189,248,0.06)",
        "margin": "2em"
    })
], style={
    "background": "#0f1724",
    "min-height": "100vh"
})

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html, body, #react-entry-point, .dash-app { height: 100%; }
            body { margin: 0; background: #0f1724; color: #f3f4f6; font-family: Montserrat, Arial, sans-serif; }
            /* Header */
            .dcc-Header { display:flex; align-items:center; gap:1rem; }
            .site-title { font-weight:700; color:#06b6d4; letter-spacing: -0.5px; }
            .site-title .fa-fire { margin-right: 8px; transform: translateY(2px); }
            /* subtle title glow animation */
            @keyframes titleGlow { 0% { text-shadow: 0 0 0 rgba(6,182,212,0.0);} 50% { text-shadow: 0 0 18px rgba(6,182,212,0.06);} 100% { text-shadow: 0 0 0 rgba(6,182,212,0.0);} }
            .site-title { animation: titleGlow 6s ease-in-out infinite; }
            /* Tabs center and modern spacing */
            .tabs-container { display:flex; justify-content:center; margin-top: 1rem; }
            .tab { padding: 12px 22px !important; border-radius:10px !important; }
            /* reduce contrast on selected tab underline */
            .tab--selected { background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "tab-map":
        palette = RISK_PALETTE
        if wildfire_df.empty:
            return html.Div([
                html.H2("Live Fire Map", style={"color": "#e6e6e6"}),
                html.Div("No wildfire data available.", style={"color": "#e0e0e0"})
            ])
        fig = px.scatter_mapbox(
            wildfire_df,
            lat="latitude",
            lon="longitude",
            color="risk_level",
            size="spread_distance_km",
            custom_data=["fire_id", "risk_level", "risk_score", "frp", "humidity", "wind_speed", "spatiotemporal_neighbor_count", "spread_distance_km", "event_timestamp"],
            color_discrete_map=palette,
            zoom=4,
            height=800
        )
        fig.update_traces(
            marker=dict(
                opacity=0.85,
                sizemode="area",
                sizemin=6,
                sizeref=0.5,
                symbol="circle"
            ),
            hovertemplate=
                "<span style='color:#e6e6e6'>"
                "<b>Fire ID:</b> %{customdata[0]}<br>"
                "<b>Risk Level:</b> %{customdata[1]}<br>"
                "<b>Risk Score:</b> %{customdata[2]}<br>"
                "<b>FRP:</b> %{customdata[3]}<br>"
                "<b>Humidity:</b> %{customdata[4]}%<br>"
                "<b>Wind Speed:</b> %{customdata[5]} km/h<br>"
                "<b>Neighbor Count:</b> %{customdata[6]}<br>"
                "<b>Predicted Spread:</b> %{customdata[7]} km<br>"
                "<b>Detection Time:</b> %{customdata[8]}<extra></extra>"
                "</span>"
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#f3f4f6")), font_color="#f3f4f6")
        return html.Div([
            html.H2("Live Fire Map", style={"color": "#f3f4f6"}),
            dcc.Graph(figure=fig, style={"height": "90vh", "background": "#181818", "border-radius": "16px"})
        ])
    elif tab == "tab-risk":
        palette = RISK_PALETTE
        # Risk level distribution chart
        risk_counts = wildfire_df["risk_level"].value_counts().reindex(["LOW", "MEDIUM", "HIGH", "EXTREME"], fill_value=0)
        bar_fig = px.bar(
            x=risk_counts.index,
            y=risk_counts.values,
            color=risk_counts.index,
            color_discrete_map=palette,
            labels={"x": "Risk Level", "y": "Count"},
            title="Current Risk Level Distribution"
        )
        bar_fig.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")
        # Top highest risk fires table
        top_risk = wildfire_df.sort_values("risk_score", ascending=False).head(10)
        table_cols = ["latitude", "longitude", "risk_level", "risk_score", "frp", "event_timestamp"]
        table_html = html.Table([
            html.Thead(html.Tr([html.Th(col, style={"color": "#f3f4f6", "background": "#ef4444"}) for col in table_cols])),
            html.Tbody([
                html.Tr([
                    html.Td(str(row[col]), style={"color": palette.get(row["risk_level"], "#f3f4f6")}) if col == "risk_level" else html.Td(str(row[col]), style={"color": "#f3f4f6"})
                    for col in table_cols
                ]) for _, row in top_risk.iterrows()
            ])
        ], style={"width": "100%", "margin-top": "1em", "background": "#0b1220", "border-radius": "8px"})
        # Map highlighting only HIGH and EXTREME risk fires
        high_risk = wildfire_df[wildfire_df["risk_level"].isin(["HIGH", "EXTREME"])]
        map_fig = None
        if not high_risk.empty:
            map_fig = px.scatter_mapbox(
                high_risk,
                lat="latitude",
                lon="longitude",
                color="risk_level",
                size="spread_distance_km",
                custom_data=["fire_id", "risk_level", "risk_score", "frp", "humidity", "wind_speed", "spatiotemporal_neighbor_count", "spread_distance_km", "event_timestamp"],
                color_discrete_map=palette,
                zoom=4,
                height=500
            )
            map_fig.update_traces(
                marker=dict(
                    opacity=0.85,
                    sizemode="area",
                    sizemin=6,
                    sizeref=0.5,
                    symbol="circle"
                ),
                hovertemplate=
                    "<span style='color:#e6e6e6'>"
                    "<b>Fire ID:</b> %{customdata[0]}<br>"
                    "<b>Risk Level:</b> %{customdata[1]}<br>"
                    "<b>Risk Score:</b> %{customdata[2]}<br>"
                    "<b>FRP:</b> %{customdata[3]}<br>"
                    "<b>Humidity:</b> %{customdata[4]}%<br>"
                    "<b>Wind Speed:</b> %{customdata[5]} km/h<br>"
                    "<b>Neighbor Count:</b> %{customdata[6]}<br>"
                    "<b>Predicted Spread:</b> %{customdata[7]} km<br>"
                    "<b>Detection Time:</b> %{customdata[8]}<extra></extra>"
                    "</span>"
            )
            map_fig.update_layout(mapbox_style="open-street-map")
            map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#f3f4f6")), font_color="#f3f4f6")
        return html.Div([
            html.H2("Wildfire Risk Analysis", style={"color": "#f3f4f6"}),
            dcc.Graph(figure=bar_fig, style={"height": "350px", "background": "#181818", "border-radius": "16px"}),
            html.H3("Top Highest Risk Fires", style={"color": "#f3f4f6", "margin-top": "1em"}),
            table_html,
            html.H3("High/Extreme Risk Fires Map", style={"color": "#f3f4f6", "margin-top": "1em"}),
            dcc.Graph(figure=map_fig, style={"height": "500px", "background": "#0b1220", "border-radius": "16px"}) if map_fig else html.Div("No high/extreme risk fires to display.", style={"color": "#f3f4f6"})
        ])
    elif tab == "tab-env":
        # Environmental Drivers: relationship visuals and correlation stats
        palette = RISK_PALETTE
        if wildfire_df.empty:
            return html.Div([
                html.H2("Environmental Drivers", style={"color": "#e6e6e6"}),
                html.Div("No wildfire data available.", style={"color": "#e0e0e0"})
            ])

        def corr_value(x, y):
            if x in wildfire_df.columns and y in wildfire_df.columns:
                df = wildfire_df[[x, y]].dropna()
                if len(df) >= 2:
                    return round(df[x].corr(df[y]), 3), len(df)
            return None, 0

        # Wind speed vs predicted spread
        fig_wind = None
        if "wind_speed" in wildfire_df.columns and "spread_distance_km" in wildfire_df.columns:
            fig_wind = px.scatter(
                wildfire_df,
                x="wind_speed",
                y="spread_distance_km",
                color="risk_level",
                color_discrete_map=palette,
                labels={"wind_speed": "Wind Speed (km/h)", "spread_distance_km": "Predicted Spread (km)"},
                title="Wind Speed vs Predicted Spread"
            )
            fig_wind.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")

        # Humidity vs risk score
        fig_humidity = None
        if "humidity" in wildfire_df.columns and "risk_score" in wildfire_df.columns:
            fig_humidity = px.scatter(
                wildfire_df,
                x="humidity",
                y="risk_score",
                color="risk_level",
                color_discrete_map=palette,
                labels={"humidity": "Humidity (%)", "risk_score": "Risk Score"},
                title="Humidity vs Risk Score"
            )
            fig_humidity.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")

        # Temperature vs risk score
        fig_temp = None
        if "temperature" in wildfire_df.columns and "risk_score" in wildfire_df.columns:
            fig_temp = px.scatter(
                wildfire_df,
                x="temperature",
                y="risk_score",
                color="risk_level",
                color_discrete_map=palette,
                labels={"temperature": "Temperature (°C)", "risk_score": "Risk Score"},
                title="Temperature vs Risk Score"
            )
            fig_temp.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")

        # Compute correlation summaries
        wind_corr, wind_n = corr_value("wind_speed", "spread_distance_km")
        hum_corr, hum_n = corr_value("humidity", "risk_score")
        temp_corr, temp_n = corr_value("temperature", "risk_score")

        corr_cards = html.Div([
            html.Div([
                html.H4("Wind ↔ Spread", style={"margin": "0", "color": "#f3f4f6"}),
                html.P((f"Pearson r: {wind_corr}" if wind_corr is not None else "insufficient data"), style={"color": "#f3f4f6", "margin": "0"}),
                html.P((f"Samples: {wind_n}" if wind_n else ""), style={"color": "#cbd5e1", "margin": "0", "font-size": "0.9em"})
            ], style={"padding": "12px", "background": "#0b1220", "border-radius": "8px", "width": "30%"}),
            html.Div([
                html.H4("Humidity ↔ Risk", style={"margin": "0", "color": "#f3f4f6"}),
                html.P((f"Pearson r: {hum_corr}" if hum_corr is not None else "insufficient data"), style={"color": "#f3f4f6", "margin": "0"}),
                html.P((f"Samples: {hum_n}" if hum_n else ""), style={"color": "#cbd5e1", "margin": "0", "font-size": "0.9em"})
            ], style={"padding": "12px", "background": "#0b1220", "border-radius": "8px", "width": "30%", "margin-left": "1em"}),
            html.Div([
                html.H4("Temp ↔ Risk", style={"margin": "0", "color": "#f3f4f6"}),
                html.P((f"Pearson r: {temp_corr}" if temp_corr is not None else "insufficient data"), style={"color": "#f3f4f6", "margin": "0"}),
                html.P((f"Samples: {temp_n}" if temp_n else ""), style={"color": "#cbd5e1", "margin": "0", "font-size": "0.9em"})
            ], style={"padding": "12px", "background": "#0b1220", "border-radius": "8px", "width": "30%", "margin-left": "1em"})
        ], style={"display": "flex", "margin-top": "1em"})

        pearson_explain = html.Div([
            html.H4("What is Pearson r?", style={"color": "#f3f4f6", "margin-top": "1em"}),
            html.P("Pearson r measures the strength and direction of a linear relationship between two numerical variables (\n-1 to 1).", style={"color": "#cbd5e1", "margin": "0.2em 0 0.6em 0", "max-width": "72%"}),
            html.Ul([
                html.Li("r ≈ 0: little or no linear relationship", style={"color": "#cbd5e1"}),
                html.Li("r > 0: positive relationship — as X increases, Y tends to increase", style={"color": "#cbd5e1"}),
                html.Li("r < 0: negative relationship — as X increases, Y tends to decrease", style={"color": "#cbd5e1"}),
                html.Li("Rough strength guide: |r| < 0.2 weak, 0.2–0.5 moderate, >0.5 strong", style={"color": "#cbd5e1"})
            ], style={"margin-top": "0.4em"})
        ], style={"padding": "12px", "background": "#071223", "border-radius": "8px", "margin-top": "1em"})

        return html.Div([
            html.H2("Environmental Drivers", style={"color": "#e6e6e6"}),
            corr_cards,
            pearson_explain,
            html.Div([
                dcc.Graph(figure=fig_wind, style={"width": "49%", "display": "inline-block"}) if fig_wind else html.Div("Wind vs Spread data not available", style={"color": "#e6e6e6"}),
                dcc.Graph(figure=fig_humidity, style={"width": "49%", "display": "inline-block", "float": "right"}) if fig_humidity else html.Div("Humidity vs Risk data not available", style={"color": "#e6e6e6"})
            ], style={"margin-top": "1em"}),
            html.Div([
                dcc.Graph(figure=fig_temp, style={"width": "100%"}) if fig_temp else html.Div("Temperature vs Risk data not available", style={"color": "#e6e6e6"})
            ], style={"margin-top": "1em"})
        ])
    elif tab == "tab-spread":
        # Fire Spread Insights: distribution, drivers, and top spread events
        palette = RISK_PALETTE

        if wildfire_df.empty:
            return html.Div([
                html.H2("Fire Spread Insights", style={"color": "#f3f4f6"}),
                html.Div("No wildfire data available.", style={"color": "#e0e0e0"})
            ])

        # Histogram of predicted spread distances
        hist_fig = None
        if "spread_distance_km" in wildfire_df.columns:
            hist_fig = px.histogram(
                wildfire_df.dropna(subset=["spread_distance_km"]),
                x="spread_distance_km",
                nbins=30,
                title="Predicted Spread (km) Distribution",
                labels={"spread_distance_km": "Predicted Spread (km)", "count": "Count"}
            )
            hist_fig.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")

        # Scatter: spread vs wind speed
        scatter_fig = None
        if "wind_speed" in wildfire_df.columns and "spread_distance_km" in wildfire_df.columns:
            scatter_fig = px.scatter(
                wildfire_df.dropna(subset=["wind_speed", "spread_distance_km"]),
                x="wind_speed",
                y="spread_distance_km",
                color="risk_level",
                color_discrete_map=palette,
                labels={"wind_speed": "Wind Speed (km/h)", "spread_distance_km": "Predicted Spread (km)"},
                title="Predicted Spread vs Wind Speed"
            )
            scatter_fig.update_layout(paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6")

        # Top spread events table and map
        top_spread = wildfire_df.dropna(subset=["spread_distance_km"]).sort_values("spread_distance_km", ascending=False).head(15)
        table_cols = ["fire_id", "latitude", "longitude", "risk_level", "spread_distance_km", "event_timestamp"]
        top_table = html.Table([
            html.Thead(html.Tr([html.Th(col, style={"color": "#f3f4f6", "background": "#ef4444"}) for col in table_cols])),
            html.Tbody([
                html.Tr([
                    html.Td(str(row.get(col, "")), style={"color": palette.get(row.get("risk_level"), "#f3f4f6")}) if col == "risk_level" else html.Td(str(row.get(col, "")), style={"color": "#f3f4f6"})
                    for col in table_cols
                ]) for _, row in top_spread.iterrows()
            ])
        ], style={"width": "100%", "margin-top": "1em", "background": "#0b1220", "border-radius": "8px"})

        map_fig = None
        if not top_spread.empty and "latitude" in top_spread.columns and "longitude" in top_spread.columns:
            # If multiple events share identical coordinates, add a tiny jitter so markers are visible separately
            df_plot = top_spread.reset_index(drop=True).copy()
            if not df_plot.empty:
                # count duplicates and compute an index within each group
                group_counts = df_plot.groupby(["latitude", "longitude"])['latitude'].transform('count').astype(float)
                cum_idx = df_plot.groupby(["latitude", "longitude"]).cumcount().astype(float)
                jitter_scale = 0.0006  # ~60m latitude/longitude offset
                # center the jitter around zero for each group
                df_plot['__lat_shift'] = (cum_idx - (group_counts - 1) / 2.0) * jitter_scale
                # apply small longitude jitter scaled by cos(lat) to keep distances reasonable
                df_plot['__lon_shift'] = df_plot['__lat_shift'] / np.cos(np.deg2rad(df_plot['latitude'].astype(float)).replace(0, 1))
                df_plot['latitude'] = df_plot['latitude'].astype(float) + df_plot['__lat_shift']
                df_plot['longitude'] = df_plot['longitude'].astype(float) + df_plot['__lon_shift']

            map_fig = px.scatter_mapbox(
                    df_plot,
                    lat="latitude",
                    lon="longitude",
                    color="risk_level",
                    size="spread_distance_km",
                    size_max=12,
                    color_discrete_map=palette,
                    custom_data=["fire_id", "risk_level", "spread_distance_km", "event_timestamp"],
                    zoom=4,
                    height=450,
                    title="Top Predicted Spread Events"
                )
            map_fig.update_traces(
                    marker=dict(opacity=0.85, sizemode="area", sizemin=4, allowoverlap=True),
                    hovertemplate="<span style='color:#f3f4f6'><b>Fire:</b> %{customdata[0]}<br><b>Risk:</b> %{customdata[1]}<br><b>Spread:</b> %{customdata[2]} km<br><b>Time:</b> %{customdata[3]}<extra></extra></span>"
                )
            map_fig.update_layout(mapbox_style="open-street-map", paper_bgcolor="#0f1724", plot_bgcolor="#0f1724", font_color="#f3f4f6", legend=dict(font=dict(color="#f3f4f6")))

        return html.Div([
            html.H2("Fire Spread Intelligence", style={"color": "#f3f4f6"}),
            html.Div([
                dcc.Graph(figure=hist_fig, style={"width": "49%", "display": "inline-block"}) if hist_fig else html.Div("Spread data not available", style={"color": "#f3f4f6"}),
                dcc.Graph(figure=scatter_fig, style={"width": "49%", "display": "inline-block", "float": "right"}) if scatter_fig else html.Div("Wind/Spread data not available", style={"color": "#f3f4f6"})
            ], style={"margin-top": "1em"}),
            html.H3("Top Predicted Spread Events", style={"color": "#f3f4f6", "margin-top": "1em"}),
            top_table,
            html.Div([dcc.Graph(figure=map_fig, style={"height": "450px", "background": "#0b1220", "border-radius": "12px"})]) if map_fig else html.Div()
        ])
    elif tab == "tab-watch":
        # Operational Watchlist: filters and priority table
        if wildfire_df.empty:
            return html.Div([
                html.H2("Operational Watchlist", style={"color": "#f3f4f6"}),
                html.Div("No wildfire data available.", style={"color": "#e0e0e0"})
            ])

        filter_panel = html.Div([
            html.Div([
                html.Label("Risk Levels", style={"color": "#f3f4f6"}),
                dcc.Dropdown(id="watch-filter-risk", options=[
                    {"label": "LOW", "value": "LOW"},
                    {"label": "MEDIUM", "value": "MEDIUM"},
                    {"label": "HIGH", "value": "HIGH"},
                    {"label": "EXTREME", "value": "EXTREME"}
                ], multi=True, placeholder="Select risk levels", value=["HIGH", "EXTREME"], style={"width": "260px"})
            ], style={"display": "inline-block", "margin-right": "1em"}),
            html.Button("Submit", id="watch-submit", n_clicks=0, style={"background": "#38bdf8", "color": "#07203a", "border": "none", "padding": "8px 12px", "border-radius": "6px"})
        ], style={"margin-bottom": "1em"})

        table_container = html.Div(id="watch-table")

        return html.Div([
            html.H2("Operational Watchlist", style={"color": "#f3f4f6"}),
            filter_panel,
            table_container
        ])
    else:
        return html.Div("Select a tab.")

@app.callback(
    Output("watch-table", "children"),
    Input("watch-submit", "n_clicks"),
    State("watch-filter-risk", "value")
)
def update_watch_table(n_clicks, risk_levels):
    # Server-side filtering of the global wildfire_df triggered by Submit
    df = wildfire_df.copy()
    if df.empty:
        return html.Div("No data", style={"color": "#e6e6e6"})

    if risk_levels:
        df = df[df["risk_level"].isin(risk_levels)]

    # sort by risk_score (if present) then by spread
    if "risk_score" in df.columns:
        df = df.sort_values(["risk_score", "spread_distance_km"], ascending=[False, False])
    else:
        df = df.sort_values("spread_distance_km", ascending=False)

    display_rows = df.head(100)
    if display_rows.empty:
        return html.Div("No matching events", style={"color": "#f3f4f6"})

    cols = ["fire_id", "event_timestamp", "risk_level", "risk_score", "spread_distance_km", "latitude", "longitude"]
    table = html.Table([
        html.Thead(html.Tr([html.Th(c, style={"color": "#f3f4f6", "background": "#0b1220"}) for c in cols])),
        html.Tbody([
            html.Tr([
                html.Td(str(row.get(c, "")), style={"color": "#f3f4f6"}) for c in cols
            ]) for _, row in display_rows.iterrows()
        ])
    ], style={"width": "100%", "background": "#0b1220", "border-radius": "8px", "margin-top": "0.5em"})

    return table


if __name__ == "__main__":
    app.run(debug=True)
