import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import simpson, trapezoid

# ------------------ Utilities ------------------
spectral_regions = [
    ("Radio", 0, 3e9, "lightblue"),
    ("Microwave", 3e9, 3e12, "lightgreen"),
    ("Infrared", 3e12, 2.99e14, "lightcoral"),
    ("Visible", 3.01e14, 7.5e14, "khaki"),
    ("UV", 7.5e14, 3e16, "violet"),
    ("X-ray", 3e16, 3e19, "orange"),
    ("Gamma-ray", 3e19, 3e30, "red")
]

def read_file(uploaded_file):
    try:
        if st.checkbox("Its a TXT file"):
            df = pd.read_csv(uploaded_file, delim_whitespace=True, engine='python')
        else:
            df = pd.read_csv(uploaded_file, engine='python')

        # Ensure numeric conversion
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Unsupported file format. Please upload a valid CSV file.\nError: {e}")
        return None

def plot_graph(data, x_column, y_columns, color_groups, pattern_groups, bullet_groups,
               color_labels, pattern_labels, bullet_labels,
               x_log_scale, y_log_scale, x_range, y_range, 
               title, x_label, y_label, font_sizes, marker_size, show_background=False):

    plt.figure(figsize=(10, 6))
    pattern_styles = {'solid': '-', 'dotted': ':', 'dashed': '--', 'dashdot': '-.'}
    marker_styles_available = ['o', 's', '^', 'D', '*', '+', 'x']

    # --- Background spectral regions ---
    if show_background and y_range:
        for label, x_min, x_max, color in spectral_regions:
            plt.fill_between(
                [x_min, x_max], [y_range[0]]*2, [y_range[1]]*2,
                color=color, alpha=0.2, label=label
            )

    # ------------------ Colors ------------------
    color_idx = 0
    column_colors, column_labels = {}, {}
    for idx, group in enumerate(color_groups):
        color = plt.cm.tab10(color_idx % 10)
        color_idx += 1
        label = color_labels[idx] if color_labels and idx < len(color_labels) else f"Group {idx+1}"
        for col in group:
            column_colors[col] = color
            column_labels[col] = label

    # ------------------ Patterns ------------------
    column_linestyles, column_pattern_labels = {}, {}
    for idx, group in enumerate(pattern_groups):
        style = '-'
        label = f"Pattern {idx+1}"
        if pattern_labels and idx < len(pattern_labels):
            label, style_key = pattern_labels[idx]
            style = pattern_styles.get(style_key, '-')
        for col in group:
            column_linestyles[col] = style
            column_pattern_labels[col] = label

    # ------------------ Markers ------------------
    column_markers, column_marker_labels = {}, {}
    for idx, group in enumerate(bullet_groups):
        marker = 'o'
        label = f"Bullet {idx+1}"
        if bullet_labels and idx < len(bullet_labels):
            label, marker = bullet_labels[idx]
        for col in group:
            column_markers[col] = marker
            column_marker_labels[col] = label

    used_labels = set()

    for col in y_columns:
        color = column_colors.get(col, plt.cm.tab10(color_idx % 10))
        if col not in column_colors:
            color_idx += 1
        linestyle = column_linestyles.get(col, '-')
        marker = column_markers.get(col, 'o')
        label = column_labels.get(col) or column_pattern_labels.get(col) or column_marker_labels.get(col) or col

        if label not in used_labels:
            plt.plot(data[x_column], data[col], marker=marker, markersize=marker_size,
                     linestyle=linestyle, color=color, label=label)
            used_labels.add(label)
        else:
            plt.plot(data[x_column], data[col], marker=marker, markersize=marker_size,
                     linestyle=linestyle, color=color)

    if x_log_scale:
        plt.xscale('log')
    if y_log_scale:
        plt.yscale('log')
    if x_range:
        plt.xlim(x_range)
    if y_range:
        plt.ylim(y_range)
    
        
    plt.title(title, fontsize=font_sizes.get("title", 16))
    plt.xlabel(x_label, fontsize=font_sizes.get("labels", 14))
    plt.ylabel(y_label, fontsize=font_sizes.get("labels", 14))
    plt.xticks(fontsize=font_sizes.get("ticks", 12))
    plt.yticks(fontsize=font_sizes.get("ticks", 12))
    plt.grid(True)
    if show_legend:
        plt.legend(title="Legend", fontsize=font_sizes.get("legend", 12))    
    plt.tight_layout()
    st.pyplot(plt)


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
            return "❌ Simpson's 1/3 rule requires an odd number of points."
        return simpson(y_data, x_data)
    elif method == 'Simpson 3/8':
        if n < 4:
            return "❌ Simpson's 3/8 rule requires at least 4 points."
        if (n - 1) % 3 != 0:
            return "❌ Simpson's 3/8 rule requires intervals multiple of 3."
        h = (x_data[-1] - x_data[0]) / (n - 1)
        result = y_data[0] + y_data[-1]
        for i in range(1, n-1):
            result += 3*y_data[i] if i % 3 != 0 else 2*y_data[i]
        return (3*h/8) * result
    else:
        return "❌ Unknown method selected."

