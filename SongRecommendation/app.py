import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster_and_urls(music_title):
    try:
        response = requests.get(f"https://saavn.dev/api/search/songs?query={music_title}")
        response.raise_for_status()
        data = response.json()

        if 'data' in data and isinstance(data['data']['results'], list) and len(data['data']['results']) > 0:
            result = data['data']['results'][0]
            poster_url = result['image'][2]['url']
            download_urls = result['downloadUrl']

            # Extract URLs and sort by quality (highest quality first)
            urls = {quality['quality']: quality['url'] for quality in download_urls}
            sorted_qualities = sorted(urls.keys(), key=lambda x: int(x.replace('kbps', '')), reverse=True)
            default_quality = sorted_qualities[0] if sorted_qualities else None
            default_url = urls.get(default_quality)

            return poster_url, default_url
        else:
            raise ValueError("Unexpected data format or no results found.")

    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None
    except (IndexError, KeyError, ValueError) as e:
        st.error(f"Error fetching poster or URL: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None

def recommender(song):
    song_index = songs[songs['track_name'] == song].index
    if not song_index.empty:
        song_index = song_index[0]
        distances = similarity[song_index]
        song_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_songs = []

        for i in song_list:
            song_id = i[0]
            song_name = songs.iloc[i[0]].track_name
            recommended_songs.append(song_name)
        return recommended_songs
    else:
        return []

# Streamlit Layout
st.set_page_config(page_title="Stairway to Your Musical Heaven", page_icon="🎵", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #121212;
            color: #ffffff;
        }
        .title {
            text-align: center;
            color: #1DB954;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .subtitle {
            text-align: center;
            color: #B3B3B3;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .recommendation-card {
            background: #1F1F1F;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .recommendation-card img {
            border-radius: 8px;
        }
        .recommendation-card h3 {
            color: #ffffff;
        }
        .recommendation-card audio {
            width: 100%;
        }
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            padding: 10px;
            background: #1F1F1F;
            color: #B3B3B3;
            font-size: 0.8rem;
            border-top-right-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description with custom styling
st.markdown("<div class='title'>Stairway to Your Musical Heaven</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Discover your next favorite track with our advanced music recommendation system.</div>", unsafe_allow_html=True)

# Load song list and similarity matrix
song_list = pickle.load(open('SongRecommendation/musicForLovers.pkl', 'rb'))
songs = pd.DataFrame(song_list)
similarity = pickle.load(open('SongRecommendation/similarityFounded.pkl', 'rb'))

# User selects a song
selected_song = st.selectbox(
    'Which song would you like to recommend?',
    songs['track_name'].values,
    key='select_song'
)

if st.button('Recommend'):
    if selected_song in songs['track_name'].values:
        recommendations = recommender(selected_song)
        if recommendations:
            st.write(f"Recommendations for **{selected_song}**:")

            # Create an expander to make the recommendations scrollable
            with st.expander("See Recommendations", expanded=True):
                for song in recommendations:
                    poster_url, download_url = fetch_poster_and_urls(song)

                    # Display each song's details in a styled container
                    with st.container():
                        st.markdown(f"""
                            <div class='recommendation-card'>
                                <img src="{poster_url}" width="150" />
                                <h3>{song}</h3>
                                <div>
                                    {f'<audio controls><source src="{download_url}" type="audio/mp3"></audio>' if download_url else "No preview available."}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning(f"No recommendations found for **{selected_song}**.")
    else:
        st.warning(f"The song **{selected_song}** is not in the playlist. Please select another song.")

# Footer with credit
st.markdown("<div class='footer'>Developed by Adarsh Verma</div>", unsafe_allow_html=True)
