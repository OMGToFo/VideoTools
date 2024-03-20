import streamlit as st
import yt_dlp

from yt_dlp import YoutubeDL

from streamlit_option_menu import option_menu

import moviepy.editor as mp
import tempfile
import speech_recognition as sr


import os

_="""
option = st.sidebar.selectbox("Choose:",
                              ("Download YouTube", "Video to Audio","Videoframegrabber"),
                              index=None,
                              placeholder="Select..." )
"""


st.set_page_config(
    page_title="Simple Videotools",
    page_icon="🧊",
    #layout="wide",
    #initial_sidebar_state="expanded",
)

#---Option Menu -------------------

option = option_menu(
	menu_title="Videotools",
	options=["Download YouTube", "Video to Audio","Framegrabber","Videoresizer"],
	icons=["youtube", "soundwave","collection","pip"], #https://icons.getbootstrap.com/
	orientation="horizontal",
)

#Code um den Button-Design anzupassen
m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #ce1126;
    color: white;
    height: 3em;
    width: 14em;
    border-radius:10px;
    border:3px solid #000000;
    font-size:20px;
    font-weight: bold;
    margin: auto;
    display: block;
}
div.stButton > button:hover {
	background:linear-gradient(to bottom, #ce1126 5%, #ff5a5a 100%);
	background-color:#ce1126;
}
div.stButton > button:active {
	position:relative;
	top:3px;
}
</style>""", unsafe_allow_html=True)




if option != "Download YouTube":
    uploaded_file = st.sidebar.file_uploader("Upload Video", type=['mp4', 'mov', 'avi', 'flv', 'wmv'])




if option == "Download YouTube": #######################################################################
    @st.cache  # _data
    def download_video_from_url(url):
        videoinfo = YoutubeDL().extract_info(url=url, download=False)
        filename = f"./youtube/{videoinfo['id']}.mp4"
        options = {
            'format': 'best',  # Use 'best' to download both video and audio
            'keepvideo': True,
            'outtmpl': filename,
        }
        with YoutubeDL(options) as ydl:
            ydl.download([videoinfo['webpage_url']])
        return filename


    @st.cache  # _data
    def download_audio_from_url(url):
        videoinfo = YoutubeDL().extract_info(url=url, download=False)
        filename = f"./youtube/{videoinfo['id']}.mp3"
        options = {
            'format': 'bestaudio/best',  # Download the best audio
            'keepvideo': False,  # Don't keep the video
            'outtmpl': filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Convert to MP3
                'preferredquality': '192',  # Audio quality
            }],
        }
        with YoutubeDL(options) as ydl:
            ydl.download([videoinfo['webpage_url']])
        return filename


    _="""
        def extract_YTaudio(video_file):
            video = mp.VideoFileClip(filename_video)
            audio = video.audio
            audio_file = "audio.wav"
            audio.write_audiofile(audio_file)
            return audio_file
    """


    st.title("YouTube Downloader")

    st.info("Copy the link from the Share Option")
    url = st.text_input('Url:', '')
    YTDownloadStart = st.button("Start fetching Youtube-Video")

    if YTDownloadStart:
            if url != "":
                filename_video = download_video_from_url(url)
                st.video(filename_video)
                with open(filename_video, "rb") as f:
                    st.download_button("Download Video", data=f, file_name="YT_video.mp4")











if option == "Video to Audio": #######################################################################



    def extract_audio(video_file):
        video = mp.VideoFileClip(video_file)
        audio = video.audio
        audio_file = "audio.wav"
        audio.write_audiofile(audio_file)
        return audio_file


    def transcribe_audio(audio_file, language):
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=language)
            return text


    st.title("Video to Audio")
    #uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi', 'flv', 'wmv'])

    if uploaded_file is None:
        st.warning("<<<  Upload a videofile <<<")
        st.sidebar.warning("^^^ Upload a video ^^^")

    if uploaded_file is not None:

        st.write("Uploaded video:")
        video_filename = uploaded_file.name
        st.write(uploaded_file.name)
        st.write(uploaded_file.size)
        showUploadedVideo = st.checkbox("Show uploaded video")
        if showUploadedVideo:
            st.video(uploaded_file)

        st.title('Convert Video to Audio')

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())

        with st.spinner('Extracting Audio...'):
            audio_file = extract_audio(tfile.name)
        st.audio(audio_file, format='audio/wav')
        st.download_button('Download Audio', audio_file, 'audio.wav')

        st.divider()
        st.title('Transcribe Audio')

        language = st.selectbox('Choose language',
                                ['de-DE', 'en-US', 'sv-SE', 'de-CH', 'fr-FR', 'es-ES', 'it-IT'])
        audiotranskribieren = st.button("Start transcription!")

        if audiotranskribieren:

            with st.status('Transcribing...'):
                transcript = transcribe_audio(audio_file, language)
            st.text_area('Transkript:', value=transcript, height=400)


if option == "Framegrabber": #######################################################################

    import cv2
    import numpy as np
    import tempfile

    import zipfile
    import os
    import base64


    def extract_stills(video_path, frame_interval):
        frames = []
        timecodes = []
        video_capture = cv2.VideoCapture(video_path)
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_number = 0
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            if frame_number % frame_interval == 0:
                # Convert frame from BGR to RGB color space
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
                timecodes.append(frame_number / fps)

            frame_number += 1

        video_capture.release()
        return frames, timecodes


    def display_frames(frames, timecodes):
        for i, frame in enumerate(frames):
            # Display the frame using Streamlit
            st.image(frame, caption=f"Frame {i + 1}, Timecode: {timecodes[i]:.2f} seconds")


    def download_link(frames, timecodes):
        # Create a temporary directory to store the frames
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, (frame, timecode) in enumerate(zip(frames, timecodes)):
                filename = f"frame_{i + 1}_timecode_{timecode:.2f}.png"
                filepath = os.path.join(temp_dir, filename)
                cv2.imwrite(filepath, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

            # Create a zip file containing all the frames
            with zipfile.ZipFile("extracted_frames.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_dir))

        # Provide a download link for the zip file
        st.write("Download the zip file containing all frames:")
        st.markdown(get_binary_file_downloader_link("extracted_frames.zip", "Click here to download"),
                    unsafe_allow_html=True)


    def get_binary_file_downloader_link(file_path, download_link_text):
        with open(file_path, 'rb') as file:
            base64_file = base64.b64encode(file.read()).decode()
        href = f'<a href="data:file/txt;base64,{base64_file}" download="{file_path}">{download_link_text}</a>'
        return href


    st.title("Video to Stills Converter")

    # Add file upload functionality
    #uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])

    if uploaded_file is None:
        st.warning("<<<  Upload a videofile <<<")
        st.sidebar.warning("^^^ Upload a video ^^^")


    if uploaded_file is not None:
        # Save the uploaded video to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        video_path = temp_file.name

        # User input for frame grab interval
        # frame_interval = st.slider("Select frame grab interval (in seconds)", 1, 10, 1)

        frame_interval = st.number_input("Select frame grab interval (in seconds)", min_value=0.01, max_value=None,
                                         value=1.00, step=0.10)
        st.subheader("")
        startGrabbing = st.checkbox("Start framegrabbing!")
        if startGrabbing:

            # Convert video to still frames
            frames, timecodes = extract_stills(video_path, int(frame_interval * 30))  # Assuming 30 frames per second

            # Display the number of extracted frames
            st.write("Number of frames extracted:", len(frames))

            # Display the selected frames with timecodes
            display_frames(frames, timecodes)

            if st.button("Download All Frames"):
                download_link(frames, timecodes)







if option == "Videoresizer": #######################################################################


    import moviepy.editor as mp
    import os

    # Streamlit UI
    st.title("MP4 Video Resizer")

    # Upload video
    #uploaded_file = st.file_uploader("Upload a video (MP4 format)", type=["mp4"])

    if uploaded_file is None:
        st.warning("<<<  Upload a videofile <<<")
        st.sidebar.warning("^^^ Upload a video ^^^")


    if uploaded_file is not None:
        st.write("Uploaded video:")
        video_filename = uploaded_file.name
        st.write(uploaded_file.name)
        st.write(uploaded_file.size)

        # Check the file extension
        #if video_filename.endswith(".mp4"):
        if 1 == 1:
            # Display the uploaded video
            showUploadedVideo = st.checkbox("Show uploaded video")
            if showUploadedVideo:
                st.video(uploaded_file)

            # Resize options
            st.write("")
            st.subheader("Choose resize options:")
            new_width = st.number_input("New Width (pixels):", min_value=1, value=640)
            preserve_aspect_ratio = st.checkbox("Preserve Aspect Ratio", value=True)

            # User input for output path
            # output_path = st.text_input("Enter output filename for the resized video", value="resized_video.mp4")
            output_path = "resized_video.mp4"

            if st.button("Resize!"):
                st.subheader("")
                if new_width <= 0:
                    st.error("Please enter a valid width.")
                else:
                    # Save the uploaded video temporarily
                    with open(video_filename, "wb") as video_file:
                        video_file.write(uploaded_file.read())

                    # Read the video
                    video = mp.VideoFileClip(video_filename)
                    st.write("Original width: ",video.size[0], " Original height: ",video.size[1])


                    # Calculate the new height while preserving aspect ratio
                    if preserve_aspect_ratio:
                        aspect_ratio = video.size[0] / video.size[1]
                        new_height = int(new_width / aspect_ratio)

                    else:
                        new_height = video.size[1]

                    # Resize the video
                    resized_video = video.resize((new_width, new_height))

                    # Save the resized video to the user-specified output path
                    output_path = output_path.strip()  # Remove leading/trailing spaces
                    resized_video.write_videofile(output_path)

                    st.success(f"Video resized:  New width: " + str(new_width) + " - New height: " + str(new_height))

                    # Display the resized video



                    st.write("Resized video:")

                    videowidth = max(new_width, 0.01)
                    side = max((100 - new_width) / 2, 0.01)

                    _, container, _ = st.columns([side, videowidth, side])
                    container.video(data=output_path)


                    #st.video(output_path)

                    # Allow the user to download the resized video
                    # st.download_button(label="Download Resized Video", data=output_path, file_name="Resizedvideo.mp4", key="download_button")

                    with open(output_path, "rb") as f:
                        st.download_button("Download Video", data=f,
                                           file_name="resized_video_width" + str(new_width) + ".mp4")

                    # Clean up the resources
                    resized_video.close()
                    video.close()

                    # Remove temporary uploaded video
                    os.remove(video_filename)
        else:
            st.error("Please upload a video in MP4 format.")







