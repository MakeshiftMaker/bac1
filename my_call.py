import pjsua2 as pj


class Call(pj.Call):
    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.connected = False
        
    def hangup(self, code=pj.PJSIP_SC_DECLINE):
        prm = pj.CallOpParam()
        prm.statusCode = code
        super().hangup(prm)   # call base pj.Call.hangup

