import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

# Set up the page layout and title
st.set_page_config(layout="wide")
st.title("📉 Painting Stats Model")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")

# Process the uploaded file
if uploaded_file is not None:
    try:
        # Load the dataset from the specified sheet
        df = pd.read_excel(uploaded_file, sheet_name='Sheet1')

        # Display the uploaded data
        st.write("### Uploaded Data")
        st.dataframe(df)
        st.write("-----------------------------------")

        # Combine Width Measurements for Molding (C to E), Painting (G to I), PaintingWithoutOven (O to Q), and MoldingPlusOven (S to U)
        molding_data = df.iloc[:, 2:5].values.flatten()
        painting_data = df.iloc[:, 6:9].values.flatten()
        painting_without_oven_data = df.iloc[:, 14:17].values.flatten()
        molding_plus_oven_data = df.iloc[:, 18:21].values.flatten()

        # Handle NaN and infinity values
        def clean_data(data):
            data = data[~pd.isnull(data)]
            return data[np.isfinite(data)]

        molding_data = clean_data(molding_data)
        painting_data = clean_data(painting_data)
        painting_without_oven_data = clean_data(painting_without_oven_data)
        molding_plus_oven_data = clean_data(molding_plus_oven_data)

        # Function to create bell curve
        def create_bell_curve(data, title, lsl, usl):
            mean_value = data.mean()
            fig = ff.create_distplot([data], group_labels=[title], bin_size=0.05)
            fig.add_vline(x=lsl, line=dict(color='red', dash='dash'), annotation_text=f'LSL ({lsl})')
            fig.add_vline(x=usl, line=dict(color='red', dash='dash'), annotation_text=f'USL ({usl})')
            fig.add_vline(x=mean_value, line=dict(color='blue', dash='dash'), annotation_text=f'Mean ({mean_value:.2f})')
            return fig

        lsl = 81.2
        usl = 82.2

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        # Plot Molding bell curve
        with col1:
            st.write("### Molding Measurements")
            fig_molding = create_bell_curve(molding_data, 'Molding Measurements', lsl, usl)
            st.plotly_chart(fig_molding)

        # Plot Painting bell curve
        with col2:
            st.write("### Painting Measurements")
            fig_painting = create_bell_curve(painting_data, 'Painting Measurements', lsl, usl)
            st.plotly_chart(fig_painting)

        # Plot PaintingWithoutOven bell curve
        with col3:
            st.write("### PaintingWithoutOven Measurements")
            fig_painting_without_oven = create_bell_curve(painting_without_oven_data, 'PaintingWithoutOven Measurements', lsl, usl)
            st.plotly_chart(fig_painting_without_oven)

        # Plot MoldingPlusOven bell curve
        with col4:
            st.write("### MoldingPlusOven Measurements")
            fig_molding_plus_oven = create_bell_curve(molding_plus_oven_data, 'MoldingPlusOven Measurements', lsl, usl)
            st.plotly_chart(fig_molding_plus_oven)

        # Comparison between different part conditions
        st.write("### Comparison Between Different Part Conditions")

        part_conditions = (
            ['Molding'] * len(molding_data) + 
            ['Painting'] * len(painting_data) + 
            ['PaintingWithoutOven'] * len(painting_without_oven_data) + 
            ['MoldingPlusOven'] * len(molding_plus_oven_data)
        )
        measurements = np.concatenate([
            molding_data, 
            painting_data, 
            painting_without_oven_data, 
            molding_plus_oven_data
        ])

        comparison_data = {
            'Part Condition': part_conditions,
            'Measurement Value': measurements
        }
        df_comparison = pd.DataFrame(comparison_data)
        fig_comparison = px.box(df_comparison, x='Part Condition', y='Measurement Value', points="all")
        st.plotly_chart(fig_comparison)

    except Exception as e:
        st.error(f"Error: {e}")
