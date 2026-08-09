from django.contrib import admin
from .models import AnalysisSession, SentimentItem
# Register your models here.

admin.site.register(AnalysisSession)
admin.site.register(SentimentItem)