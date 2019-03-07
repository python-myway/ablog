"""
    flask_elasticsearch
    ~~~~~~~~~~~~~~
    :copyright: (c) 2019 by Misaki.
    :license: .
    # todo
"""
import warnings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from flask import current_app


class FlaskElasticsearch:
    def __init__(self, app=None, **kwargs):
        self.app = app
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, **kwargs):
        if 'ELASTICSEARCH_HOST' not in app.config:
            warnings.warn(
                'None ELASTICSEARCH_HOST, Defaulting ELASTICSEARCH_HOST to "localhost:9200".'
                )
        app.config.setdefault('ELASTICSEARCH_HOST', 'localhost:9200')
        app.config.setdefault('ELASTICSEARCH_HTTP_AUTH', None)

        self.elasticsearch_options = kwargs

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):
            if hasattr(current_app, 'elasticsearch'):
                current_app.elasticsearch = None
            return response_or_exc

    def __getattr__(self, item):
        if current_app is not None:
            if not hasattr(ctx, 'elasticsearch'):
                if isinstance(current_app.config.get('ELASTICSEARCH_HOST'), str):
                    hosts = [current_app.config.get('ELASTICSEARCH_HOST')]
                elif isinstance(current_app.config.get('ELASTICSEARCH_HOST'), list):
                    hosts = current_app.config.get('ELASTICSEARCH_HOST')
                current_app.elasticsearch = Elasticsearch(hosts=hosts,
                                                  http_auth=ctx.app.config.get('ELASTICSEARCH_HTTP_AUTH'),
                                                  **self.elasticsearch_options)

            return getattr(current_app.elasticsearch, item)

    def search(self):
        ...