# ------------------ Line Graph ------------------

def linegraph():
    st.title("📈 Line Graph Plotting Tool")
    st.write("Upload file to explore more features")
    st.link_button("Download sample data files","https://drive.google.com/drive/folders/12_u23IiQ-Xoi9yG2Sk_FNwD0akuUgpyH?usp=share_link")
    uploaded_file = st.file_uploader("📤 Upload your data file", key="linegraph")
#----------youtube tutorial--------
    st.markdown(
        """
        <a href="https://m.youtube.com/watch?v=aGHeqNbDjW8" style="
            text-decoration:none;
            display:inline-flex;
            align-items:center;
            background:#ff0000;
            color:white;
            padding:10px 16px;
            border-radius:12px;
            font-size:18px;
            font-weight:600;">
            
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/2560px-YouTube_full-color_icon_%282017%29.svg.png"
                 width="24" style="margin-right:10px;">
            YouTube
        </a>
        """,
        unsafe_allow_html=True
    )
#----------------------------------
    if uploaded_file is not None:
        data = read_file(uploaded_file)
        if data is None:
            return

        st.subheader("🔍 Data Preview")
        st.dataframe(data)

        columns = data.columns.tolist()
        x_column = st.selectbox("Select X-axis column", columns)
        y_columns = st.multiselect("Select Y-axis columns", columns, default=[columns[1]])

        st.sidebar.header("📝 Labels & Title")
        title = st.sidebar.text_input("Graph Title", f"Multiple Curves: Y vs {x_column}")
        x_axis_label = st.sidebar.text_input("X-axis Label", x_column)
        y_axis_label = st.sidebar.text_input("Y-axis Label", "Y Values")

        # ------------------ Sidebar customization ------------------
        st.sidebar.header("🖊️ Graph Styling")
        marker_size = st.sidebar.number_input("Marker size", min_value=0, max_value=20, value=6)
        font_sizes = {
            "title": st.sidebar.number_input("Title font size", value=16),
            "labels": st.sidebar.number_input("Axis labels font size", value=14),
            "ticks": st.sidebar.number_input("Ticks font size", value=12),
            "legend": st.sidebar.number_input("Legend font size", value=12)
        }
        # In the sidebar / settings section
        global show_legend
        show_legend = st.sidebar.checkbox("Show Legend", value=True)

        # ------------------ Bullet groups ------------------
        with st.expander("🔹 Bullet (Marker) Groups"):
            marker_styles_available = ['o', 's', '^', 'D', '*', '+', 'x']
            bullet_groups, bullet_labels = [], []
            num_bullet_groups = st.number_input("Number of bullet groups", min_value=0, max_value=10, value=0)
            for i in range(num_bullet_groups):
                cols = st.multiselect(f"Bullet Group {i+1} Columns", columns, key=f"bullet_group_{i}")
                label = st.text_input(f"Label for Bullet Group {i+1}", key=f"bullet_label_{i}", value=f"Bullet {i+1}")
                marker = st.selectbox(f"Marker style for Group {i+1}", marker_styles_available, key=f"bullet_marker_{i}")
                if cols:
                    bullet_groups.append(cols)
                    bullet_labels.append((label, marker))

        # ------------------ Axis Range Inputs ------------------
        with st.expander("📐 Axis Scale & Range", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                x_log_scale = st.checkbox("Log scale X-axis", value=False)
                x_min_str = st.text_input("X-axis min", value=str(data[x_column].min()))
                x_max_str = st.text_input("X-axis max", value=str(data[x_column].max()))
            with col2:
                y_log_scale = st.checkbox("Log scale Y-axis", value=False)
                y_min_str = st.text_input("Y-axis min", value=str(data[y_columns[0]].min()))
                y_max_str = st.text_input("Y-axis max", value=str(data[y_columns[0]].max()))

        try:
            x_range = (float(x_min_str), float(x_max_str))
            y_range = (float(y_min_str), float(y_max_str))
        except ValueError:
            st.error("Invalid axis range values. Use numeric or scientific notation (e.g., 1e-5).")
            st.stop()

        # ------------------ Color & Pattern Groups ------------------
        with st.expander("🎨 Color Groups"):
            color_groups, color_labels = [], []
            num_color_groups = st.number_input("Number of color groups", min_value=1, max_value=10, value=1)
            for i in range(num_color_groups):
                cols = st.multiselect(f"Color Group {i+1} Columns", columns, key=f"color_group_{i}")
                label = st.text_input(f"Label for Color Group {i+1}", key=f"color_label_{i}", value=f"Group {i+1}")
                if cols:
                    color_groups.append(cols)
                    color_labels.append(label)

        with st.expander("🎚️ Pattern Groups"):
            pattern_styles_available = ['solid', 'dotted', 'dashed', 'dashdot']
            pattern_groups, pattern_labels = [], []
            num_pattern_groups = st.number_input("Number of pattern groups", min_value=0, max_value=10, value=0)
            for i in range(num_pattern_groups):
                cols = st.multiselect(f"Pattern Group {i+1} Columns", columns, key=f"pattern_group_{i}")
                label = st.text_input(f"Label for Pattern Group {i+1}", key=f"pattern_label_{i}", value=f"Pattern {i+1}")
                pattern = st.selectbox(f"Pattern Style for Group {i+1}", pattern_styles_available, key=f"pattern_style_{i}")
                if cols:
                    pattern_groups.append(cols)
                    pattern_labels.append((label, pattern))
        
        show_background = st.sidebar.checkbox("Show Spectral Backgrounds", value=False)

        if st.button("📊 Plot Line Graph"):
            if not color_groups:
                color_groups = [[col] for col in y_columns]
                color_labels = y_columns
        
            plot_graph(
                data, x_column, y_columns,
                color_groups, pattern_groups, bullet_groups,
                color_labels, pattern_labels, bullet_labels,
                x_log_scale, y_log_scale,
                x_range, y_range,
                title, x_axis_label, y_axis_label,
                font_sizes, marker_size,show_background = show_background

            )


        # ------------------ Integration ------------------
        with st.expander("🧮 Integration (Area under Curve)"):
            int_x_column = st.selectbox("X-axis for integration", columns, index=columns.index(x_column))
            int_y_column = st.selectbox("Y-axis for integration", columns, index=columns.index(y_columns[0]))
            log_x_integ = st.checkbox("Log scale X-axis for integration", value=x_log_scale)
            log_y_integ = st.checkbox("Log scale Y-axis for integration", value=y_log_scale)
            method = st.selectbox("Integration method", ["trapezoid", "Simpson 1/3", "Simpson 3/8"])

            if st.button("➕ Calculate Integral"):
                combined = data[[int_x_column, int_y_column]].copy()
                combined[int_x_column] = pd.to_numeric(combined[int_x_column], errors='coerce')
                combined[int_y_column] = pd.to_numeric(combined[int_y_column], errors='coerce')
                combined = combined.dropna()
                combined = combined.sort_values(by=int_x_column)

                x_vals = combined[int_x_column].values
                y_vals = combined[int_y_column].values

                if len(x_vals) < 2:
                    st.error("Not enough valid points for integration.")
                else:
                    result = integrate_curve(x_vals, y_vals, log_x=log_x_integ, log_y=log_y_integ, method=method)
                    if isinstance(result, str) and result.startswith("❌"):
                        st.error(result)
                    else:
                        st.success(f"✅ Integral ({method}): {result:.4E}")

# ------------------ Pie Chart ------------------

def plot_pie_chart():
    st.title("🥧 Pie Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="piechart")
    if uploaded_file is None:
        return
    data = read_file(uploaded_file)
    if data is None:
        return

    st.subheader("Data Preview")
    st.write(data)
    column = st.selectbox("Select column for pie chart", data.columns)
    fig, ax = plt.subplots()
    data[column].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_title(f"Pie Chart of {column}")
    st.pyplot(fig)

# ------------------ Bar Chart ------------------

def plot_bar_chart():
    st.title("📊 Bar Chart Visualization")
    uploaded_file = st.file_uploader("Upload your data file", key="barchart")
    if uploaded_file is None:
        return
    data = read_file(uploaded_file)
    if data is None:
        return

    st.subheader("Data Preview")
    st.write(data)

    columns = data.columns.tolist()
    x_column = st.selectbox("X-axis column", columns)
    y_column = st.selectbox("Y-axis column", columns, index=1)

    use_labels = st.checkbox("Use custom labels from column?")
    if use_labels:
        label_column = st.selectbox("Label column", columns)
        labels = data[label_column].astype(str)
    else:
        labels = data[x_column].astype(str)

    fig, ax = plt.subplots()
    ax.bar(labels, data[y_column])
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_title(f"{y_column} vs {x_column}")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

# ------------------ Main ------------------


st.sidebar.title("Visualization Tools")
st.sidebar.write("Developed by Pranjal Sharma")
option = st.sidebar.selectbox("Choose a tool", ["Line Graph Plot", "Pie Chart", "Bar Chart"])
if option == "Line Graph Plot":
    linegraph()
elif option == "Pie Chart":
    plot_pie_chart()
elif option == "Bar Chart":
    plot_bar_chart()

