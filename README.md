# YouTube Subtitle Extractor

This project is an algorithm that searches for relevant YouTube videos, verifies their credibility, extracts subtitles, cleans them, and uses pagination to avoid processing the same videos multiple times. The script is written in Python and uses various libraries to interact with YouTube API, process text, and manage pagination.

## Features

- **Search YouTube Videos**: Searches for YouTube videos based on a query.
- **Filter Videos**: Filters videos by views, likes, like/dislike ratio, channel subscribers, and duration.
- **Extract Subtitles**: Extracts English subtitles provided by the content creator.
- **Clean and Format Subtitles**: Cleans and formats the extracted subtitles.
- **Pagination**: Uses pagination to avoid processing duplicate videos in batch runs.

## Technologies Used

- **Python**
- **Google API Client**
- **YouTube Transcript API**
- **NLTK (Natural Language Toolkit)**
- **Regular Expressions (Regex)**
- **ISO8601 Duration Parser (isodate)**

## Prerequisites

- **Python 3.x**
- **Google API Key**

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Vikramssamyal/youtube-subtitle-extractor.git
   cd youtube-subtitle-extractor
