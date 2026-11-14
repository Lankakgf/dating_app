from django.contrib import admin

from .models import Block, Match, Report, Swipe


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reported', 'reporter', 'reason', 'resolved', 'created_at')
    list_filter = ('reason', 'resolved')
    search_fields = ('reported__username', 'reporter__username')


admin.site.register(Swipe)
admin.site.register(Match)
admin.site.register(Block)