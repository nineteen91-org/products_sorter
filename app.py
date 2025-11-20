import streamlit as st
import pandas as pd
from db import init_db, save_upload, get_uploads, get_upload_data

st.set_page_config(page_title="Excel Manager", layout="wide")
init_db()

# ---------- PREMIUM CSS ----------
st.markdown("""
    <style>
    .main > div {
        padding: 20px;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
        margin-bottom: 18px;
    }
    .title {
        font-size: 20px;
        font-weight: 600;
        padding-bottom: 8px;
        border-bottom: 1px solid #efefef;
        margin-bottom: 12px;
    }
    .muted {
        color: #6b7280;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Nineteen 91 Enterprises")

left, right = st.columns([1, 2])


# ---------------- LEFT: Upload ----------------
with left:
    st.markdown("<div class='card'><div class='title'>📤 Upload Excel</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload .xlsx / .xls", type=["xlsx", "xls"], key="uploader")

    if uploaded_file:
        df = pd.read_excel(uploaded_file, dtype=str)
        df = df.fillna("")

        st.write("Preview:")
        st.dataframe(df.head())

        if st.button("Save to Database"):
            save_upload(uploaded_file.name, df)
            st.success("File saved successfully!")

            # SAFE REFRESH
            st.session_state["refresh_uploads"] = True
            st.session_state["uploader"] = None   # clears file input
            st.stop()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------- RIGHT: File list + viewer ----------------
with right:
    st.markdown("<div class='card'><div class='title'>📁 Uploaded Files</div>", unsafe_allow_html=True)

    # Force reload of uploaded file list
    if st.session_state.get("refresh_uploads"):
        uploads = get_uploads()
        st.session_state["refresh_uploads"] = False
    else:
        uploads = get_uploads()

    if uploads.empty:
        st.info("No files uploaded yet.")
        selected_file = None
    else:
        # show filename with id in dropdown
        selected_file = st.selectbox(
            "Select a file to view",
            uploads["filename"] + " (ID: " + uploads["id"].astype(str) + ")"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Show only when a file is selected
    if selected_file:
        st.markdown("<div class='card'><div class='title'>📄 File Data</div>", unsafe_allow_html=True)

        upload_id = int(selected_file.split("ID: ")[1].replace(")", ""))
        df_loaded = get_upload_data(upload_id)

        if df_loaded.empty:
            st.info("No rows found for the selected file.")
        else:
            # -------- SEARCH BOX --------
            search_query = st.text_input("Search in rows (type and press Enter)", placeholder="Type to filter rows across all columns...")

            if search_query:
                # Fast vectorized approach: join all columns into single string per row and search once
                # Convert to string to be safe for mixed dtypes
                joined = df_loaded.astype(str).agg(' '.join, axis=1)
                mask = joined.str.contains(search_query, case=False, na=False)
                df_filtered = df_loaded[mask].reset_index(drop=True)
                st.write(f"Showing {len(df_filtered)} of {len(df_loaded)} rows matching \"{search_query}\"")
            else:
                df_filtered = df_loaded

            # Display filtered dataframe
            st.dataframe(df_filtered, use_container_width=True)

            # Optional: Download button for filtered view
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button("Download filtered CSV", data=csv, file_name=f"upload_{upload_id}.csv", mime="text/csv")

        st.markdown("</div>", unsafe_allow_html=True)
