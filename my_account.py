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
        
    def onCallState(self, prm): # callback for call-state changes, for example hanging up
        ci = self.getInfo()
        print(f"[Call] State changed: {ci.stateText} ({ci.lastStatusCode})")

        # If call is disconnected, remove it from account’s active_calls
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            if self.acc and ci.id in self.acc.active_calls:
                print(f"[Call] Removing call {ci.id} from active_calls")
                del self.acc.active_calls[ci.id] # watch if the call disconnects and remove it out of the call dict
        
    def call(self, target_uri): # Make a call
        call = my_call.Call(self)
        call_param = pj.CallOpParam()
        call.makeCall(target_uri, call_param)
        return call
    
    def hangup_all(self):
        for call in list(self.active_calls.values()):
            call.hangup()
    