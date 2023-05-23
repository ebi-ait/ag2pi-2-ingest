import os

from hca_ingest.api.ingestapi import IngestApi

INGEST_TOKEN = os.getenv('INGEST_TOKEN', '')


class ReadyIngestApi(IngestApi):

    def __init__(self, ingest_token=INGEST_TOKEN, ingest_api_url='https://api.ingest.staging.archive.data.humancellatlas.org/'):
        super(ReadyIngestApi, self).__init__(ingest_api_url)
        self.setup_ingest_token(ingest_token)

    @staticmethod
    def __correct_token(token_str: str) -> str:
        return token_str if token_str.startswith('Bearer') else f"Bearer {token_str}"

    def setup_ingest_token(self, token):
        token = self.__correct_token(token)
        self.set_token(token)