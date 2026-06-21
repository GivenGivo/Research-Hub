from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear

from .models import Post, Sector, ThreatLevel, Expert, PolicyDocument
from .forms import PostForm, ExpertContactForm

# ============== BASIC VIEWS ==============

def about(request):
    """About page - Public access"""
    return render(request, 'blog/about.html', {'title': "About Page"})


def home(request):
    """Home page with all the dashboard components - Public access"""
    # Get all posts
    posts = Post.objects.all().order_by('-date_posted')
    
    # Pagination (10 posts per page)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get sectors for sidebar
    sectors = Sector.objects.all()
    
    context = {
        'posts': page_obj,
        'alerts': Post.objects.filter(is_alert=True, threat_level__level='CRITICAL')[:3],
        'featured': Post.objects.filter(is_featured=True)[:5],
        'sectors': sectors,
        'latest_stats': Post.objects.exclude(statistic_value='')[:6],
        'experts': Expert.objects.filter(is_available=True)[:3],
        'total_posts': Post.objects.count(),
        'total_alerts': Post.objects.filter(is_alert=True).count(),
        'recent_policies': PolicyDocument.objects.all()[:5],
        'title': 'ZedAMR - AMR Intelligence Dashboard',
    }
    return render(request, 'blog/home.html', context)


# ============== POST VIEWS ==============

