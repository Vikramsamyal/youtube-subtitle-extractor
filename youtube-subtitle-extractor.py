# Install necessary packages
!pip install isodate youtube-transcript-api nltk

# Import libraries
from googleapiclient.discovery import build
from isodate import parse_duration
from youtube_transcript_api import YouTubeTranscriptApi
import nltk
import re
import os
from nltk.tokenize import sent_tokenize


# Download necessary NLTK resources
nltk.download('punkt')



# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')


# Function to load processed video IDs
def load_processed_videos(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return set(file.read().split())
    else:
        return set()



# Function to save processed video IDs
def save_processed_videos(filename, video_ids):
    with open(filename, 'a') as file:
        for video_id in video_ids:
            file.write(video_id + '\n')

# Function to fetch and filter videos with pagination
def fetch_and_filter_videos(next_page_token=None):
    search_response = youtube.search().list(
        q='tax planning in India',
        part='id,snippet',
        maxResults=50,
        type='video',
        videoCaption='closedCaption',
        pageToken=next_page_token,
        publishedAfter='2016-01-01T00:00:00Z'
    ).execute()

    video_ids = [item['id']['videoId'] for item in search_response['items']]
    videos_response = youtube.videos().list(
        id=','.join(video_ids),
        part='statistics,snippet,contentDetails'
    ).execute()

    filtered_video_info = []

    for video in videos_response['items']:
        stats = video['statistics']
        snippet = video['snippet']
        content_details = video['contentDetails']

        # Thresholds and filters
        min_views = 10000
        min_likes = 500
        like_dislike_ratio_threshold = 4
        min_subscribers = 1000
        max_duration_seconds = 20 * 60

        video_duration = parse_duration(content_details['duration']).total_seconds()
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        dislikes = int(stats.get('dislikeCount', 1))
        like_dislike_ratio = likes / max(dislikes, 1)
        channel_id = snippet['channelId']
        channel_response = youtube.channels().list(id=channel_id, part='statistics').execute()
        channel_stats = channel_response['items'][0]['statistics']
        subscribers = int(channel_stats.get('subscriberCount', 0))

        if (views >= min_views and likes >= min_likes and like_dislike_ratio >= like_dislike_ratio_threshold and
            subscribers >= min_subscribers and video_duration <= max_duration_seconds):
            filtered_video_info.append((video['id'], snippet['title'], snippet['publishedAt'], snippet['channelTitle'], subscribers))

    return filtered_video_info, search_response.get('nextPageToken')


# Function to save next page token
def save_next_page_token(filename, token):
    with open(filename, 'w') as file:
        file.write(token)

# Function to load next page token
def load_next_page_token(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return file.read().strip()
    return None


# Function to clean and format transcript
def clean_and_format_transcript(transcript):
    full_text = " ".join([segment["text"] for segment in transcript if segment["text"].isascii()])
    full_text = re.sub(r'\[.*?\]|\(.*?\)|\w+:\s|http\S+|www\S+|[^a-zA-Z0-9\s.,?!]', '', full_text)
    cleaned_text = full_text.lower()
    sentences = sent_tokenize(cleaned_text)
    formatted_lines = []
    current_line = ""
    max_chars_per_line = 100
    for sentence in sentences:
        if len(current_line) + len(sentence) + 1 <= max_chars_per_line:
            current_line += sentence + " "
        else:
            formatted_lines.append(current_line.strip())
            current_line = sentence + " "
    if current_line:
        formatted_lines.append(current_line.strip())
    return "\n".join(formatted_lines)


# Function to save transcript to file
def save_transcript_to_file(video_info, transcript):
    video_id, title, published_at, channel_name, subscribers = video_info
    filename = f"{video_id}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Title: {title}\nPublished At: {published_at}\nChannel: {channel_name}\nSubscribers: {subscribers}\n\n")
        file.write(transcript)
    print(f"Transcript saved to {filename}")


# Function to fetch subtitles in preferred languages
def get_preferred_subtitles(video_id):
    languages_priority = ["en", "en-IN", "en-US"]  # List of preferred languages in order of priority
    for language in languages_priority:
        try:
            # Attempt to fetch the transcript for the given video ID and language
            return YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        except Exception as e:
            # If fetching the transcript fails (e.g., no subtitles available for the languages), continue to the next language
            continue
    # Return None if no subtitles were found for any of the preferred languages
    return None



# Function to process each video
def process_video(video_info):
    video_id = video_info[0]
    subtitles = get_preferred_subtitles(video_id)
    if subtitles:
        formatted_transcript = clean_and_format_transcript(subtitles)
        save_transcript_to_file(video_info, formatted_transcript)
    else:
        print(f"Subtitles not found for video ID: {video_id}")


# Main execution function
def main():
    processed_videos_filename = 'processed_videos.txt'
    next_page_token_filename = 'next_page_token.txt'
    
    processed_videos = load_processed_videos(processed_videos_filename)
    next_page_token = load_next_page_token(next_page_token_filename)

    video_info_list, next_page_token = fetch_and_filter_videos(next_page_token)
    new_videos_to_process = [info for info in video_info_list if info[0] not in processed_videos]

    for video_info in new_videos_to_process:
        process_video(video_info)
        processed_videos.add(video_info[0])

    save_processed_videos(processed_videos_filename, [info[0] for info in new_videos_to_process])
    save_next_page_token(next_page_token_filename, next_page_token)




# Run main function
main()
