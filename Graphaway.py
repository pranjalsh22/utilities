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
            df = pd.read_csv(uploaded_file, engine='python')  # engine='python' is more forgiving with weird formats

        # Optional: ensure numeric columns interpret scientific notation
        for col in df.select_dtypes(include=['object']):
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except Exception:
                pass  # Skip columns that can't be converted

        return df
    except Exception as e:
        st.error(f"Unsupported file format. Please upload a valid CSV file with tabular data (comma or space-separated).\nError: {e}")
        return None

def plot_graph(data, x_column, y_columns, color_groups, pattern_groups, 
               color_labels, pattern_labels, x_log_scale, y_log_scale, x_range, y_range, 
               title, x_label, y_label):
    
    plt.figure(figsize=(10, 6))
    
    # Line style options
    pattern_styles = {
        'solid': '-',
        'dotted': ':',
        'dashed': '--',
        'dashdot': '-.'
    }

    used_labels = set()
    color_idx = 0

    # Plot color groups
    for idx, group in enumerate(color_groups):
        color = plt.cm.tab10(color_idx % 10)
        color_idx += 1
        label = color_labels[idx] if color_labels and idx < len(color_labels) else f"Color group {idx+1}"
        for col in group:
            if label not in used_labels:
                plt.plot(data[x_column], data[col], marker='o', linestyle='-', color=color, label=label)
                used_labels.add(label)
            else:
                plt.plot(data[x_column], data[col], marker='o', linestyle='-', color=color)

    # Plot pattern groups with same color logic but styled lines
    for idx, group in enumerate(pattern_groups):
        linestyle = '-'
        pattern_label = f"Pattern group {idx+1}"
        if pattern_labels and idx < len(pattern_labels):
            pattern_label, pattern_style_key = pattern_labels[idx]
            linestyle = pattern_styles.get(pattern_style_key, '-')
        
        color = plt.cm.tab10(color_idx % 10)
        color_idx += 1

        for col in group:
            if pattern_label not in used_labels:
                plt.plot(data[x_column], data[col], marker='o', linestyle=linestyle, color=color, label=pattern_label)
                used_labels.add(pattern_label)
            else:
                plt.plot(data[x_column], data[col], marker='o', linestyle=linestyle, color=color)

    # Remove duplicate legend entries
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), title="Legend")

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)


def is_probably_log(column_data):
    col = np.array(column_data)
    if np.any(col <= 0):
        return False
    if (np.min(col) > -10) and (np.max(col) < 10):
        return True
    return False

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

