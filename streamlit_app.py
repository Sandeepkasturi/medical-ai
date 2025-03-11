import streamlit as st
from PIL import Image
import base64
import os
import requests
from urllib.parse import urlparse
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
from google.generativeai import configure, GenerativeModel
import fitz  # PyMuPDF
import re
import pandas as pd

# Set up the Generative AI configuration with a placeholder API key
configure(api_key="AIzaSyCzEjZj0VlVSO3L_bti6DhUrvq0dDDFYX8")

# Create a Generative Model instance (assuming 'gemini-pro' is a valid model)
model = GenerativeModel('gemini-2.0-flash')


# Function to download generated report
def download_generated_report(content, filename, format='txt'):
    extension = format
    temp_filename = f"{filename}.{extension}"
    with open(temp_filename, 'w') as file:
        file.write(content)
    with open(temp_filename, 'rb') as file:
        data = file.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/{format};base64,{b64}" download="{filename}.{format}">Download Report ({format.upper()})</a>'
    st.markdown(href, unsafe_allow_html=True)
    os.remove(temp_filename)


# Function to load Lottie animations
def load_lottie_url(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Function to extract topic from prompt
def extract_topic(prompt):
    start_phrases = ["@codex", "codex", "@medic"]
    for phrase in start_phrases:
        if prompt.lower().startswith(phrase):
            return prompt[len(phrase):].strip()
    return prompt.strip()


# Function to fetch YouTube videos
def fetch_youtube_videos(query):
    api_key = st.secrets["youtube_api_key"]
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 4,
        "key": api_key
    }
    response = requests.get(search_url, params=params)
    video_details = []
    if response.status_code == 200:
        results = response.json()["items"]
        for item in results:
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_details.append({
                "title": video_title,
                "url": video_url,
                "video_id": video_id
            })
    else:
        st.error(f"Failed to fetch YouTube videos. Status code: {response.status_code}")
    return video_details


