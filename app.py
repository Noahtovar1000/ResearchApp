import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

df = pd.read_csv('C:\\Users\\Noah Tovar\\Downloads\\Copy of 2021-2024 Products Team Customers by Item and Ship To.csv')
st.set_page_config(layout='wide')
st.markdown('<style>div.block-container{padding-top:1rem}</style>', unsafe_allow_html=True)
image = Image.open(r'C:\Users\Noah Tovar\Downloads\Phokus_Logo.jpg')


col1, col2 = st.columns([0.1,0.9])
with col1:
    st.image(image,width=300)

html_title = """
    <style>
    .title-test{
    font-weight:bold;
    padding:20px;
    border-radius:7px
    }
    </style>
    <center><h1 class = "title-test"> Phokus Research Interactive Dashboard</h1></center>"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)

col3, col4, col5 =st.columns([0.1,0.45,0.45])
with col3:
    box_date = str(datetime.datetime.now().strftime('%d %B %Y'))
    st.write(f'Last Updated by:     \n {box_date}')
    #--------------------------------Making Purchase By Month Graph -------------------------------------------------------------------------------------

with col4:
    purchase_categories = df['Vertical'].dropna().unique()
df['Ship Date'] = pd.to_datetime(df['Ship Date'])
df['Month'] = df['Ship Date'].dt.to_period('M').dt.to_timestamp()

download_data = pd.DataFrame()

fig = go.Figure()
for category in purchase_categories:
    temp_df = df[(df['Vertical'] == category) & (df['Ship Date'].dt.year == 2024)]
    monthly_count = temp_df.groupby('Month').size().reset_index(name='Purchase Count')
    monthly_count['Category'] = category
    download_data = pd.concat([download_data, monthly_count], ignore_index=True)

    fig.add_trace(go.Scatter(
        x=monthly_count['Month'],
        y=monthly_count['Purchase Count'],
        mode='lines+markers',
        name=category,
        visible=(category == purchase_categories[0])
    ))

dropdown_buttons = [
    dict(label=cat,
         method='update',
         args=[{'visible': [cat == c for c in purchase_categories]},
               {'title': f'Purchase Quantity by Month (2024) - {cat}'}])
    for cat in purchase_categories
]

fig.update_layout(
    title=f'Purchases by Month (2024) - {purchase_categories[0]}',
    xaxis_title='Month',
    yaxis_title='Purchase Count',
    updatemenus=[{
        'buttons': dropdown_buttons,
        'direction': 'down',
        'showactive': True
    }],
    template='plotly_white'
)

# Display chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

csv_data = download_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Line Chart Data",
    data=csv_data,
    file_name="purchase_quantity_by_month.csv",
    mime="text/csv"
)
st.divider()
#--------------------------------------------------Making table that gives purchases by category---------------------------------------------------------

_, view1, dwn1, view2, dwn2 = st.columns([0.15, 0.7, 0.20, 0.20, 0.20])


# -- Inside your layout --
_, view1, dwn1, view2, dwn2 = st.columns([0.1, 0.7, 0.20, 0.20, 0.20])

with view1:
    # Prepare data for charting
    data = pd.crosstab(df['Vertical'], df['Product Category (PC)'])
    chart_data = data.drop(index='Grand Total', errors='ignore').drop(columns='Total', errors='ignore')
    chart_data = chart_data.reset_index().melt(id_vars='Vertical', var_name='Product Category', value_name='Quantity')

    # Create horizontal stacked bar chart
    bar_fig = px.bar(
        chart_data,
        y='Vertical',
        x='Quantity',
        color='Product Category',
        title='Product Categories Purchased per Buyer',
        labels={'Quantity': 'Purchase Count'},
        barmode='stack',
        orientation='h',
        height=700,
        width=1200
    )

    st.plotly_chart(bar_fig, use_container_width=True)

# -- Download button moved here, after chart --
 # Optional visual break

csv = chart_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Stacked Bar Chart Data",
    data=csv,
    file_name="stacked_bar_chart_data.csv",
    mime="text/csv"
)

st.divider()

#---------------------------------------------Making graph by purchase amount-------------------------------------------

with col5:
    # Clean up the data
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
df['Month'] = df['Ship Date'].dt.to_period('M').dt.to_timestamp()
df['Amount $$'] = (
    df['Amount $$']
    .astype(str)
    .str.replace(r'[^\d.]', '', regex=True)
)
df['Amount $$'] = pd.to_numeric(df['Amount $$'], errors='coerce')

# Get unique categories
purchase_categories = df['Vertical'].dropna().unique()

# Create the figure
fig = go.Figure()

# Create a DataFrame to collect data for download
download_price_data = pd.DataFrame()

# Add a trace for each category
for category in purchase_categories:
    temp_df = df[(df['Vertical'] == category) & (df['Ship Date'].dt.year == 2024)]
    
    monthly_price = temp_df.groupby('Month')['Amount $$'].mean().round(2).reset_index(name='Purchase Price')
    monthly_price['Category'] = category  # Add category to track
    
    download_price_data = pd.concat([download_price_data, monthly_price], ignore_index=True)

    fig.add_trace(go.Scatter(
        x=monthly_price['Month'],
        y=monthly_price['Purchase Price'],
        mode='lines+markers',
        name=category,
        visible=(category == purchase_categories[0])
    ))

# Create dropdown buttons for each category
dropdown_buttons = [
    dict(label=cat,
         method='update',
         args=[{'visible': [cat == c for c in purchase_categories]},
               {'title': f'Purchase Price by Month (2024) - {cat}'}])
    for cat in purchase_categories
]

# Update layout
fig.update_layout(
    title=f'Purchase Price by Month (2024) - {purchase_categories[0]}',
    xaxis_title='Month',
    yaxis_title='Average Purchase Price ($)',
    updatemenus=[{
        'buttons': dropdown_buttons,
        'direction': 'down',
        'showactive': True
    }],
    template='plotly_white'
)

# Show chart
st.plotly_chart(fig, use_container_width=True)

# ✅ Add download button for price data
csv_price_data = download_price_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Purchase Price Data",
    data=csv_price_data,
    file_name="purchase_price_by_month.csv",
    mime="text/csv"
)

st.divider()

#-------------------------------Pie Chart----------------------------------------------------------

fig3 = df.groupby('Vertical')['Amount $$'].sum().reset_index()

fig = px.pie(
    fig3,
    names='Vertical',
    values='Amount $$',
    title='Total Purchase Amount by Group'
)
fig.update_traces(textinfo='percent+label')

# Show the pie chart once (inside a column)
_, col6 = st.columns([0.1, 1])
with col6:
    st.plotly_chart(fig, use_container_width=True)

# Add a download button for the pie chart data
csv_pie_data = fig3.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Pie Chart Data",
    data=csv_pie_data,
    file_name="total_purchase_amount_by_group.csv",
    mime="text/csv"
)