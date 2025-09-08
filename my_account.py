import pjsua2 as pj

class Account(pj.Account):
    def __init__(self, sip_uri):
        pj.Account.__init__(self)
        self.cfg = pj.AccountConfig()
        self.cfg.idUri = sip_uri
        self.create(self.cfg)
    
    def onIncomingCall(self, prm):
        return super().onIncomingCall(prm)