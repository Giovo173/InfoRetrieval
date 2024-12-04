from django.shortcuts import render
from games.models import Game
from django.db.models import Q
from mapreduce import perform_query

def search_games(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        db_paths = ['db1.sqlite3', 'db2.sqlite3', 'db3.sqlite3']
        results = perform_query(query, db_paths)

    return render(request, 'search_results.html', {'query': query, 'results': results})