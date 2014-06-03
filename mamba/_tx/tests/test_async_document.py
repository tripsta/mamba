from collections import namedtuple
from mamba.test import unittest
from twisted.internet import defer
from mamba._tx.async_document import AsyncDocument

MongoConfig = namedtuple("MongoConfig", ["port", "host", "pool_size", "database"])
MongoSection = namedtuple("Section", ["custom"])
ServiceSection = namedtuple("ServiceSection", ["service"])
ConfigSection = namedtuple("ConfigSection", ["config"])


CUSTOM_CONF = ConfigSection(config=ServiceSection(
    service=MongoSection(custom=MongoConfig(port=27017,
                                            host="localhost",
                                            database="mamba_test",
                                            pool_size=1))))

class MyCustomConfigDocument(AsyncDocument):
    __collection_name__ = "custom_config_collection"
    __configsection__ = "custom"
    __CONFIG__ = CUSTOM_CONF

class AsyncDocumentTestCase(unittest.TestCase):

    @defer.inlineCallbacks
    def tearDown(self):
        yield AsyncDocument.reset()

    @defer.inlineCallbacks
    def test_drop_database(self):
        doc = MyCustomConfigDocument({"foo": "bar"})
        yield doc.save()
        yield doc.drop_database()
