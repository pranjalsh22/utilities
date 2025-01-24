import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def read_file(uploaded_file):
    try:
        if st.checkbox("small space is seperating criteria"):
            return pd.read_csv(uploaded_file, delim_whitespace=True)
        else:
            return pd.read_csv(uploaded_file)
    except:
        st.error("Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).")
        return None

def plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range):
    x_data = data[x_column]
    y_data = data[y_column]
    
    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')

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

def main():
    st.title("Interactive Data Plotting with Streamlit")
    uploaded_file = st.file_uploader("Upload your data file")

    if uploaded_file is not None:
        pd.set_option('display.float_format', '{:e}'.format)
        data = read_file(uploaded_file)
        
        if data is not None:
            st.subheader("Data Preview")
            st.write(data)
            columns = data.columns.tolist()

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

            if st.button("Plot Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(data, x_column, y_column, x_log_scale, y_log_scale, x_range, y_range)

if __name__ == "__main__":
    main()
