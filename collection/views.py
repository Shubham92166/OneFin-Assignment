from django.shortcuts import render

# Create your views here.

def get_top_genres_from_all_movies(all_my_movies):
    all_genres = []
    for movie in all_my_movies:
        genre = (movie.get('genres')).split(',')
        all_genres.extend(genre)

    genres_cleaned_data = []

    for pair in all_my_movies:
        genres_cleaned_data.extend(pair['genres'].split(','))

    counter = {}
    for genre in genres_cleaned_data:
        counter[genre] = counter.get(genre, 0) + 1
    
    sorted_counter = sorted(counter.items(), key = lambda val : val[1], reverse=True)
    
    top_genres = []

    TOP_GENRES_TO_FETCH = 3

    for _ in range(TOP_GENRES_TO_FETCH):
        top_genres.append(sorted_counter[_][0])
    
    return top_genres