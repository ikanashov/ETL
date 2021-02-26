from django.contrib import admin

from .models import FilmGenre, FilmPerson, FilmType, FilmWork, FilmWorkGenre, FilmWorkPerson


@admin.register(FilmGenre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description'
    )
    search_fields = ('name', )
    fields = (
        'name',
        'description',
    )


@admin.register(FilmType)
class TypeAdmin(admin.ModelAdmin):
    pass


class FilmGenreInline(admin.TabularInline):
    model = FilmWorkGenre
    extra = 0
    fields = (
        'genre',
    )


class FilmWorkPersonInline(admin.TabularInline):
    model = FilmWorkPerson
    extra = 0
    fields = (
        'person',
        'film_work',
        'role',
    )


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = (
        'imdb_tconst',
        'title',
        'type',
        'creation_date'
    )
    list_filter = (
        'type',
        'genres',
    )
    search_fields = (
        'title',
        'imdb_tconst',
    )
    fields = (
        ('title', 'type', 'rating', ),
        ('creation_date', 'end_date', ),
        ('imdb_tconst', 'imdb_pconst', ),
        'description',
        'certificate',
        'file_path',
        ('season_number', 'episode_number', ),
    )
    inlines = [
        FilmGenreInline,
        FilmWorkPersonInline,
    ]


@admin.register(FilmWorkPerson)
class FilmWorkPersonAdmin(admin.ModelAdmin):
    list_filter = (
        'role',
    )


@admin.register(FilmPerson)
class PersonAdmin(admin.ModelAdmin):
    search_fields = [
        'full_name',
    ]
    inlines = [
        FilmWorkPersonInline,
    ]
