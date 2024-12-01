from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('votes/', views.votes, name='votes'),
    path('votes_candidates/<int:election_id>/', views.votes_candidates, name='votes_candidates'),  # Updated URL pattern
    path('guidelines/', views.guidelines, name='guidelines'),
    path('get-positions/<int:election_id>/', views.get_positions, name='get_positions'),
    path('logout/', views.logout, name='logout'), 
    # path( 'submit_vote/<int:candidate_id>/<int:election_id>/<int:position_id>/<int:student_id>/', views.submit_vote, name='submit_vote'),
    path('submit-vote/', views.submit_votes, name='submit-votes'),
    path('results/<int:election_id>/', views.results_page, name='results'),

]
