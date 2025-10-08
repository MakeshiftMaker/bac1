import pjsua2 as pj
import my_call

class Account(pj.Account): # Account dervitive
    def __init__(self, sip_uri): # Constructor for my_account, calls super constructor and then auto adds the uri you want to call
        super().__init__()
        self.cfg = pj.AccountConfig()
        self.cfg.idUri = sip_uri
        self.create(self.cfg)
        self.active_calls = {} # we keep track of each call object here otherwise the call will get garbage collected immediatly

    def onIncomingCall(self, prm): # Callback function when a call is incoming, for now just auto-accept
        call = my_call.Call(self, prm.callId)
        call_info = call.getInfo()
        self.active_calls[prm.callId] = call
        print(f"Incoming call from {call_info.remoteUri}")
        #print(f"Will wait for media transport before answering")
        print(f"Accepting Automatically")
        
        call_prm = pj.CallOpParam()
        call_prm.statusCode = pj.PJSIP_SC_OK
        call.answer(call_prm)
        
    def call(self, target_uri):
        call = my_call.Call(self)
        call_param = pj.CallOpParam(True)
        try:
            call.makeCall(target_uri, call_param)
            self.active_calls[call.getId()] = call
            return call
        except pj.Error as e:
            print(f"[Account] Failed to make call to {target_uri}")
            print(f"  message={e.title}: {e.info}")
            raise
    
    def hangup_all(self):
        for call in list(self.active_calls.values()):
            call.hangup()

    def hangup_one(self, call_id):
        call = self.active_calls.get(call_id)
        if call:
            call.hangup()
            print(f"Call {call_id} hung up.")
        else:
            print(f"No active call with id={call_id}")

    def get_active_calls(self):
        return self.active_calls