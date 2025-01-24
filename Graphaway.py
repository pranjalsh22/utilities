import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to read the input file
def read_file(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a file with tabular data.")
        return None

# Function to create the plot
def plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range):
    # Extract selected columns
    x_data = data[x_column]
    y_data = data[y_column]
    
    # Apply log scale if selected
    if x_log_scale:
        x_data = np.log10(x_data)
    if y_log_scale:
        y_data = np.log10(y_data)

    # Set the plot limits if provided
    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, marker='o', linestyle='-', color='b')
    
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f'Plot of {y_column} vs {x_column}')
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

# Streamlit app interface
def main():
    st.title("Interactive Data Plotting with Streamlit")

    # File upload
    uploaded_file = st.file_uploader("Upload your .txt or .csv file", type=["txt", "csv"])

    if uploaded_file is not None:
        # Read the file and display a preview
        data = read_file(uploaded_file)
        
        if data is not None:
            # Show the dataframe preview
            st.subheader("Data Preview")
            st.write(data.head())

            # Select columns for x and y axes
            columns = data.columns.tolist()

            # 2 Columns for selecting X and Y Axis
            col1, col2 = st.columns(2)

            with col1:
                x_column = st.selectbox("Select X-axis column", columns)
                x_log_scale = st.checkbox("Log scale for X-axis", value=False)
                x_range_min = st.number_input(f"X-axis {x_column} min", value=float(data[x_column].min()))
                x_range_max = st.number_input(f"X-axis {x_column} max", value=float(data[x_column].max()))

            with col2:
                y_column = st.selectbox("Select Y-axis column", columns)
                y_log_scale = st.checkbox("Log scale for Y-axis", value=False)
                y_range_min = st.number_input(f"Y-axis {y_column} min", value=float(data[y_column].min()))
                y_range_max = st.number_input(f"Y-axis {y_column} max", value=float(data[y_column].max()))

            # Plotting button
            if st.button("Plot Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                
                # Plot the graph
                plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range)

if __name__ == "__main__":
    main()
