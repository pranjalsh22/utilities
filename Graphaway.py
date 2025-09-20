import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid

def read_file(uploaded_file):
    try:
        if st.checkbox("Small space is separating criteria"):
            df = pd.read_csv(uploaded_file, delim_whitespace=True, engine='python')
        else:
            df = pd.read_csv(uploaded_file, engine='python')

        # Ensure all object columns are converted to numeric where possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Unsupported file format. Please upload a valid CSV file with tabular data.\nError: {e}")
        return None

def plot_graph(data, x_column, y_columns, color_groups, pattern_groups, 
               color_labels, pattern_labels, x_log_scale, y_log_scale, x_range, y_range, 
               title, x_label, y_label,
               font_sizes, marker_style, marker_size, show_legend, legend_title):

    plt.figure(figsize=(10, 6))

    pattern_styles = {
        'solid': '-',
        'dotted': ':',
        'dashed': '--',
        'dashdot': '-.'
    }

    # Assign colors
    color_idx = 0
    column_colors, column_labels = {}, {}
    for idx, group in enumerate(color_groups):
        color = plt.cm.tab10(color_idx % 10)
        color_idx += 1
        label = color_labels[idx] if color_labels and idx < len(color_labels) else f"Group {idx+1}"
        for col in group:
            column_colors[col] = color
            column_labels[col] = label

    # Assign patterns
    column_linestyles, column_pattern_labels = {}, {}
    for idx, group in enumerate(pattern_groups):
        label = f"Pattern {idx+1}"
        style = '-'
        if pattern_labels and idx < len(pattern_labels):
            label, style_key = pattern_labels[idx]
            style = pattern_styles.get(style_key, '-')
        for col in group:
            column_linestyles[col] = style
            column_pattern_labels[col] = label

    used_labels = set()

    # Plot each Y-column
    for col in y_columns:
        color = column_colors.get(col, plt.cm.tab10(color_idx % 10))
        if col not in column_colors:
            color_idx += 1
        linestyle = column_linestyles.get(col, '-')
        label = column_labels.get(col) or column_pattern_labels.get(col) or col

        if label not in used_labels:
            plt.plot(
                data[x_column], data[col],
                marker=marker_style, markersize=marker_size,
                linestyle=linestyle, color=color, label=label
            )
            used_labels.add(label)
        else:
            plt.plot(
                data[x_column], data[col],
                marker=marker_style, markersize=marker_size,
                linestyle=linestyle, color=color
            )

    # Legend control
    if show_legend:
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(
            by_label.values(), by_label.keys(),
            title=legend_title, fontsize=font_sizes["legend"], title_fontsize=font_sizes["legend"]
        )

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    # Font sizes
    plt.title(title, fontsize=font_sizes["title"])
    plt.xlabel(x_label, fontsize=font_sizes["labels"])
    plt.ylabel(y_label, fontsize=font_sizes["labels"])
    plt.tick_params(axis='both', labelsize=font_sizes["ticks"])
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def linegraph():
    st.title("📈 Line Graph Plotting Tool")
    uploaded_file = st.file_uploader("📤 Upload your data file", key="linegraph")

    if uploaded_file is not None:
        data = read_file(uploaded_file)

        if data is not None:
            st.subheader("🔍 Data Preview")
            st.dataframe(data)
            columns = data.columns.tolist()

            st.markdown("### ✏️ Axis Configuration")
            x_column = st.selectbox("Select **X-axis column**", columns)
            y_columns = st.multiselect("Select **Y-axis columns**", columns, default=[columns[1]])

            # -----------------------------------------
            # 🔹 Initialize variables (avoid NameError)
            color_groups, color_labels = [], []
            pattern_groups, pattern_labels = [], []
            x_range_min, x_range_max = None, None
            y_range_min, y_range_max = None, None
            x_log_scale, y_log_scale = False, False
            # -----------------------------------------

            st.sidebar.header("📝 Labels & Title")
            title = st.sidebar.text_input("Graph Title", f'Multiple Curves: Y vs {x_column}')
            x_axis_label = st.sidebar.text_input("X-axis Label", x_column)
            y_axis_label = st.sidebar.text_input("Y-axis Label", "Y Values")

            # 🎨 Style & Appearance
            with st.sidebar.expander("🎨 Style & Appearance", expanded=True):
                font_sizes = {
                    "title": st.number_input("Title font size", value=16),
                    "labels": st.number_input("Axis labels font size", value=14),
                    "ticks": st.number_input("Tick labels font size", value=12),
                    "legend": st.number_input("Legend font size", value=12)
                }
                marker_style = st.selectbox("Marker style", ["o", "s", "D", "^", "v", "x", "+", None])
                marker_size = st.number_input("Marker size", value=6)
                show_legend = st.checkbox("Show legend?", value=True)
                legend_title = st.text_input("Legend title", "Legend")

            # Axis scales & ranges
            with st.expander("📐 Axis Scale & Range", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    x_log_scale = st.checkbox("Log scale for X-axis", value=False)
                    x_data = pd.to_numeric(data[x_column], errors='coerce').dropna()
                    x_range_min = st.number_input(
                        f"X-axis {x_column} min", value=float(x_data.min())
                    )
                    x_range_max = st.number_input(
                        f"X-axis {x_column} max", value=float(x_data.max())
                    )
                with col2:
                    y_log_scale = st.checkbox("Log scale for Y-axis", value=False)
                    y_data_first = pd.to_numeric(data[y_columns[0]], errors='coerce').dropna()
                    y_range_min = st.number_input(
                        "Y-axis min", value=float(y_data_first.min())
                    )
                    y_range_max = st.number_input(
                        "Y-axis max", value=float(y_data_first.max())
                    )

            if st.button("📊 Plot Line Graph"):
                # ✅ Fallback in case user didn’t adjust range
                if x_range_min is None or x_range_max is None:
                    x_range = None
                else:
                    x_range = (x_range_min, x_range_max)

                if y_range_min is None or y_range_max is None:
                    y_range = None
                else:
                    y_range = (y_range_min, y_range_max)

                if not color_groups:
                    color_groups = [[col] for col in y_columns]
                    color_labels = y_columns

                plot_graph(
                    data, x_column, y_columns,
                    color_groups, pattern_groups,
                    color_labels, pattern_labels,
                    x_log_scale, y_log_scale,
                    x_range, y_range,
                    title, x_axis_label, y_axis_label,
                    font_sizes, marker_style, marker_size,
                    show_legend, legend_title
                )

def integrate_curve(x_data, y_data, log_x=False, log_y=False, method='trapezoid'):
    if log_x:
        x_data = np.power(10, x_data)
    if log_y:
        y_data = np.power(10, y_data)

    n = len(x_data)

    if method == 'trapezoid':
        return trapezoid(y_data, x_data)
    elif method == 'Simpson 1/3':
        if n < 3:
            return "❌ Simpson's 1/3 rule requires at least 3 points."
        if (n - 1) % 2 != 0:
            return "❌ Simpson's 1/3 rule needs an even number of intervals (odd number of points)."
        return simpson(y_data, x_data)
    elif method == 'Simpson 3/8':
        if n < 4:
            return "❌ Simpson's 3/8 rule requires at least 4 points."
        if (n - 1) % 3 != 0:
            return "❌ Simpson's 3/8 rule requires number of intervals to be a multiple of 3."
        h = (x_data[-1] - x_data[0]) / (n - 1)
        result = y_data[0] + y_data[-1]
        for i in range(1, n - 1):
            result += 3 * y_data[i] if i % 3 != 0 else 2 * y_data[i]
        return (3 * h / 8) * result
    else:
        return "❌ Unknown method selected."

def plot_pie_chart():
    st.title("🥧 Pie Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="piechart")

    if uploaded_file is not None:
        data = read_file(uploaded_file)
        if data is not None:
            st.subheader("Data Preview")
            st.write(data)

            column = st.selectbox("Select a column for the pie chart", data.columns)

            fig, ax = plt.subplots()
            data[column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_title(f"Pie Chart of {column}")
            st.pyplot(fig)

def plot_bar_chart():
    st.title("📊 Bar Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="barchart")

    if uploaded_file is not None:
        data = read_file(uploaded_file)
        if data is not None:
            st.subheader("Data Preview")
            st.write(data)

            columns = data.columns.tolist()
            x_column = st.selectbox("Select X-axis column", columns)
            y_column = st.selectbox("Select Y-axis column", columns, index=1)

            use_labels = st.checkbox("Use custom labels from a column?")
            if use_labels:
                label_column = st.selectbox("Select column for labels", columns)
                labels = data[label_column].astype(str)
            else:
                labels = data[x_column].astype(str)

            fig, ax = plt.subplots()
            ax.bar(labels, data[y_column])
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            ax.set_title(f"Bar Chart: {y_column} vs {x_column}")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

def main():
    st.sidebar.title("Visualization Tools")
    option = st.sidebar.selectbox("Choose a tool", 
                                  ["Line Graph Plot", "Pie Chart", "Bar Chart"])

    if option == "Line Graph Plot":
        linegraph()
    elif option == "Pie Chart":
        plot_pie_chart()
    elif option == "Bar Chart":
        plot_bar_chart()

if __name__ == "__main__":
    main()
