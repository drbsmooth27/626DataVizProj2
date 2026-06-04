import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import pycountry
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("results.csv")
df.columns = df.columns.str.strip()

df = df[[
    "Sale Month",
    "Title",
    "Store",
    "Quantity",
    "Country of Sale",
    "Earnings (USD)"
]]

df = df.rename(columns={
    "Sale Month": "sale_month",
    "Title": "title",
    "Store": "store",
    "Quantity": "quantity",
    "Country of Sale": "country_code",
    "Earnings (USD)": "earnings"
})

df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
df["earnings"] = pd.to_numeric(df["earnings"], errors="coerce").fillna(0)

df["sale_month"] = df["sale_month"].astype(str).str.strip()
df["title"] = df["title"].astype(str).str.strip()
df["store"] = df["store"].astype(str).str.strip()
df["country_code"] = df["country_code"].astype(str).str.strip().str.upper()

def get_country_name(code):
    country = pycountry.countries.get(alpha_2=str(code).upper())
    if country:
        return country.name
    return str(code)

def get_iso3(code):
    country = pycountry.countries.get(alpha_2=str(code).upper())
    if country:
        return country.alpha_3
    return None

df["country"] = df["country_code"].apply(get_country_name)
df["iso_alpha"] = df["country_code"].apply(get_iso3)

print("Missing country mappings:")
print(sorted(df[df["iso_alpha"].isna()]["country_code"].dropna().unique()))

youtube_embed_url = "https://www.youtube.com/embed/WSMkMtFdJtA"

first_milestone = 500_000
second_milestone = 1_000_000

BRONCOS_NAVY = "#002244"
BRONCOS_ORANGE = "#FB4F14"
BRONCOS_BLUE = "#0A2342"
LIGHT_BG = "#f3f6fb"
CARD_BG = "#ffffff"

sale_months = sorted(df["sale_month"].unique())
month_to_index = {month: i for i, month in enumerate(sale_months)}
index_to_month = {i: month for i, month in enumerate(sale_months)}
df["month_index"] = df["sale_month"].map(month_to_index)

store_options = sorted(df["store"].dropna().unique())
country_options = sorted(df["country"].dropna().unique())

def estimate_billboard_units(row):
    if "YouTube" in row["store"] or "Ads" in row["store"]:
        return row["quantity"] / 3750
    return row["quantity"] / 1250

df["billboard_units"] = df.apply(estimate_billboard_units, axis=1)

def card_style():
    return {
        "backgroundColor": CARD_BG,
        "padding": "20px",
        "borderRadius": "18px",
        "boxShadow": "0 8px 24px rgba(0, 34, 68, 0.12)",
        "border": "1px solid rgba(0, 34, 68, 0.08)"
    }

def label_style():
    return {
        "fontWeight": "700",
        "display": "block",
        "marginBottom": "8px",
        "color": BRONCOS_NAVY
    }

def summary_card(title, value, subtitle=""):
    return html.Div(
        style={
            "backgroundColor": CARD_BG,
            "padding": "22px",
            "borderRadius": "18px",
            "boxShadow": "0 8px 24px rgba(0, 34, 68, 0.12)",
            "borderTop": f"5px solid {BRONCOS_ORANGE}"
        },
        children=[
            html.Div(title, style={
                "color": BRONCOS_NAVY,
                "fontSize": "14px",
                "fontWeight": "800",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px"
            }),
            html.Div(value, style={
                "fontSize": "30px",
                "fontWeight": "900",
                "marginTop": "8px",
                "color": BRONCOS_NAVY
            }),
            html.Div(subtitle, style={
                "color": "#6b7280",
                "fontSize": "13px",
                "marginTop": "6px"
            })
        ]
    )

def data_table_style():
    return {
        "style_table": {"overflowX": "auto"},
        "style_header": {
            "backgroundColor": BRONCOS_NAVY,
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "left"
        },
        "style_cell": {
            "padding": "10px",
            "textAlign": "left",
            "fontFamily": "Arial",
            "fontSize": "14px",
            "minWidth": "120px",
            "width": "150px",
            "maxWidth": "220px",
            "whiteSpace": "normal"
        },
        "style_data_conditional": [
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f9fafb"
            }
        ]
    }

def clean_chart_layout(fig):
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_font_color=BRONCOS_NAVY,
        font={"color": BRONCOS_NAVY}
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e5e7eb")
    fig.update_yaxes(showgrid=True, gridcolor="#e5e7eb")
    return fig

