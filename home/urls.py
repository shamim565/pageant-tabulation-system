from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    
    # Judges
    path('judges/', views.judge_list, name='judge_list'),
    path('judges/create/', views.judge_create, name='judge_create'),
    path('judges/<int:event_id>/edit/', views.event_edit, name='judge_edit'),
    path('judges/<int:event_id>/delete/', views.event_delete, name='judge_delete'),
    path('events/<int:event_id>/judges/', views.event_judge_list, name='event_judge_list'),
    path('events/<int:event_id>/judges/add/', views.event_judge_add, name='event_judge_add'),
    path('events/<int:event_id>/judges/<int:judge_id>/delete/', views.event_judge_delete, name='event_judge_delete'),

    # Criterias
    path('events/<int:event_id>/criterias/', views.criteria_list, name='criteria_list'),
    path('events/<int:event_id>/criterias/add/', views.criteria_add, name='criteria_add'),
    path('events/<int:event_id>/criterias/<int:criteria_id>/edit/', views.criteria_edit, name='criteria_edit'),
    path('events/<int:event_id>/criterias/<int:criteria_id>/delete/', views.criteria_delete, name='criteria_delete'),

    # Scores
    path('events/<int:event_id>/scores/', views.score_list, name='score_list'),
    
    # Admin URLs
    path('add_candidate/', views.add_candidate, name='add_candidate'),
    path('edit_candidate/<int:id>/', views.edit_candidate, name='edit_candidate'),
    path('delete_candidate/<int:id>/', views.delete_candidate, name='delete_candidate'),
    path('add_criteria/', views.criteria_add, name='add_criteria'),
    path('edit_criteria/<int:id>/', views.criteria_edit, name='edit_criteria'),
    path('delete_criteria/<int:id>/', views.criteria_delete, name='delete_criteria'),
    path('create_judge/', views.create_judge, name='create_judge'),
    # Judge URLs (unchanged for now)
    path('judge_dashboard/', views.judge_dashboard, name='judge_dashboard'),
]