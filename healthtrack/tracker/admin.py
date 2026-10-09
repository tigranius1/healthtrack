from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('user', 'measured_at', 'systolic', 'diastolic', 'pulse', 'is_hypertensive')
    list_filter = ('user', 'measured_at')
    search_fields = ('user__username', 'note')