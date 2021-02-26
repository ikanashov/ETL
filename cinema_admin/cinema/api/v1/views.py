from cinema.apps import CinemaConfig
from cinema.models import FilmCrewRole, FilmWork

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView


class Movies(BaseListView):
    model = FilmWork
    queryset = model.objects.select_related('type')
    ordering = 'id'
    paginate_by = CinemaConfig.movies_per_page
    http_method_names = ['get']
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        self.queryset = self.queryset.annotate(
            actors=ArrayAgg('crew__full_name', filter=Q(filmworkperson__role=FilmCrewRole.ACTOR), distinct=True)
        )
        self.queryset = self.queryset.annotate(
            directors=ArrayAgg('crew__full_name', filter=Q(filmworkperson__role=FilmCrewRole.DIRECTOR), distinct=True)
        )
        self.queryset = self.queryset.annotate(
            writers=ArrayAgg('crew__full_name', filter=Q(filmworkperson__role=FilmCrewRole.WRITER), distinct=True)
        )
        self.queryset = self.queryset.annotate(genres_name=ArrayAgg('genres__name', distinct=True))
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            self.queryset = self.queryset.filter(id__exact=pk)
        queryset = super().get_queryset()
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, currentpage, pageobjects, is_paginated = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': currentpage.previous_page_number() if currentpage.has_previous() else None,
            'next': currentpage.next_page_number() if currentpage.has_next() else None,
            'results': []
        }
        for film in pageobjects:
            film_dict = {
                'id':  film.id,
                'title': film.title,
                'description': film.description,
                'creation_date': film.creation_date,
                'rating': film.rating,
                'type': film.type.name,
                'genres': film.genres_name,
                'actors': film.actors,
                'directors': film.directors,
                'writers': film.writers,
            }
            if is_paginated:
                context['results'].append(film_dict)
            else:
                return film_dict
        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
