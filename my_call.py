import pjsua2 as pj


class Call(pj.Call):
    def __init__(self, acc, peer_uri="", chat=None, call_id=pj.PJSUA_INVALID_ID):
        pj.Call.__init__(self, acc, call_id)
        self.acc = acc
        self.peerUri = peer_uri
        self.chat = chat
        self.connected = False
        self.onhold = False
