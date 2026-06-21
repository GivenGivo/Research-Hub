from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField  # If you have CKEditor installed

class Sector(models.Model):
    """Health, Agriculture, Environment"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Changed to allow null
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class", blank=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a unique slug for sector
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Sector.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class ThreatLevel(models.Model):
    """CRITICAL, HIGH, MEDIUM, LOW"""
    LEVEL_CHOICES = [
        ('CRITICAL', '🔴 Critical'),
        ('HIGH', '🟠 High'),
        ('MEDIUM', '🟡 Medium'),
        ('LOW', '🟢 Low'),
    ]
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='MEDIUM')
    color = models.CharField(max_length=7, default='#FF4444')
    
    def __str__(self):
        return self.level

class Post(models.Model):
    # Basic Information
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True, null=True)  # Changed to allow null
    summary = models.TextField(help_text="Short summary shown in cards", blank=True)
    content = RichTextField(help_text="Full article content with formatting")  # Or use models.TextField()
    
    # Publication Details
    date_posted = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # AMR Specific Fields
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    threat_level = models.ForeignKey(ThreatLevel, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="e.g., Lusaka, Ndola, Livingstone")
    
    # Statistics (for the dashboard cards)
    statistic_value = models.CharField(max_length=50, blank=True, help_text="e.g., 34%")
    statistic_change = models.CharField(max_length=20, blank=True, help_text="e.g., ↑ 12% in 6m")
    statistic_label = models.CharField(max_length=100, blank=True, help_text="e.g., ICU Resistance")
    
    # Cost/Impact Data
    cost_estimate = models.CharField(max_length=100, blank=True, help_text="e.g., $47 Million")
    cost_description = models.CharField(max_length=200, blank=True, help_text="e.g., extra beds")
    
    # Action Items
    action_items = models.TextField(blank=True, help_text="Bullet points of action items")
    
    # Media & Downloads
    featured_image = models.ImageField(upload_to='research_images/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='research_pdfs/', blank=True, null=True)
    infographic = models.FileField(upload_to='infographics/', blank=True, null=True)
    
    # Engagement
    views_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_alert = models.BooleanField(default=False, help_text="Show as CRITICAL ALERT")
    
    # Metadata
    references = models.TextField(blank=True, help_text="Reference links or citations")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated tags")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Create a unique slug from title
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Check if slug exists and make it unique
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog-detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_posted']

class Expert(models.Model):
    """For 'Ask an Expert' feature"""
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    expertise = models.TextField()
    email = models.EmailField()
    photo = models.ImageField(upload_to='experts/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class PolicyDocument(models.Model):
    """For 'Draft Policies' and 'References'"""
    title = models.CharField(max_length=300)
    document_type = models.CharField(max_length=50, choices=[
        ('POLICY', 'Draft Policy'),
        ('REFERENCE', 'Reference'),
        ('INFOGRAPHIC', 'Infographic'),
        ('PLAYBOOK', 'Playbook'),
    ])
    file = models.FileField(upload_to='documents/')
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title