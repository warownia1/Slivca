import mongomock
import pytest

import slivka.db
from slivka.db.documents import JobRequest


@pytest.fixture('module')
def mock_mongo():
    slivka.db.mongo = mongomock.MongoClient()
    slivka.db.database = slivka.db.mongo.slivkadb
    yield slivka.db.database
    del slivka.db.database
    del slivka.db.mongo


@pytest.fixture('function')
def insert_jobs():
    all_jobs = []
    collection = JobRequest.get_collection(slivka.db.database)

    def insert(jobs):
        all_jobs.extend(jobs)
        collection.insert_many(jobs)

    yield insert
    collection.delete_many({'_id': {'$in': [job['_id'] for job in all_jobs]}})