app = dash.Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Inter, Arial, sans-serif",
        "backgroundColor": LIGHT_BG,
        "padding": "24px"
    },
    children=[

        html.Div(
            style={
                "background": f"linear-gradient(135deg, {BRONCOS_NAVY}, {BRONCOS_BLUE})",
                "color": "white",
                "padding": "30px",
                "borderRadius": "20px",
                "marginBottom": "20px",
                "borderBottom": f"8px solid {BRONCOS_ORANGE}"
            },
            children=[
    html.Div(
        "BRONCOS COUNTRY ANTHEM",
        style={
            "fontSize": "14px",
            "fontWeight": "800",
            "letterSpacing": "2px",
            "color": BRONCOS_ORANGE
        }
    ),
    html.H1(
        "Music Streaming Milestone Dashboard",
        style={"margin": "6px 0 0 0", "fontSize": "36px"}
    ),
    html.P(
        "Broncos Country Anthem: A University of Colorado student-created anthem connecting campus, community, and Broncos Football fans worldwide.",
        style={"marginTop": "10px", "color": "#dbeafe", "fontSize": "16px"}
    )
]
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr 1fr",
                "gap": "16px",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style=card_style(),
                    children=[
                        html.Label("Select Song", style=label_style()),
                        dcc.Dropdown(
                            id="song-filter",
                            options=[
                                {"label": song, "value": song}
                                for song in sorted(df["title"].unique())
                            ],
                            value=sorted(df["title"].unique())[0],
                            clearable=False
                        )
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.Label("Select Stores / Platforms", style=label_style()),
                        dcc.Dropdown(
                            id="store-filter",
                            options=[
                                {"label": store, "value": store}
                                for store in store_options
                            ],
                            value=store_options,
                            multi=True
                        )
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.Label("Select Countries", style=label_style()),
                        dcc.Dropdown(
                            id="country-filter",
                            options=[
                                {"label": country, "value": country}
                                for country in country_options
                            ],
                            value=country_options,
                            multi=True
                        )
                    ]
                )
            ]
        ),

        html.Div(
            style={**card_style(), "marginBottom": "20px"},
            children=[
                html.Label("Select Sale Month Range", style=label_style()),
                dcc.RangeSlider(
                    id="month-range",
                    min=0,
                    max=len(sale_months) - 1,
                    step=1,
                    value=[0, len(sale_months) - 1],
                    marks={
                        i: {
                            "label": month,
                            "style": {"color": BRONCOS_NAVY, "fontWeight": "600"}
                        }
                        for i, month in index_to_month.items()
                    },
                    tooltip={"placement": "bottom", "always_visible": False}
                )
            ]
        ),

        html.Div(
            id="summary-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "16px",
                "marginBottom": "20px"
            }
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1.5fr 1fr",
                "gap": "20px",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Music Video", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        html.Iframe(
                            src=youtube_embed_url,
                            style={
                                "width": "100%",
                                "height": "360px",
                                "border": "0",
                                "borderRadius": "14px"
                            },
                            allow=(
                                "accelerometer; autoplay; clipboard-write; "
                                "encrypted-media; gyroscope; picture-in-picture; web-share"
                            )
                        )
                    ]
                ),

                html.Div(id="platform-panel", style=card_style())
            ]
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "2fr 1fr",
                "gap": "20px",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Global Stream Map", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="world-map")
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Milestone Tracker", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="milestone-gauge")
                    ]
                )
            ]
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px",
                "marginBottom": "20px"
            },
            children=[
                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Monthly Stream Growth", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="monthly-line")
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Top 10 Platform Leaderboard", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="platform-bar")
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Top 10 Countries", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="country-bar")
                    ]
                ),

                html.Div(
                    style=card_style(),
                    children=[
                        html.H3("Top 10 Streams vs Billboard Units", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                        dcc.Graph(id="unit-comparison")
                    ]
                )
            ]
        ),

        html.Div(
            style=card_style(),
            children=[
                html.H3("All Store Summary", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                html.Div(id="store-table")
            ]
        ),

        html.Div(
            style={**card_style(), "marginTop": "20px"},
            children=[
                html.H3("All Country Summary", style={"marginTop": "0", "color": BRONCOS_NAVY}),
                html.Div(id="country-table")
            ]
        )
    ]
)