def main():
    st.set_page_config(page_title="Medical AI APP", page_icon="❤️", layout="wide",
                       initial_sidebar_state="expanded")

    st.sidebar.image("medi.png", use_column_width=True)
    # Custom Follow Me buttons with adjustable width and clickable links using Streamlit's st.sidebar.markdown()
    page = st.sidebar.selectbox("**MENU**",
                                ["🏠 Home", "🧠 Healthcare assistant", "📝 Disease analyzer", "💊 Drug Details",])
    st.sidebar.markdown(""" Follow me on:
    <style>
    .follow-me {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 20px;
    }
    .follow-me img {
        width: 40px;
        height: auto;
        border-radius: 5px;
        margin-right: 25px; /* Adjust this value for spacing */
    }
    </style>

    <div class="follow-me">
        <a href="https://github.com/sandeepkasturi" target="_blank">
            <img src="https://imgs.search.brave.com/J98scS-zV9tuiqZTsNtHuZRskbrcZFOkVCzZeNH2CJI/rs:fit:500:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvY29tbW9ucy90/aHVtYi8yLzI5L0dp/dEh1Yl9sb2dvXzIw/MTMuc3ZnLzIyMHB4/LUdpdEh1Yl9sb2dv/XzIwMTMuc3ZnLnBu/Zw" alt="GitHub">
        </a>
        <a href="https://www.instagram.com/sandeep_kasturi_" target="_blank">
            <img src="https://imgs.search.brave.com/iDxNo9u4vGUacdSB5VVCvgGmGkmPVpHOK5q1gvszsQs/rs:fit:500:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvY29tbW9ucy90/aHVtYi85Lzk1L0lu/c3RhZ3JhbV9sb2dv/XzIwMjIuc3ZnLzIy/MHB4LUluc3RhZ3Jh/bV9sb2dvXzIwMjIu/c3ZnLnBuZw" alt="Instagram">
        </a>
        <a href="https://twitter.com/@Sandeepkasturi9" target="_blank">
            <img src="https://imgs.search.brave.com/LXvqCdGG_3hdMxsJQbeCtZcCseEiPVOSkVdwnsV6WJo/rs:fit:500:0:0/g:ce/aHR0cHM6Ly91cGxv/YWQud2lraW1lZGlh/Lm9yZy93aWtpcGVk/aWEvY29tbW9ucy90/aHVtYi9jL2NlL1hf/bG9nb18yMDIzLnN2/Zy8yMjBweC1YX2xv/Z29fMjAyMy5zdmcu/cG5n" alt="Twitter">
        </a>
    </div>
    """, unsafe_allow_html=True)

    if page == "🏠 Home":
        st.title("Welcome to Medical AI 🧑‍⚕️")
        st.markdown("""
        **Medical AI**:
        Medical, powered by the Gemini API, is a basic application designed for Mental Health Care. 
        """)

        # Embedding Lottie animation
        lottie_url = "https://lottie.host/d7233830-b2c0-4719-a5c0-0389bd2ab539/qHF7qyXl5q.json"
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=400, height=300, key="lottie_animation")
        else:
            st.error("Failed to load Lottie animation.")

        st.markdown("""
        **Guidelines:**

        - **Respectful Conduct**: Users are expected to engage in respectful and considerate interactions within the medical community. Any form of harassment, hate speech, or derogatory behavior will not be tolerated.
        - **Accuracy of Information**: While Medical aims to provide helpful information and support, users should understand that the content provided is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for personalized guidance.
        - **Data Privacy**: Medical respects user privacy and confidentiality. Personal information shared within the platform will be handled with the utmost care and will not be shared with third parties without explicit consent, except as required by law.
        - **Community Support**: Medical encourages users to support each other in a positive and constructive manner. Users are welcome to share their experiences, insights, and advice, but should refrain from giving medical diagnoses or prescribing treatments.
        - **Feedback and Suggestions**: We value user feedback and suggestions for improving Medical. Users are encouraged to provide feedback on their experience with the platform and suggest features or content that would enhance their user experience.
        - **Safety and Well-being**: Medical prioritizes the safety and well-being of its users. If you or someone you know is in crisis or experiencing a medical emergency, please seek immediate assistance from a qualified healthcare professional or emergency services.

        Developed by SKAV TECH, a company focused on creating practical AI projects, Medical is intended for educational purposes only. We do not endorse any illegal or unethical activities.
        """)
    elif page == "🧠 Healthcare assistant":
        st.header("🧠 Healthcare assistant")

        lottie_url = "https://lottie.host/0c079fc2-f4df-452a-966b-3a852ffb9801/WjOxpGVduu.json"
        # Load and display Lottie animation
        lottie_animation = load_lottie_url(lottie_url)
        if lottie_animation:
            st_lottie(lottie_animation, speed=1, width=220, height=300, key="lottie_animation")
        else:
            st.error("Failed to load Lottie animation.")

        st.markdown(
            "Medical AI may provide inaccurate responses. Read all the guidelines and usage instructions. Contact a doctor before proceeding.")

        question = st.text_input("Ask the model a question:")
        if st.button("Ask AI"):
            topic = extract_topic(question)

            with st.spinner("Generating response 😉"):
                try:
                    response = model.generate_content(f"You are an expert mental healthcare professional: {question}")
                    if response.text:
                        st.text("Medical AI Response:")
                        st.write(response.text)
                        st.markdown('---')

                        # Fetch YouTube video suggestions
                        video_suggestions = fetch_youtube_videos(topic)
                        if video_suggestions:
                            st.markdown("### YouTube Video Suggestions:")

                            # Summary provided by the model
                            summary = response.text

                            # Display the summary
                            st.markdown(f"**Summary:** {summary}")

                            for video in video_suggestions:
                                st.write(f"[{video['title']}]({video['url']})")
                                st.video(video["url"])

                    else:
                        st.error("No valid response received from the AI model.")
                        st.write(f"Safety ratings: {response.safety_ratings}. Change the prompt to continue.")
                except ValueError as e:
                    st.info(f"🤐 Unable to assist with that prompt due to: {e}. Change the prompt to continue.")
                except IndexError as e:
                    st.info(f"🤐 Unable to assist with that prompt due to: {e}. Change the prompt to continue.")
                except Exception as e:
                    st.info(f"An unexpected error occurred 😕. Change the prompt to continue: {e}")

                report_keywords = ["report", "health", "illness", "summary", "sick"]
                if any(keyword in question.lower() for keyword in report_keywords):
                    if response.text:
                        download_generated_report(response.text, "report")
        st.markdown('---')

    elif page == "📝 Disease analyzer":
        st.header("📝 Disease analyzer")
        st.markdown("Upload your medical report (PDF format):")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

        if uploaded_file is not None:
            try:
                text = extract_text_from_pdf(uploaded_file)
                st.text_area("Extracted Text:", text, height=300)

                if st.button("Analyze Report"):
                    with st.spinner("Analyzing report..."):
                        try:
                            prompt = f"Analyze the following medical report and provide insights:\n\n{text}"
                            response = model.generate_content(prompt)
                            if response.text:
                                st.text("Analysis:")
                                st.write(response.text)
                                download_generated_report(response.text, "analysis", format="txt")
                            else:
                                st.error("No valid response received from the AI model.")
                        except ValueError as e:
                            st.error(f"Unable to analyze the report: {e}")
                        except IndexError as e:
                            st.error(f"Unable to analyze the report: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred while analyzing the report: {e}")

            except Exception as e:
                st.error(f"Failed to extract text from PDF: {e}")

    elif page == "💊 Drug Details":
        st.header("💊 Drug Details")
        st.markdown("Select the input method:")

        input_method = st.radio("Choose the input method:", ("Text Input", "PDF Upload"))

        if input_method == "Text Input":
            medicine_name = st.text_input("Enter the medicine name:")

            if st.button("Analyze Medicine"):
                with st.spinner("Analyzing medicine details..."):
                    try:
                        prompt = f"Provide insights on the following medicine: {medicine_name}"
                        response = model.generate_content(prompt)
                        if response.text:
                            st.text("Analysis:")
                            st.write(response.text)
                            download_generated_report(response.text, "medicine_analysis", format="txt")
                        else:
                            st.error("No valid response received from the AI model.")
                    except ValueError as e:
                        st.error(f"Unable to analyze the medicine details: {e}")
                    except IndexError as e:
                        st.error(f"Unable to analyze the medicine details: {e}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred while analyzing the medicine details: {e}")

        elif input_method == "PDF Upload":
            uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

            if uploaded_file is not None:
                try:
                    text = extract_text_from_pdf(uploaded_file)
                    st.text_area("Extracted Text:", text, height=300)

                    if st.button("Analyze Medicine"):
                        with st.spinner("Analyzing medicine details..."):
                            try:
                                prompt = f"Analyze the following medicine details and provide insights:\n\n{text}"
                                response = model.generate_content(prompt)
                                if response.text:
                                    st.text("Analysis:")
                                    st.write(response.text)
                                    download_generated_report(response.text, "medicine_analysis", format="txt")
                                else:
                                    st.error("No valid response received from the AI model.")
                            except ValueError as e:
                                st.error(f"Unable to analyze the medicine details: {e}")
                            except IndexError as e:
                                st.error(f"Unable to analyze the medicine details: {e}")
                            except Exception as e:
                                st.error(f"An unexpected error occurred while analyzing the medicine details: {e}")

                except Exception as e:
                    st.error(f"Failed to extract text from PDF: {e}")

if __name__ == "__main__":
    main()
