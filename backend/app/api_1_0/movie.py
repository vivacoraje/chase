# -*- coding: utf-8 -*-
from flask_restful import Resource
from ..extensions import api
from ..models import Movie
from flask import request
from flask import current_app


class MovieApi(Resource):

    def get(self, id):
        m = Movie.query.filter_by(id=id).first_or_404()
        return m.to_dict()


api.add_resource(MovieApi, '/api/movies/<id>')


class MoviesApi(Resource):

    def get(self):
        page = request.args.get('page', 1, type=int)
        if Movie.query.all() is None:
            return []
        movies_pagination = Movie.query.paginate(
            page, per_page=current_app.config['PER_PAGE'], error_out=False
        )
        movies = movies_pagination.items
        return [m.to_dict() for m in movies]


api.add_resource(MoviesApi, '/api/movies')
