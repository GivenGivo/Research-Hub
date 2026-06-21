# blog/context_processors.py

from .models import Post, Sector, ThreatLevel, Expert, PolicyDocument
from django.contrib.admin.models import LogEntry

def admin_context(request):
    # Only add context for admin pages
    if request.path.startswith('/admin/'):
        return {
            'total_posts': Post.objects.count(),
            'total_alerts': Post.objects.filter(is_alert=True).count(),
            'total_sectors': Sector.objects.count(),
            'total_experts': Expert.objects.count(),
            'total_threats': ThreatLevel.objects.count(),
            'total_policies': PolicyDocument.objects.count(),
            'recent_posts': Post.objects.order_by('-date_posted')[:10],
            'recent_actions': LogEntry.objects.select_related(
                'user', 'content_type'
            ).order_by('-action_time')[:10],
        }
    return {}