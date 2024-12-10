import streamlit as st

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Interactive Map", "File Upload"])

if page == "Interactive Map":
    st.title("Interactive Map")
    st.map()  # Placeholder for your full-screen map logic

elif page == "File Upload":
    st.title("File Upload")

    uploaded_file = st.file_uploader("Choose a file", type=["tif"])
    if uploaded_file is not None:
        st.write("Uploaded file:", uploaded_file.name)
        # Save the uploaded file locally
        with open(f"./uploaded_files/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File {uploaded_file.name} saved successfully!")
