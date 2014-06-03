from __future__ import print_function, division
from twisted.internet import defer
import cyclone.web
import txmongo
import datetime
from bson.son import SON

class AsyncDocument(object):
    __collection__ = {}
    __collection_name__ = None
    __mongo__ = {}
    __defaultconfigsection__ = "mongo"
    __configsection__ = "mongo"
    __CONFIG__ = None
    __doc_attrs__ = {}

    def __init__(self, kwargs):
        self.__doc_attrs__ = {}
        self.__doc_attrs__.update(kwargs)

    def pre_save(self):
        pass

    @defer.inlineCallbacks
    def save(self):
        now = datetime.datetime.utcnow()
        if not 'dateCreated' in self.__doc_attrs__:
            self.__doc_attrs__["dateCreated"] = now
        pre = yield defer.maybeDeferred(self.pre_save)
        collection = yield self.get_collection()
        res = yield collection.save(self.__doc_attrs__)
        defer.returnValue(res)


    @classmethod
    @defer.inlineCallbacks
    def reset(cls):
        cls.__collection__ = {}
        if len(cls.__mongo__) > 0:
            for k, __mongo__ in cls.__mongo__.iteritems():
                yield __mongo__.disconnect()
        cls.__mongo__ = {}
        defer.returnValue(cls)

    @classmethod
    @defer.inlineCallbacks
    def get_mongo(cls):
        sectionkey = cls.__configsection__
        if not sectionkey in cls.__mongo__:
            CFG = cls._get_config()
            mongo = yield txmongo.MongoConnectionPool(CFG.host, int(CFG.port),
                                                      pool_size=CFG.pool_size)
            cls.__mongo__[sectionkey] = mongo

        defer.returnValue(cls.__mongo__[sectionkey])

    @classmethod
    def get_collection_name(cls):
        coll_name = cls.__collection_name__
        if coll_name is None:
            cfg = cls._get_config()
            coll_name = cfg.collection
        return coll_name

    @classmethod
    @defer.inlineCallbacks
    def get_collection(cls):
        if not cls.__configsection__ in cls.__collection__:
            mongo = yield cls.get_mongo()
            cfg = cls._get_config()
            coll_name = cls.get_collection_name()
            mongo_collection = mongo[cfg.database][coll_name]
            cls.__collection__[cls.__configsection__] = mongo_collection
        defer.returnValue(cls.__collection__[cls.__configsection__])

    @classmethod
    @defer.inlineCallbacks
    def find_one(cls, mongo_id):
        coll = yield cls.get_collection()
        docs = yield coll.find_one(ObjectId(mongo_id))
        defer.returnValue(docs if len(docs) else None)

    @classmethod
    @defer.inlineCallbacks
    def find_all_recent(cls, how_many=25):
        coll = yield cls.get_collection()
        f = txmongo.filter.sort(txmongo.filter.DESCENDING("dateCreated"))
        docs = yield coll.find(limit=how_many, filter=f)
        defer.returnValue(docs)

    @classmethod
    @defer.inlineCallbacks
    def drop_database(cls):
        cmd = SON({"dropDatabase": 1})
        mongo = yield cls.get_mongo()
        cfg = cls._get_config()
        coll_name = cls.get_collection_name()
        db = mongo[cfg.database]
        yield db["$cmd"].find_one(cmd)

    @classmethod
    def _get_config(cls):
        cfg = cls.__CONFIG__.config.service
        return getattr(cfg, cls.__configsection__)
