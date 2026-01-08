from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        """Configure offline mode for model loading"""
        import os
        # Disable HF model online lookup to avoid network issues
        os.environ['HF_DATASETS_OFFLINE'] = '1'
        # Use local cache only
        os.environ['TRANSFORMERS_OFFLINE'] = '1'