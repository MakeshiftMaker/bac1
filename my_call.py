import pjsua2 as pj


class Call(pj.Call):
    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        #self.connected = False
        self.acc = acc  # keep a reference to the owning Account

        
    def hangup(self, code=pj.PJSIP_SC_DECLINE):
        prm = pj.CallOpParam()
        prm.statusCode = code
        super().hangup(prm)   # call base pj.Call.hangup

    def onCallState(self, prm):
        ci = self.getInfo()
        print(f"[Call] State changed: {ci.stateText} ({ci.lastStatusCode})")

        # Remove the call from the account's active_calls if it disconnects
        if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            call_id = self.getId()
            if self.acc and call_id in self.acc.active_calls:
                print(f"[Call] Removing call {call_id} from active_calls")
                del self.acc.active_calls[call_id]