@app.callback(
    Output("summary-cards", "children"),
    Output("platform-panel", "children"),
    Output("world-map", "figure"),
    Output("milestone-gauge", "figure"),
    Output("monthly-line", "figure"),
    Output("platform-bar", "figure"),
    Output("country-bar", "figure"),
    Output("unit-comparison", "figure"),
    Output("store-table", "children"),
    Output("country-table", "children"),
    Input("song-filter", "value"),
    Input("store-filter", "value"),
    Input("country-filter", "value"),
    Input("month-range", "value")
)
def update_dashboard(selected_song, selected_stores, selected_countries, selected_month_range):

    start_month_index = selected_month_range[0]
    end_month_index = selected_month_range[1]

    filtered = df[
        (df["title"] == selected_song) &
        (df["month_index"] >= start_month_index) &
        (df["month_index"] <= end_month_index)
    ].copy()

    if selected_stores:
        filtered = filtered[filtered["store"].isin(selected_stores)]

    if selected_countries:
        filtered = filtered[filtered["country"].isin(selected_countries)]

    total_streams = filtered["quantity"].sum()
    total_earnings = filtered["earnings"].sum()
    total_countries = filtered["country"].nunique()
    total_units = filtered["billboard_units"].sum()

    streams_to_500k = max(first_milestone - total_streams, 0)

    selected_start_month = index_to_month[start_month_index]
    selected_end_month = index_to_month[end_month_index]

    cards = [
        summary_card("Total Streams", f"{total_streams:,.0f}", f"{selected_start_month} through {selected_end_month}"),
        summary_card("Estimated Billboard Units", f"{total_units:,.1f}", "Streams converted to estimated units"),
        summary_card("Total Earnings", f"${total_earnings:,.2f}", "Based on selected filters"),
        summary_card("Countries Reached", f"{total_countries}", f"{streams_to_500k:,.0f} streams away from 500K")
    ]

    platform_summary = (
        filtered.groupby("store")
        .agg(
            streams=("quantity", "sum"),
            earnings=("earnings", "sum"),
            units=("billboard_units", "sum")
        )
        .reset_index()
        .sort_values("streams", ascending=False)
    )

    top_platforms = platform_summary.head(10)
    top_platform_snapshot = platform_summary.head(5)

    country_summary = (
        filtered.groupby(["country", "country_code", "iso_alpha"], dropna=False)
        .agg(
            streams=("quantity", "sum"),
            earnings=("earnings", "sum"),
            units=("billboard_units", "sum")
        )
        .reset_index()
        .sort_values("streams", ascending=False)
    )

    country_map_data = country_summary.dropna(subset=["iso_alpha"]).copy()
    country_map_data["log_streams"] = np.log10(country_map_data["streams"] + 1)

    top_countries = country_summary.head(10)

    platform_icons = {
        "Spotify": "🟢",
        "Apple Music": "🍎",
        "YouTube (Ads)": "▶️",
        "Amazon Music": "🛒",
        "TikTok": "🎵",
        "YouTube (ContentID)": "▶️",
        "Youtube Shorts Composition": "▶️",
        "YouTube (Audio)": "▶️"
    }

    platform_panel = [
        html.H3("Top Platform Snapshot", style={"marginTop": "0", "color": BRONCOS_NAVY}),
        html.P("Showing top 5 platforms by streams.", style={"color": "#6b7280"})
    ]

    for _, row in top_platform_snapshot.iterrows():
        platform_panel.append(
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "padding": "12px",
                    "border": f"1px solid {BRONCOS_NAVY}",
                    "borderRadius": "14px",
                    "marginBottom": "8px",
                    "backgroundColor": "#f9fafb"
                },
                children=[
                    html.Div([
                        html.Div(
                            f"{platform_icons.get(row['store'], '🎧')} {row['store']}",
                            style={"fontWeight": "800", "color": BRONCOS_NAVY}
                        ),
                        html.Div(
                            f"${row['earnings']:,.2f} earnings",
                            style={"fontSize": "13px", "color": "#6b7280"}
                        )
                    ]),
                    html.Div(
                        f"{row['streams']:,.0f}",
                        style={"fontWeight": "900", "fontSize": "18px", "color": BRONCOS_ORANGE}
                    )
                ]
            )
        )

    map_fig = px.choropleth(
        country_map_data,
        locations="iso_alpha",
        color="log_streams",
        hover_name="country",
        custom_data=[
            "iso_alpha",
            "streams",
            "earnings",
            "units",
            "log_streams"
        ],
        labels={
            "log_streams": "Log Color Scale"
        },
        color_continuous_scale=["#dbeafe", "#FB4F14", "#002244"],
        title="Global streams by country"
    )

    map_fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>"
            "ISO Code: %{customdata[0]}<br>"
            "Streams: %{customdata[1]:,}<br>"
            "Earnings: $%{customdata[2]:,.2f}<br>"
            "Estimated Units: %{customdata[3]:,.2f}<br>"
            "Log Streams: %{customdata[4]:.3f}"
            "<extra></extra>"
        )
    )

    map_fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_font_color=BRONCOS_NAVY,
        geo=dict(
            showframe=True,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_color=BRONCOS_NAVY,
            bordercolor=BRONCOS_ORANGE
        )
    )

    gauge_fig = go.Figure()

    gauge_fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=total_streams,
            delta={"reference": first_milestone},
            title={"text": "Streams Toward 1 Million"},
            gauge={
                "axis": {"range": [0, second_milestone]},
                "bar": {"color": BRONCOS_ORANGE, "thickness": 0.35},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": BRONCOS_NAVY,
                "steps": [
                    {"range": [0, first_milestone], "color": "#e5e7eb"},
                    {"range": [first_milestone, second_milestone], "color": "#dbeafe"}
                ],
                "threshold": {
                    "line": {"color": BRONCOS_NAVY, "width": 5},
                    "thickness": 0.75,
                    "value": first_milestone
                }
            }
        )
    )

    gauge_fig.update_layout(
        height=320,
        margin={"r": 30, "t": 60, "l": 30, "b": 20},
        paper_bgcolor="white",
        font={"color": BRONCOS_NAVY}
    )

    monthly = (
        filtered.groupby("sale_month")
        .agg(streams=("quantity", "sum"))
        .reset_index()
        .sort_values("sale_month")
    )

    monthly_fig = px.line(
        monthly,
        x="sale_month",
        y="streams",
        markers=True,
        title="Streams by Sale Month"
    )

    monthly_fig.update_traces(
        line_color=BRONCOS_ORANGE,
        line_width=4,
        marker_size=10,
        marker_color=BRONCOS_NAVY,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Streams: %{y:,}"
            "<extra></extra>"
        )
    )
    monthly_fig = clean_chart_layout(monthly_fig)

    platform_bar_fig = px.bar(
        top_platforms.sort_values("streams", ascending=True),
        x="streams",
        y="store",
        orientation="h",
        text="streams",
        title="Top 10 Platforms by Streams"
    )

    platform_bar_fig.update_traces(
        marker_color=BRONCOS_ORANGE,
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Streams: %{x:,}"
            "<extra></extra>"
        )
    )
    platform_bar_fig = clean_chart_layout(platform_bar_fig)

    country_bar_fig = px.bar(
        top_countries.sort_values("streams", ascending=True),
        x="streams",
        y="country",
        orientation="h",
        text="streams",
        title="Top 10 Countries by Streams"
    )

    country_bar_fig.update_traces(
        marker_color=BRONCOS_NAVY,
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Streams: %{x:,}"
            "<extra></extra>"
        )
    )
    country_bar_fig = clean_chart_layout(country_bar_fig)

    unit_fig = go.Figure()

    unit_fig.add_trace(
        go.Bar(
            x=top_platforms["store"],
            y=top_platforms["streams"],
            name="Streams",
            marker_color=BRONCOS_ORANGE,
            customdata=top_platforms[["units"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Streams: %{y:,}<br>"
                "Billboard Units: %{customdata[0]:,.2f}"
                "<extra></extra>"
            )
        )
    )

    unit_fig.add_trace(
        go.Bar(
            x=top_platforms["store"],
            y=top_platforms["units"],
            name="Estimated Billboard Units",
            marker_color=BRONCOS_NAVY,
            customdata=top_platforms[["streams"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Billboard Units: %{y:,.2f}<br>"
                "Streams: %{customdata[0]:,}"
                "<extra></extra>"
            )
        )
    )

    unit_fig.update_layout(
        barmode="group",
        title="Top 10 Streams vs Estimated Billboard Units"
    )
    unit_fig = clean_chart_layout(unit_fig)

    store_table_data = platform_summary.copy()
    store_table_data["streams"] = store_table_data["streams"].round(0)
    store_table_data["earnings"] = store_table_data["earnings"].round(2)
    store_table_data["units"] = store_table_data["units"].round(2)

    country_table_data = country_summary.copy()
    country_table_data["streams"] = country_table_data["streams"].round(0)
    country_table_data["earnings"] = country_table_data["earnings"].round(2)
    country_table_data["units"] = country_table_data["units"].round(2)
    country_table_data = country_table_data.drop(columns=["iso_alpha"])

    table_style = data_table_style()

    store_table = dash_table.DataTable(
        data=store_table_data.to_dict("records"),
        columns=[
            {"name": "Store", "id": "store"},
            {"name": "Streams", "id": "streams", "type": "numeric"},
            {"name": "Earnings", "id": "earnings", "type": "numeric"},
            {"name": "Estimated Units", "id": "units", "type": "numeric"}
        ],
        page_size=10,
        sort_action="native",
        filter_action="native",
        export_format="csv",
        **table_style
    )

    country_table = dash_table.DataTable(
        data=country_table_data.to_dict("records"),
        columns=[
            {"name": "Country", "id": "country"},
            {"name": "Code", "id": "country_code"},
            {"name": "Streams", "id": "streams", "type": "numeric"},
            {"name": "Earnings", "id": "earnings", "type": "numeric"},
            {"name": "Estimated Units", "id": "units", "type": "numeric"}
        ],
        page_size=10,
        sort_action="native",
        filter_action="native",
        export_format="csv",
        **table_style
    )

    return (
        cards,
        platform_panel,
        map_fig,
        gauge_fig,
        monthly_fig,
        platform_bar_fig,
        country_bar_fig,
        unit_fig,
        store_table,
        country_table
    )

if __name__ == "__main__":
    app.run(debug=True)