class PostListView(ListView):
    """List all posts with filtering - Public access"""
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.all().order_by('-date_posted')
        
        # Filter by sector
        sector = self.request.GET.get('sector')
        if sector:
            queryset = queryset.filter(sector__slug=sector)
        
        # Filter by threat level
        threat = self.request.GET.get('threat')
        if threat:
            queryset = queryset.filter(threat_level__level=threat)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(location__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add extra context for dashboard
        context['alerts'] = Post.objects.filter(is_alert=True)[:3]
        context['featured'] = Post.objects.filter(is_featured=True)[:5]
        context['sectors'] = Sector.objects.all()
        context['threat_levels'] = ThreatLevel.objects.all()
        context['latest_stats'] = Post.objects.exclude(statistic_value='')[:6]
        context['experts'] = Expert.objects.filter(is_available=True)[:3]
        context['title'] = 'ZedAMR - Research Hub'
        
        # Filter context
        context['current_sector'] = self.request.GET.get('sector', '')
        context['current_threat'] = self.request.GET.get('threat', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['total_posts'] = Post.objects.count()
        context['total_alerts'] = Post.objects.filter(is_alert=True).count()
        
        return context


class PostDetailView(DetailView):
    """Detailed view of a single post - Public access"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.views_count += 1
        post.save()
        
        # Related posts (same sector, exclude current)
        context['related_posts'] = Post.objects.filter(
            sector=post.sector
        ).exclude(id=post.id)[:3]
        
        # If no related posts in same sector, show recent posts
        if not context['related_posts']:
            context['related_posts'] = Post.objects.exclude(
                id=post.id
            ).order_by('-date_posted')[:3]
        
        # Experts
        context['experts'] = Expert.objects.filter(is_available=True)[:3]
        
        # Add all sectors for navigation
        context['sectors'] = Sector.objects.all()
        
        # Add threat level color
        if post.threat_level:
            context['threat_color'] = post.threat_level.color
        
        return context


# ============== SECTOR VIEWS ==============

class SectorDetailView(ListView):
    """View posts by sector - Public access"""
    model = Post
    template_name = 'blog/sector_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.sector = get_object_or_404(Sector, slug=self.kwargs.get('sector_slug'))
        return Post.objects.filter(sector=self.sector).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sector'] = self.sector
        context['sector_posts_count'] = self.get_queryset().count()
        context['title'] = f"{self.sector.name} - Research"
        context['sectors'] = Sector.objects.all()
        return context


# ============== SEARCH VIEWS ==============

class SearchResultsView(ListView):
    """Advanced search results - Public access"""
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        sector = self.request.GET.get('sector', '')
        threat = self.request.GET.get('threat', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        
        queryset = Post.objects.all()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__icontains=query) |
                Q(author__username__icontains=query) |
                Q(location__icontains=query)
            )
        
        if sector:
            queryset = queryset.filter(sector__slug=sector)
        
        if threat:
            queryset = queryset.filter(threat_level__level=threat)
        
        if date_from:
            queryset = queryset.filter(date_posted__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date_posted__lte=date_to)
        
        return queryset.order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['sectors'] = Sector.objects.all()
        context['threat_levels'] = ThreatLevel.objects.all()
        context['title'] = 'Search Results'
        context['total_results'] = self.get_queryset().count()
        return context


# ============== ALERT VIEWS ==============

class AlertListView(ListView):
    """View all critical alerts - Public access"""
    model = Post
    template_name = 'blog/alerts.html'
    context_object_name = 'alerts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(
            is_alert=True
        ).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Critical Alerts'
        context['total_alerts'] = self.get_queryset().count()
        context['sectors'] = Sector.objects.all()
        return context


# ============== STATISTICS VIEWS ==============

def statistics_dashboard(request):
    """Dashboard for AMR statistics - Public access"""
    context = {
        'title': 'AMR Statistics Dashboard',
        'total_posts': Post.objects.count(),
        'total_alerts': Post.objects.filter(is_alert=True).count(),
        'posts_by_sector': Sector.objects.annotate(count=Count('researchpost')),
        'posts_by_threat': ThreatLevel.objects.annotate(count=Count('researchpost')),
        'recent_posts': Post.objects.order_by('-date_posted')[:10],
        'top_locations': Post.objects.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'sectors': Sector.objects.all(),
    }
    return render(request, 'blog/statistics.html', context)


# ============== EXPERT VIEWS ==============

def expert_list(request):
    """List all available experts - Public access"""
    experts = Expert.objects.filter(is_available=True)
    context = {
        'experts': experts,
        'title': 'Ask an Expert',
        'total_experts': experts.count(),
        'sectors': Sector.objects.all(),
    }
    return render(request, 'blog/experts.html', context)


def expert_detail(request, pk):
    """View individual expert - Public access"""
    expert = get_object_or_404(Expert, pk=pk)
    context = {
        'expert': expert,
        'title': f'{expert.name} - Expert',
        'sectors': Sector.objects.all(),
    }
    return render(request, 'blog/expert_detail.html', context)


# ============== CRUD OPERATIONS (Admin Only) ==============

class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new research post - Admin only"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        # Only allow admin or staff users to create posts
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Research Post'
        context['form_action'] = 'Create'
        context['sectors'] = Sector.objects.all()
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing post - Admin or Author only"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Research Post'
        context['form_action'] = 'Update'
        context['sectors'] = Sector.objects.all()
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a post - Admin or Author only"""
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Research Post'
        context['sectors'] = Sector.objects.all()
        return context


# ============== POLICY VIEWS ==============

def policy_list(request):
    """List all policy documents - Public access"""
    policies = PolicyDocument.objects.all().order_by('-date_uploaded')
    sectors = Sector.objects.all()
    
    # Filter by sector
    sector_filter = request.GET.get('sector')
    if sector_filter:
        policies = policies.filter(sector__slug=sector_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        policies = policies.filter(document_type=type_filter)
    
    context = {
        'policies': policies,
        'sectors': sectors,
        'current_sector': sector_filter,
        'current_type': type_filter,
        'title': 'Policy Documents',
    }
    return render(request, 'blog/policies.html', context)


# ============== CONTACT/EXPERT FORM ==============

def contact_expert(request, pk):
    """Contact form for experts - Public access"""
    expert = get_object_or_404(Expert, pk=pk)
    
    if request.method == 'POST':
        form = ExpertContactForm(request.POST)
        if form.is_valid():
            # Here you would send email or save to database
            return render(request, 'blog/contact_success.html', {
                'expert': expert,
                'title': 'Message Sent',
                'sectors': Sector.objects.all(),
            })
    else:
        form = ExpertContactForm()
    
    context = {
        'form': form,
        'expert': expert,
        'title': f'Contact {expert.name}',
        'sectors': Sector.objects.all(),
    }
    return render(request, 'blog/contact_expert.html', context)


# ============== API-LIKE ENDPOINTS (Optional) ==============

def get_posts_by_sector_json(request, sector_slug):
    """AJAX endpoint to get posts by sector - Public access"""
    sector = get_object_or_404(Sector, slug=sector_slug)
    posts = Post.objects.filter(sector=sector).values('id', 'title', 'slug', 'date_posted')
    from django.http import JsonResponse
    return JsonResponse(list(posts), safe=False)


def get_latest_stats_json(request):
    """AJAX endpoint for real-time stats - Public access"""
    stats = Post.objects.exclude(statistic_value='').values(
        'id', 'title', 'statistic_value', 'statistic_change', 'statistic_label'
    )[:6]
    from django.http import JsonResponse
    return JsonResponse(list(stats), safe=False)