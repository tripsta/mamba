from __future__ import absolute_import
import socket
import time
import os
import codecs

from twisted.internet import reactor, defer
from twisted.python import log

from seeya.conversation_log.models import SearchConversationLog, ConversationLog
from mamba.helpers import log_with_traceback
from mamba.workers.gearmanized import Gearmanized

HOST_NAME = socket.gethostname()


class GearmanLogConversationService(Gearmanized):
    job_name = "log_conversation"

    def invoke(self, conversation):
        try:
            if self._is_development():
                reactor.callInThread(self._log_to_file, **conversation)
            reactor.callLater(0, self._log_to_mongo, **conversation)
        except Exception, e:
            log.err(e)
        return True

    @defer.inlineCallbacks
    def _log_to_mongo(self, **kwargs):
        raise NotImplementedError("Subclasses should implement this!")

    def _log_to_file(self, **kwargs):
        raise NotImplementedError("Subclasses should implement this!")

    def _is_development(self):
        raise NotImplementedError("Subclasses should implement this!")

log_conversation = GearmanLogConversationService
