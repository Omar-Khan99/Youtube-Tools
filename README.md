# AI YouTube Assistant

This project features an intelligent AI assistant specialized in handling YouTube video-related tasks. It leverages the power of Large Language Models (LLMs) and various tools to provide two core functionalities: summarizing specific YouTube videos and recommending videos based on user queries.

## Features

-   **YouTube Video Summarization**: Given a YouTube URL, the assistant can download the video's audio, transcribe it using Whisper, and then generate a concise summary of its content. This is useful for quickly grasping the main points of a long video without watching it entirely.
-   **YouTube Video Recommendation**: Users can ask the assistant to find videos on a specific topic or subject. The assistant will search YouTube, analyze the relevance of various videos, and provide a curated list of recommendations with titles and links.

## Technologies Used

*   **Python**: The core programming language for the project.
*   **LangChain**: Used for orchestrating the AI agent, defining tools, and managing LLM interactions.
*   **Groq API**: Provides high-performance inference for the LLM (Llama3-70B and Llama3-8B models) used for summarization and recommendation logic.
*   **YouTube Data API v3**: Utilized for searching YouTube videos, fetching video details (title, description, views, likes, duration), and identifying playlists.
*   **`yt-dlp`**: A powerful command-line program to download videos and audio from YouTube and other video sites, specifically used here for extracting audio.
*   **`python-dotenv`**: For securely loading environment variables, especially API keys.
*   **`isodate`**: To parse ISO 8601 duration strings returned by the YouTube Data API.

## Setup and Installation

Follow these steps to get the project up and running on your local machine:

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd project-3/Summarize and Diagram
    ```

2.  **Install Dependencies**:
    It's recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **API Keys Configuration**:
    You need API keys for Groq and YouTube Data API.
    *   **Groq API Key**: Obtain this from the [Groq Console](https://console.groq.com/keys).
    *   **YouTube Data API Key**: Obtain this from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials). Ensure the YouTube Data API v3 is enabled for your project.

    Create a file named `API.env` in the root directory of your project (or in the same directory as `All_Tools_used.py` if `API.env` is specified with a path in `load_dotenv()`) and add your API keys as follows:

    ```
    GROQ_API_KEY="your_groq_api_key_here"
    YOUTUBE_API_KEY="your_youtube_api_key_here"
    ```

## How to Run

Navigate to the `Summarize and Diagram` directory and run the `Multi_Agent.py` script:

```bash
python Multi_Agent.py
```

The assistant will start and prompt you to enter your queries.

## Usage Examples

Once the script is running, you can interact with the AI assistant by typing your requests:

### Summarize a YouTube Video:

Provide a direct YouTube video URL.
