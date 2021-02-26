import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import fields, indexes
from django.utils.translation import gettext_lazy as _

from model_utils.fields import AutoCreatedField
from model_utils.models import TimeStampedModel


class TimeStampedWithId(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class FilmGenre(TimeStampedWithId):
    name = models.CharField(_('название'), max_length=255, null=False, unique=True)
    description = models.TextField(_('описание'), blank=True)
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True)

    class Meta:
        verbose_name = (_('жанр'))
        verbose_name_plural = (_('жанры'))
        db_table = 'djfilmgenre'

    def __str__(self) -> str:
        return self.name


class FilmType(TimeStampedWithId):
    name = models.CharField(_('название'), max_length=255, null=False, unique=True)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = (_('тип'))
        verbose_name_plural = (_('типы'))
        db_table = 'djfilmtype'

    def __str__(self) -> str:
        return self.name


class FilmPerson(TimeStampedWithId):
    full_name = models.CharField(_('полное имя'), max_length=255, blank=False)
    imdb_nconst = models.CharField(_('imdb id'), max_length=255, blank=True, null=True)
    birth_date = models.DateField(_('дата рождения'), blank=True, null=True)
    death_date = models.DateField(_('дата смерти'), blank=True, null=True)
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True)

    class Meta:
        verbose_name = (_('персона'))
        verbose_name_plural = (_('люди'))
        db_table = 'djfilmperson'

    def __str__(self) -> str:
        return self.full_name


class FilmCrewRole(models.TextChoices):
    ACTOR = 'actor', _('актер')
    DIRECTOR = 'director', _('режисер')
    WRITER = 'writer', _('сценарист')


class FilmWork(TimeStampedWithId):
    imdb_tconst = models.CharField(_('imdb id'), max_length=255)
    imdb_pconst = models.CharField(_('imdb parrent'), max_length=255, blank=True, null=True)
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания'))
    end_date = models.DateField(_('дата завершения'), blank=True, null=True)
    certificate = models.TextField(_('возрастные ограничения'), blank=True)
    file_path = models.CharField(_('имя файла'), max_length=255, blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], default=0.0)
    season_number = models.PositiveSmallIntegerField(_('сезон'), blank=True, null=True)
    episode_number = models.PositiveSmallIntegerField(_('эпизод'), blank=True, null=True)
    genres = models.ManyToManyField(FilmGenre, through='FilmWorkGenre')
    crew = models.ManyToManyField(FilmPerson, through='FilmWorkPerson')
    type = models.ForeignKey(
        FilmType,
        db_column='type_id',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = (_('кинопроизведение'))
        verbose_name_plural = (_('кинопроизведения'))
        db_table = 'djfilmwork'

    def __str__(self) -> str:
        return self.title


class FilmWorkGenre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True)
    created = AutoCreatedField(_('создано'))
    film_work = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        FilmGenre,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['genre', 'film_work'], name='uniquie_film_genre')
        ]
        db_table = 'djfilmworkgenre'
        verbose_name = _('жанр кинопроизведения')
        verbose_name_plural = _('жанры кинопроизведения')

    def __str__(self):
        return f'Film: "{self.film_work.title}"  Genre: "{self.genre.name}"'


class FilmWorkPerson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    migrated_from = models.CharField(_('мигрировано'), max_length=255, blank=True)
    created = AutoCreatedField(_('создано'))
    film_work = models.ForeignKey(
        FilmWork,
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        FilmPerson,
        on_delete=models.CASCADE,
    )
    role = models.CharField(_('роль'), max_length=20, choices=FilmCrewRole.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'person', 'film_work'], name='uniquie_film_work_person_role')
        ]
        db_table = 'djfilmworkperson'
        verbose_name = _('участник съёмочной группы')
        verbose_name_plural = _('съёмочная группа')

    def __str__(self):
        return f'{self.person.full_name} - {self.film_work.title} - {self.role}'