def linegraph():
    st.title("📈 Line Graph Plotting Tool")
    uploaded_file = st.file_uploader("📤 Upload your data file", key="linegraph")

    if uploaded_file is not None:
        data = read_file(uploaded_file)

        if data is not None:
            st.subheader("🔍 Data Preview")
            st.dataframe(data)

            columns = data.columns.tolist()

            # Axis configuration
            st.markdown("### ✏️ Axis Configuration")
            x_column = st.selectbox("Select **X-axis column**", columns)

            y_columns = st.multiselect("Select **Y-axis columns** (plotted together)", columns, default=[columns[1]])

            # Sidebar: Labels and Title
            st.sidebar.header("📝 Labels & Title")
            title = st.sidebar.text_input("Graph Title", f'Multiple Curves: Y vs {x_column}')
            x_axis_label = st.sidebar.text_input("X-axis Label", x_column)
            y_axis_label = st.sidebar.text_input("Y-axis Label", "Y Values")

            # Axis scale and range
            with st.expander("📐 Axis Scale & Range", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    x_log_detected = is_probably_log(data[x_column])
                    x_log_scale = st.checkbox("Log scale for X-axis", value=x_log_detected)
                    x_range_min = st.number_input(f"X-axis {x_column} min", value=float(data[x_column].min()), format="%.10e")
                    x_range_max = st.number_input(f"X-axis {x_column} max", value=float(data[x_column].max()), format="%.10e")
                with col2:
                    y_log_detected = all([is_probably_log(data[col]) for col in y_columns])
                    y_log_scale = st.checkbox("Log scale for Y-axis", value=y_log_detected)
                    y_range_min = st.number_input("Y-axis min", value=float(data[y_columns[0]].min()), format="%.10e")
                    y_range_max = st.number_input("Y-axis max", value=float(data[y_columns[0]].max()), format="%.10e")

            # 🎨 Color Groups
            with st.expander("🎨 Define Color Groups"):
                st.markdown("Create multiple color groups with same line style and different colors.")
                color_groups = []
                color_labels = []
                num_color_groups = st.number_input("Number of color groups", min_value=1, max_value=10, value=1)

                for i in range(num_color_groups):
                    cols = st.multiselect(f"Color Group {i+1} Columns", columns, key=f"color_group_{i}")
                    label = st.text_input(f"Label for Color Group {i+1}", key=f"color_label_{i}", value=f"Group {i+1}")
                    if cols:
                        color_groups.append(cols)
                        color_labels.append(label)

            # 🎚️ Pattern Groups
            with st.expander("🎚️ Define Pattern Groups"):
                st.markdown("Create multiple pattern groups (different line styles, black color).")
                st.markdown("Available patterns: `solid`, `dotted`, `dashed`, `dashdot`")
                pattern_styles_available = ['solid', 'dotted', 'dashed', 'dashdot']
                pattern_groups = []
                pattern_labels = []
                num_pattern_groups = st.number_input("Number of pattern groups", min_value=0, max_value=10, value=0)

                for i in range(num_pattern_groups):
                    cols = st.multiselect(f"Pattern Group {i+1} Columns", columns, key=f"pattern_group_{i}")
                    label = st.text_input(f"Label for Pattern Group {i+1}", key=f"pattern_label_{i}", value=f"Pattern {i+1}")
                    pattern = st.selectbox(f"Pattern Style for Group {i+1}", pattern_styles_available, key=f"pattern_style_{i}")
                    if cols:
                        pattern_groups.append(cols)
                        pattern_labels.append((label, pattern))

            if st.button("📊 Plot Line Graph"):
                x_range = (x_range_min, x_range_max)
                y_range = (y_range_min, y_range_max)
                plot_graph(
                    data, x_column, y_columns,
                    color_groups, pattern_groups,
                    color_labels, pattern_labels,
                    x_log_scale, y_log_scale,
                    x_range, y_range,
                    title, x_axis_label, y_axis_label
                )

            # 🧮 Integration
            with st.expander("🧮 Integration (Area under the Curve)"):
                st.markdown(f"**Auto-detected:** X-axis log scale: `{x_log_detected}`, Y-axis log scale: `{y_log_detected}`")
                override_log_x = st.checkbox("Override X-axis as log scale", value=x_log_scale)
                override_log_y = st.checkbox("Override Y-axis as log scale", value=y_log_scale)
                method = st.selectbox("Select method", ["trapezoid", "Simpson 1/3", "Simpson 3/8"])

                if st.button("➕ Calculate Integral"):
                    if len(y_columns) != 1:
                        st.warning("Please select **only one** Y-axis column for integration.")
                    else:
                        x_vals = data[x_column].values
                        y_vals = data[y_columns[0]].values
                        result = integrate_curve(x_vals, y_vals, log_x=override_log_x, log_y=override_log_y, method=method)
                        if isinstance(result, str) and result.startswith("❌"):
                            st.error(result)
                        else:
                            st.success(f"✅ Integral using {method}: `{result:.4E}`")

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
            ax.set_title(f'Bar Chart of {y_column} vs {x_column}')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

# ---------------- Main App ------------------
choice = st.selectbox("📌 Choose a graph type", ["Line Graph", "Pie Chart", "Bar Graph"])

if choice == "Line Graph":
    linegraph()
elif choice == "Pie Chart":
    plot_pie_chart()
elif choice == "Bar Graph":
    plot_bar_chart()
