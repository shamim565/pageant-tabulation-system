from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthenticationForm


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(
        template_name='home/login.html',
        authentication_form=CustomAuthenticationForm 
    ), name='login'),
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
    path('judges/<int:id>/edit/', views.judge_edit, name='judge_edit'),
    path('judges/<int:id>/delete/', views.judge_delete, name='judge_delete'),

    # Scores
    path('event/<int:event_id>/scores/', views.event_scores, name='event_scores'),
    path('scoring/<int:event_id>/', views.scoring_page, name='scoring_page'),
    
    # Admin URLs
    path('create_judge/', views.create_judge, name='create_judge'),
    path('judge_dashboard/', views.judge_dashboard, name='judge_dashboard'),
]