from django.apps import AppConfig


class CinemaConfig(AppConfig):
    name = 'cinema'
    movies_per_page = 50

    def ready(self):
        import cinema.signals
