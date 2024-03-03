import os
from pytube import Playlist
import streamlit as st
import openai
from dotenv import load_dotenv
from pytube import YouTube, Playlist
from youtube_transcript_api import YouTubeTranscriptApi

# Load the environment variables from .env file
load_dotenv()

# Access your API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# For example, setting the OpenAI API key
openai.api_key = openai_api_key

def fetch_transcript_for_video(video_url):
    video_id = video_url.split("watch?v=")[-1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return compile_transcript(transcript)
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {e}")
        return "Transcript could not be fetched."

def compile_transcript(transcript):
    output = ''
    for x in transcript:
        sentence = x['text']
        output += f' {sentence}\n'
    return output.strip()

def process_video(url):
    video_id = url.split("watch?v=")[-1]
    yt = YouTube(url)
    video_title = yt.title
    # print(f"Fetching transcript for video: {video_title}")
    transcription = fetch_transcript_for_video(video_id)
    return {video_title: transcription}

def download_and_transcribe_selected_videos(playlist_url, selected_titles):
    playlist = Playlist(playlist_url)
    transcriptions = {}

    for video_url in playlist.video_urls:
        yt = YouTube(video_url)
        video_title = yt.title

        if video_title in selected_titles:
            # print(f"Fetching transcript for video: {video_title}")
            transcription = fetch_transcript_for_video(video_url)
            transcriptions[video_title] = transcription

    return transcriptions

def summarize_text(text, openai_api_key):
    openai.api_key = openai_api_key
    prompt = (
        "Create a concise, informative summary suitable for professors, students, and general audiences that provides a comprehensive overview of the following video content:\n\n"
        f"{text}"
    )

    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1000  # Adjust the number of tokens as needed
    )
    return response.choices[0].text.strip()

def generate_quiz_questions(api_key, context, difficulty, number_of_questions):
    openai.api_key = api_key

    formatted_prompt = (
        f"Create {number_of_questions} advanced, master's level standard questions based on the following {difficulty} text. "
        "Each question should:\n\n"
        "1. Be based on the context provided.\n"
        "2. Include a variety of question types:\n"
        "   - Single correct answer option\n"
        "   - Multiple correct answers options\n"
        "   - Text entry\n"
        "   - Numeric entry\n"
        "3. For multiple choice questions with one or more correct answers and plausible but incorrect alternatives, include 4 options (labeled A to D, each option on new line)\n"
        "4. For text or numeric entry, require a specific, correct answer.\n"
        "5. Reflect high academic standards in both content and formulation.\n"
        "6. Provide correct answer and display it on a new line and provide a brief explanation for the correct answer, highlighting key concepts or reasoning and display it on new line.\n\n"
        "Context for questions:\n\n" + context
    )
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=formatted_prompt,
        max_tokens=250 * number_of_questions
    )
    return response.choices[0].text.strip()

# def main():
#     st.title("EduTube QuizBuilder")

#     playlist_url = st.text_input("Enter the URL of the YouTube Playlist")

#     if playlist_url:
#         playlist = Playlist(playlist_url)
#         video_titles = [YouTube(url).title for url in playlist.video_urls]

#         # Session state for selected titles
#         if 'selected_titles' not in st.session_state:
#             st.session_state['selected_titles'] = []

#         selected_titles = st.multiselect("Select videos to transcribe or summarize", video_titles, default=st.session_state['selected_titles'])

#         # Update session state
#         st.session_state['selected_titles'] = selected_titles

#         # Transcription and summarization options
#         user_choice = st.radio("Choose an action", ("Transcribe", "Summarize"))

#         if st.button("Process Selected Videos"):
#             with st.spinner('Processing selected videos...'):
#                 try:
#                     transcriptions = download_and_transcribe_selected_videos(playlist_url, st.session_state['selected_titles'])
                    
#                     if user_choice == "Summarize":
#                         # Store summaries in session state
#                         st.session_state['result'] = {title: summarize_text(text, openai_api_key) for title, text in transcriptions.items()}
#                     else:
#                         # Store transcriptions in session state
#                         st.session_state['result'] = transcriptions

