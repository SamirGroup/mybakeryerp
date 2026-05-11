from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib import admin

        admin.site.site_header = 'Bunyod NON CRM'
        admin.site.site_title = 'Bunyod NON CRM'
        admin.site.index_title = 'Ma’lumotlar bazasi'
