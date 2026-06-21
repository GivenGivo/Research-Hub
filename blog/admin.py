# blog/admin.py

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.db.models import Count
from .models import Post, Sector, ThreatLevel, Expert, PolicyDocument

# ============================================================
# Custom Admin Site
# ============================================================

class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard stats"""
    site_header = '🔬 ZedAMR Admin Panel'
    site_title = 'ZedAMR Admin'
    index_title = 'Welcome to ZedAMR Admin Dashboard'
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add stats for the dashboard
        extra_context['total_posts'] = Post.objects.count()
        extra_context['total_alerts'] = Post.objects.filter(is_alert=True).count()
        extra_context['total_sectors'] = Sector.objects.count()
        extra_context['total_experts'] = Expert.objects.count()
        extra_context['total_threats'] = ThreatLevel.objects.count()
        extra_context['total_policies'] = PolicyDocument.objects.count()
        
        # Get recent posts
        extra_context['recent_posts'] = Post.objects.order_by('-date_posted')[:10]
        
        # Get recent admin actions
        extra_context['recent_actions'] = LogEntry.objects.select_related(
            'user', 'content_type'
        ).order_by('-action_time')[:10]
        
        return super().index(request, extra_context)

# ============================================================
# Create instance of custom admin site
# ============================================================

custom_admin_site = CustomAdminSite(name='custom_admin')

# ============================================================
# Register Models with Custom Admin Site
# ============================================================

class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def post_count(self, obj):
        count = Post.objects.filter(sector=obj).count()
        return format_html(
            '<span style="background: #eef2ff; color: #4f46e5; padding: 2px 10px; border-radius: 12px; font-weight: 600;">{}</span>',
            count
        )
    post_count.short_description = 'Posts'


class ThreatLevelAdmin(admin.ModelAdmin):
    list_display = ['level', 'color_preview', 'color', 'post_count']
    list_editable = ['color']
    search_fields = ['level']
    
    def color_preview(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 40px; height: 20px; background: {}; border-radius: 4px; border: 1px solid #ddd;"></span>',
            obj.color
        )
    color_preview.short_description = 'Preview'
    
    def post_count(self, obj):
        count = Post.objects.filter(threat_level=obj).count()
        return format_html(
            '<span style="background: #fef2f2; color: #dc2626; padding: 2px 10px; border-radius: 12px; font-weight: 600;">{}</span>',
            count
        )
    post_count.short_description = 'Posts'


class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title_display', 
        'sector', 
        'threat_badge', 
        'statistic_display',
        'date_posted', 
        'status_badges',
        'views_count'
    ]
    list_filter = ['sector', 'threat_level', 'is_alert', 'is_featured', 'date_posted']
    search_fields = ['title', 'content', 'summary', 'tags', 'location', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'date_posted', 'updated_at']
    date_hierarchy = 'date_posted'
    
    fieldsets = (
        ('📄 Basic Information', {
            'fields': ('title', 'slug', 'summary', 'content', 'author')
        }),
        ('🏷️ Classification', {
            'fields': ('sector', 'threat_level', 'location')
        }),
        ('📊 Statistics', {
            'fields': ('statistic_value', 'statistic_change', 'statistic_label', 
                      'cost_estimate', 'cost_description')
        }),
        ('📋 Actions & Resources', {
            'fields': ('action_items', 'featured_image', 'pdf_file', 'infographic')
        }),
        ('⚙️ Settings', {
            'fields': ('is_alert', 'is_featured', 'views_count')
        }),
        ('📚 Metadata', {
            'fields': ('references', 'tags')
        }),
        ('📅 Timeline', {
            'fields': ('date_posted', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_display(self, obj):
        title = obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
        return format_html(
            '<strong style="color: #1a1a2e;">{}</strong>',
            title
        )
    title_display.short_description = 'Title'
    
    def threat_badge(self, obj):
        if obj.threat_level:
            return format_html(
                '<span style="background: {}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">{}</span>',
                obj.threat_level.color, obj.threat_level.level
            )
        return '-'
    threat_badge.short_description = 'Threat'
    
    def statistic_display(self, obj):
        if obj.statistic_value:
            return format_html(
                '<span style="background: #fef3c7; color: #d97706; padding: 2px 10px; border-radius: 12px; font-weight: 600; font-size: 13px;">{}</span>',
                obj.statistic_value
            )
        return '-'
    statistic_display.short_description = 'Statistic'
    
    def status_badges(self, obj):
        badges = []
        if obj.is_alert:
            badges.append('<span style="background: #dc2626; color: white; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 600;">🔴 Alert</span>')
        if obj.is_featured:
            badges.append('<span style="background: #f59e0b; color: white; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 600;">⭐ Featured</span>')
        if obj.location:
            badges.append('<span style="background: #e5e7eb; color: #4b5563; padding: 2px 10px; border-radius: 12px; font-size: 10px; font-weight: 500;">📍 {}</span>'.format(obj.location))
        return format_html(' '.join(badges))
    status_badges.short_description = 'Status'
    
    actions = ['make_alert', 'remove_alert', 'make_featured', 'remove_featured']
    
    def make_alert(self, request, queryset):
        count = queryset.update(is_alert=True)
        self.message_user(request, f'{count} posts marked as ALERT.')
    make_alert.short_description = 'Mark selected as ALERT'
    
    def remove_alert(self, request, queryset):
        count = queryset.update(is_alert=False)
        self.message_user(request, f'{count} posts removed from ALERT.')
    remove_alert.short_description = 'Remove ALERT from selected'
    
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} posts marked as FEATURED.')
    make_featured.short_description = 'Mark selected as FEATURED'
    
    def remove_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} posts removed from FEATURED.')
    remove_featured.short_description = 'Remove FEATURED from selected'


class ExpertAdmin(admin.ModelAdmin):
    list_display = ['name', 'title_display', 'organization', 'availability_badge']
    list_filter = ['is_available', 'organization']
    search_fields = ['name', 'title', 'organization', 'expertise', 'email']
    
    def title_display(self, obj):
        return obj.title[:40] + '...' if len(obj.title) > 40 else obj.title
    title_display.short_description = 'Title'
    
    def availability_badge(self, obj):
        if obj.is_available:
            return format_html(
                '<span style="background: #dcfce7; color: #16a34a; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">✅ Available</span>'
            )
        return format_html(
            '<span style="background: #fee2e2; color: #dc2626; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;">❌ Unavailable</span>'
        )
    availability_badge.short_description = 'Status'


class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ['title_display', 'document_type_badge', 'sector', 'date_uploaded', 'download_count']
    list_filter = ['document_type', 'sector', 'date_uploaded']
    search_fields = ['title']
    readonly_fields = ['download_count', 'date_uploaded']
    
    def title_display(self, obj):
        title = obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        return format_html(
            '<strong style="color: #1a1a2e;">{}</strong>',
            title
        )
    title_display.short_description = 'Title'
    
    def document_type_badge(self, obj):
        colors = {
            'POLICY': '#4f46e5',
            'REFERENCE': '#059669',
            'INFOGRAPHIC': '#d97706',
            'PLAYBOOK': '#7c3aed',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 500;">{}</span>',
            colors.get(obj.document_type, '#6b7280'),
            obj.get_document_type_display()
        )
    document_type_badge.short_description = 'Type'


# ============================================================
# Register ALL models with custom admin site
# ============================================================

custom_admin_site.register(Sector, SectorAdmin)
custom_admin_site.register(ThreatLevel, ThreatLevelAdmin)
custom_admin_site.register(Post, PostAdmin)
custom_admin_site.register(Expert, ExpertAdmin)
custom_admin_site.register(PolicyDocument, PolicyDocumentAdmin)