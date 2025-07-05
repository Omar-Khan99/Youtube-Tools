import yt_dlp
import textwrap
from groq import Groq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain_groq import ChatGroq
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from googleapiclient.discovery import build
import isodate
import traceback
from dotenv import load_dotenv

load_dotenv("API.env")

# Initialize LLM
llm = ChatGroq(model="llama3-70b-8192", temperature=0.3)

# Function to Download and Transcribe video and summarize text
def summarize_video(url, filename="audio"):
    try:
        # Validate URL format
        if not url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            return "Error: Please provide a valid YouTube URL"

        # Download video
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '168',
            }],
            'outtmpl': filename,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            return f"Error downloading video: {str(e)}"

        # Transcribe audio
        try:
            client = Groq()
            filename = f"{filename}.mp3"
            with open(filename, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(filename, file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                )
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"
        finally:
            # Clean up the audio file
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass

        # Process and summarize text
        try:
            text = transcription.text
            if not text:
                return "Error: No text was extracted from the video"

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=50, separators=[" ", ",", "\n"]
            )
            texts = text_splitter.split_text(text)
            docs = [Document(page_content=t) for t in texts]
            chain = load_summarize_chain(llm, chain_type="stuff")
            summary = chain.run(docs)
            return textwrap.fill(summary, width=1000)
        except Exception as e:
            return f"Error processing text: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

youtude_api = os.getenv("YOUTUBE_API_KEY") 

# Importent variables
MAX_RESULTS = 10

def get_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=youtude_api)
    
    response = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=video_id
    ).execute()

    if not response['items']:
        return None

    video = response['items'][0]
    
    data = {
        'title': video ['snippet']['title'],
        'description': video['snippet']['description'],
        'url': f"https://www.youtube.com/watch?v={video_id}",
        'views': int(video['statistics'].get('viewCount', 0)),
        'likes': int(video['statistics'].get('likeCount', 0)),
        'duration': video['contentDetails']['duration']
    } 
    data['duration'] = isodate.parse_duration(data['duration']).total_seconds()
    if data['duration'] >= 300:
        return data
    else:
        return None

# Function to format video metadata
def formate_videos_metadata(videos):
    metadata = ""
    for idx, vid in enumerate(videos, start = 1):
        metadata += f"{idx}. Title: {vid['title']}\nDescription: {vid['description']}\n Link: {vid['url']}\n\n"
    
    return metadata

#Function to create a prompt for the LLM
def prompt(user_query, video_metadata_list):
    prompt_template = PromptTemplate(
        input_variables=["user_query", "video_metadata_list"],
        template= f"""
        You are an intelligent assistant helping users find the best YouTube videos.

        User message: "{user_query}"

        From the following videos, recommend the top 3 that are most relevant and useful, and most likely to be watched by the user from the following list:

        {video_metadata_list}

        Give reasult including the title and link only in the following format:
        1. Title: video title, Link: video link
        2. Title: video title, Link: video link
        3. Title: video title, Link: video link

        """
)
   
    return prompt_template
                
def recommend_videos(user_query):

    # to search for videos on YouTube
    try:
        youtube = build("youtube", "v3", developerKey=youtude_api)
        response = youtube.search().list(
            q=user_query,
            part="snippet",
            maxResults=MAX_RESULTS,
            type=["video", "playlist"],
        ).execute()

        # print(response)

        videos = []
        for item in response.get("items", []):
            if item["id"]["kind"] != "youtube#video":
                title = item["snippet"]["title"]
                description = item["snippet"]["description"]
                playlist_id = item["id"]["playlistId"]
                url = f"https://www.youtube.com/playlist?list={playlist_id}"
                videos.append({
                    "title": title,
                    "description": description,
                    "url": url
                })
            else:
                id = item["id"]["videoId"]
                video_data = get_video_details(id)
                if video_data:
                    videos.append(video_data)
                if type(videos) == list: 
                    formatted_list = formate_videos_metadata(videos)
                    prompt_template = prompt(user_query, formatted_list)
                    try:
                        llm = ChatGroq(
                            model="llama3-8b-8192",
                            temperature=0.5,
                            max_retries=3 
                        )

                        model = LLMChain(llm=llm, prompt=prompt_template)
                        response = model.invoke({
                            "user_query": user_query,
                            "video_metadata_list": formatted_list
                        })

                        return response["text"]
                    except Exception as e:
                        return f"Error: {e}"
                else:
                    return f"Error: {videos}"
                
    except Exception as e:
        return f"Error: {e}"