#                     # Display results
#                     for title, content in st.session_state['result'].items():
#                         st.subheader(title)
#                         st.write(content)

#                 except Exception as e:
#                     st.error(f"An error occurred: {e}")

#         # Quiz creation option
#         if 'result' in st.session_state and st.checkbox("Create a quiz based on this content?"):
#             difficulty = st.selectbox("Select difficulty level", ["Easy", "Moderate", "Difficult", "Master"])
#             number_of_questions = st.number_input("Number of questions", min_value=1, value=5)

#             if st.button("Generate Quiz"):
#                 # Aggregate all content for quiz context
#                 context = " ".join(st.session_state['result'].values())
#                 quiz_questions = generate_quiz_questions(openai_api_key, context, difficulty, number_of_questions)
#                 st.subheader("Quiz Questions")
#                 st.write(quiz_questions)

def main():
    st.title("EduTube QuizBuilder")
    # Asking user what they would like to input
    user_input_type = st.radio("Enter a YouTube Video or a YouTube Playlist URL?",
        ("YouTube Video", "YouTube Playlist"),
        key="input_type_selection"  # Unique key to avoid DuplicateWidgetID error
    )

    if user_input_type == "YouTube Playlist":
        playlist_url = st.text_input("Enter the URL of the YouTube Playlist")

        if playlist_url:
            playlist = Playlist(playlist_url)
            video_titles = [YouTube(url).title for url in playlist.video_urls]

            if 'selected_titles' not in st.session_state:
                st.session_state['selected_titles'] = []

            selected_titles = st.multiselect("Select videos to transcribe or summarize", video_titles, default=st.session_state['selected_titles'])

            st.session_state['selected_titles'] = selected_titles

            user_choice = st.radio(
                "Choose an action",
                ("Transcribe", "Summarize"),
                key="action_selection"  # Another unique key
            )

            if st.button("Process Selected Videos"):
                with st.spinner('Processing selected videos...'):
                    try:
                        transcription_playlist = download_and_transcribe_selected_videos(playlist_url, st.session_state['selected_titles'])
                        
                        if user_choice == "Summarize":
                            st.session_state['result'] = {title: summarize_text(text, openai_api_key) for title, text in transcription_playlist.items()}
                        else:
                            st.session_state['result'] = transcription_playlist

                        for title, content in st.session_state['result'].items():
                            st.subheader(title)
                            st.write(content)

                    except Exception as e:
                        st.error("You have entered a video URL, please input a YouTube playlist URL instead.")

    elif user_input_type == "YouTube Video":
        video_url = st.text_input("Enter the URL of the YouTube Video")

        

        if video_url:
            user_choice = st.radio(
                "Choose an action",
                ("Transcribe", "Summarize"),
                key="action_selection"  # Another unique key
            )
            if st.button("Process Video"):
                with st.spinner('Fetching video details...'):
                    try:
                        transcription_video = process_video(video_url)
                        # print(transcription_video)
                        if user_choice == "Summarize":
                                st.session_state['result'] = {title: summarize_text(text, openai_api_key) for title, text in transcription_video.items()}
                        else:
                            st.session_state['result'] = transcription_video


                        for title, content in st.session_state['result'].items():
                            st.subheader(title)
                            st.write(content)
                    except Exception as e:
                        st.error(f"{e}")
                    

    # Quiz creation option (this part remains common and should be outside the if-elif block if both input types allow for quiz creation)
    if 'result' in st.session_state and st.checkbox("Create a quiz based on this content?"):
        difficulty = st.selectbox("Select difficulty level", ["Easy", "Moderate", "Difficult", "Master"])
        number_of_questions = st.number_input("Number of questions", min_value=1, value=5)

        if st.button("Generate Quiz"):
            context = " ".join(st.session_state['result'].values())
            quiz_questions = generate_quiz_questions(openai_api_key, context, difficulty, number_of_questions)
            st.subheader("Quiz Questions")
            st.write(quiz_questions)


if __name__ == "__main__":
    main()
