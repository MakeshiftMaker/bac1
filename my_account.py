import pjsua2 as pj
import my_call

class Account(pj.Account):
    def __init__(self, sip_uri):
        pj.Account.__init__(self)
        self.cfg = pj.AccountConfig()
        self.cfg.idUri = sip_uri
        self.create(self.cfg)
    
    def onIncomingCall(self, prm):
        call = pj.Call(self, prm.callId)
        call_info = call.getInfo()
        print(f"Incoming call from {call_info.remoteUri}")
        #print(f"Will wait for media transport before answering")
        print(f"Accepting Automatically")
        
        call_prm = pj.CallOpParam()
        call_prm.statusCode = pj.PJSIP_SC_OK
        call.answer(call_prm)
        
    def call(self, target_uri):
        call = my_call.Call(self, peer_uri=target_uri)
        call_param = pj.CallOpParam()
        call.makeCall(target_uri, call_param)
        return call