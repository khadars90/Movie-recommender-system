import streamlit as st
import pickle
import pandas as pd
import requests
import random
import time

# --- Fetch Poster Function ---
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    """Fetch poster URL from TMDB with fallback and retry"""
    base_url = "https://api.themoviedb.org/3/movie/{}?api_key=208278546ddcf1436973b6e450bb55e0&language=en-US"
    for attempt in range(2):  # retry twice in case of temporary network issue
        try:
            response = requests.get(base_url.format(movie_id), timeout=5)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
            else:
                # fallback placeholder if TMDB has no poster
                return "https://via.placeholder.com/500x750?text=No+Poster+Available"
        except Exception:
            time.sleep(random.uniform(0.3, 0.7))  # small random delay before retry
    return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"

# --- Recommend Function ---
def recommend(movie):
    # Find movie index
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    # Sort and get top 5 most similar
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# --- Load Data ---
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# --- Streamlit UI ---
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie you like:",
    movies['title'].values
)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie_name)

    # Display results in 5 columns
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.text(names[idx])
        col.image(posters[idx])
