import streamlit as st
import os
import tempfile
import logging
import uuid
from binji.graph import graph
from binji.configuration import Configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.title("Binji")

if "thread_id_binji" not in st.session_state:
    # Turn this into two columns
    disposal_country = st.selectbox(
        "Select disposal country", ["South Korea"]
    )

    cols = st.columns(2)
    enable = st.checkbox("Enable camera")
    with cols[0]:
        camera_image = st.camera_input("Take a picture", disabled=not enable)
    with cols[1]:
        uploaded_file = st.file_uploader(
            "Or choose images", type=["png", "jpg", "jpeg"], accept_multiple_files=False
        )

    file_to_process = camera_image if camera_image else uploaded_file

    if file_to_process:
        st.session_state["thread_id_binji"] = str(uuid.uuid4())
        with st.spinner("Processing..."):
            paths = []
            # Use the appropriate method to get bytes and extension
            if uploaded_file:
                file_bytes = uploaded_file.read()
                file_suffix = os.path.splitext(uploaded_file.name)[1]
            else:
                file_bytes = camera_image.getvalue()
                file_suffix = ".jpg"  # camera_input returns jpg
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
                logger.info(f"Saving temporary file: {tmp.name}")
                tmp.write(file_bytes)
                paths.append(tmp.name)
            st.session_state["paths"] = paths
            st.session_state["disposal_country"] = disposal_country
            st.rerun()

if "paths" in st.session_state and "result" not in st.session_state:
    st.image(st.session_state["paths"][0], width=400)

    if st.button("Process image"):
        with st.spinner("Processing..."):
            input_data = {
                "image_path": st.session_state["paths"][0],
                "max_size": 640,
            }
            with st.empty():
                for stream_mode, chunk in graph.stream(
                    input_data,
                    config={
                        "configurable": Configuration(
                            thread_id=st.session_state["thread_id_binji"],
                            disposal_country=st.session_state["disposal_country"],
                        ).model_dump()
                    },
                    stream_mode=["values", "custom"],
                ):
                    if stream_mode == "custom":
                        st.write(chunk.get("custom_key", ""))
                    elif stream_mode == "values":
                        result = chunk
                        st.write("")
                st.session_state["result"] = result
        st.rerun()

if "result" in st.session_state:
    st.image(st.session_state["paths"][0], width=400)

    st.markdown(st.session_state["result"]["final_answer"])

    for path in st.session_state["paths"]:
        try:
            logger.info(f"Removing temporary file: {path}")
            os.remove(path)
        except Exception as e:
            logger.error(f"Failed to remove temporary file: {path}")
            logger.error(str(e))
