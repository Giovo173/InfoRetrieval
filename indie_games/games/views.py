from django.shortcuts import render
from django.db.models import Q
from games.mapreduce import search_games
from .models import ClusteredGame

def search_games_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        db_table_map = {
        './steam.db': 'steam',  # Replace with the correct table name for steam.db
        './itchio.db': 'itchio',  # Replace with the correct table name for itchio.db
        }
        results = search_games(query, db_table_map)

    return render(request, 'index.html', {'query': query, 'results': results})

def clustered_games_view(request):
    selected_cluster = request.GET.get('cluster')
    clusters = ClusteredGame.objects.values('cluster', 'cluster_label').distinct()
    games = ClusteredGame.objects.filter(cluster=selected_cluster) if selected_cluster else ClusteredGame.objects.all()
    context = {'clusters': clusters, 'games': games, 'selected_cluster': selected_cluster}
    return render(request, 'clustered_games.html', context)
