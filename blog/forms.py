from django import forms
from django.forms import ModelForm, Textarea, Select, TextInput, FileInput, CheckboxInput
from .models import Post, Expert, PolicyDocument

# Try to import CKEditor, but don't fail if it's not installed
try:
    from ckeditor.widgets import CKEditorWidget
    CKEDITOR_AVAILABLE = True
except ImportError:
    CKEDITOR_AVAILABLE = False
    CKEditorWidget = None


class PostForm(ModelForm):
    """Form for creating/updating research posts"""
    
    class Meta:
        model = Post
        fields = [
            'title', 'sector', 'threat_level', 'location',
            'summary', 'content', 'statistic_value', 'statistic_change',
            'statistic_label', 'cost_estimate', 'cost_description',
            'action_items', 'featured_image', 'pdf_file', 'infographic',
            'is_alert', 'is_featured', 'references', 'tags'
        ]
        widgets = {
            'title': TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter research title'}),
            'summary': Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Brief summary of the research'}),
            'action_items': Textarea(attrs={'rows': 5, 'class': 'form-control', 
                                           'placeholder': 'Enter action items, one per line'}),
            'references': Textarea(attrs={'rows': 3, 'class': 'form-control', 
                                         'placeholder': 'Enter references or links'}),
            'tags': TextInput(attrs={'class': 'form-control', 
                                    'placeholder': 'Comma separated tags: e.g., AMR, Zambia, ICU'}),
            'location': TextInput(attrs={'class': 'form-control', 
                                        'placeholder': 'e.g., Lusaka, Ndola, Livingstone'}),
            'statistic_value': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 34%'}),
            'statistic_change': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ↑ 12% in 6m'}),
            'statistic_label': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ICU Resistance'}),
            'cost_estimate': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $47 Million'}),
            'cost_description': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., extra beds'}),
            'sector': Select(attrs={'class': 'form-control'}),
            'threat_level': Select(attrs={'class': 'form-control'}),
            'featured_image': FileInput(attrs={'class': 'form-control-file'}),
            'pdf_file': FileInput(attrs={'class': 'form-control-file'}),
            'infographic': FileInput(attrs={'class': 'form-control-file'}),
            'is_alert': CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Research Title',
            'sector': 'Sector',
            'threat_level': 'Threat Level',
            'location': 'Location',
            'summary': 'Summary',
            'content': 'Full Content',
            'statistic_value': 'Statistic Value',
            'statistic_change': 'Statistic Change',
            'statistic_label': 'Statistic Label',
            'cost_estimate': 'Cost Estimate',
            'cost_description': 'Cost Description',
            'action_items': 'Action Items',
            'featured_image': 'Featured Image',
            'pdf_file': 'PDF File (Full Report)',
            'infographic': 'Infographic',
            'is_alert': 'Show as Critical Alert',
            'is_featured': 'Feature on Homepage',
            'references': 'References',
            'tags': 'Tags',
        }
        help_texts = {
            'action_items': 'Enter each action item on a new line',
            'references': 'Enter references as text or links',
            'tags': 'Separate tags with commas',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If CKEditor is available, use it for the content field
        if CKEDITOR_AVAILABLE and CKEditorWidget:
            self.fields['content'].widget = CKEditorWidget()
        else:
            self.fields['content'].widget = Textarea(attrs={
                'rows': 15, 
                'class': 'form-control', 
                'placeholder': 'Full article content...'
            })


class ExpertContactForm(forms.Form):
    """Form for contacting experts"""
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'})
    )
    subject = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of your message'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Your message...'})
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not '@' in email:
            raise forms.ValidationError("Please enter a valid email address")
        return email


class ExpertForm(ModelForm):
    """Form for creating/updating experts"""
    class Meta:
        model = Expert
        fields = ['name', 'title', 'organization', 'expertise', 'email', 'photo', 'is_available']
        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'title': TextInput(attrs={'class': 'form-control'}),
            'organization': TextInput(attrs={'class': 'form-control'}),
            'expertise': Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control', 'type': 'email'}),
            'photo': FileInput(attrs={'class': 'form-control-file'}),
            'is_available': CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PolicyDocumentForm(ModelForm):
    """Form for uploading policy documents"""
    class Meta:
        model = PolicyDocument
        fields = ['title', 'document_type', 'file', 'sector']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'document_type': Select(attrs={'class': 'form-control'}),
            'file': FileInput(attrs={'class': 'form-control-file'}),
            'sector': Select(attrs={'class': 'form-control'}),
        }