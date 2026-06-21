# blog/urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='blog-detail'),
    path('post/new/', views.PostCreateView.as_view(), name='blog-create'),
    path('post/<int:pk>/update/', views.PostUpdateView.as_view(), name='blog-update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='blog-delete'),
    
    # New URLs for AMR features
    path('sector/<slug:sector_slug>/', views.SectorDetailView.as_view(), name='sector-posts'),
    path('search/', views.SearchResultsView.as_view(), name='search-results'),
    path('alerts/', views.AlertListView.as_view(), name='alert-list'),
    path('statistics/', views.statistics_dashboard, name='statistics'),
    path('experts/', views.expert_list, name='expert-list'),
    path('expert/<int:pk>/', views.expert_detail, name='expert-detail'),
    path('contact-expert/<int:pk>/', views.contact_expert, name='contact-expert'),
    path('policies/', views.policy_list, name='policy-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)