from django.shortcuts import render
from games.models import Game
from django.db.models import Q
from mapreduce import search_games

def search_games_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        db_paths = ['db1.sqlite3', 'db2.sqlite3', 'db3.sqlite3']
        results = search_games(query, db_paths)

    return render(request, 'index.html', {'query': query, 'results': results})
