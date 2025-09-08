from fastapi import FastAPI, HTTPException
import pjsua2 as pj
import threading

app = FastAPI()

ep = pj.Endpoint()
ep.libCreate()
ep_cfg = pj.EpConfig()
ep.libInit(ep_cfg)

cfg = pj.TransportConfig()
cfg.port=5060
ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, cfg)
ep.libStart()

accounts = {}
active_calls = {}

# High-level Call class from the GUI demo
class Call(pj.Call):
    def __init__(self, acc, peer_uri='', call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.acc = acc
        self.peerUri = peer_uri
        self.connected = False

    def onCallState(self, prm):
        ci = self.getInfo()
        self.connected = ci.state == pj.PJSIP_INV_STATE_CONFIRMED

    def onCallMediaState(self, prm):
        ci = self.getInfo()
        for mi in ci.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                m = self.getMedia(mi.index)
                am = pj.AudioMedia.typecastFromMedia(m)
                ep.audDevManager().getCaptureDevMedia().startTransmit(am)
                am.startTransmit(ep.audDevManager().getPlaybackDevMedia())

# Create a dummy account
acc_cfg = pj.AccountConfig()
acc_cfg.idUri = "sip:alice@127.0.0.1"
alice = pj.Account()
alice.create(acc_cfg)
accounts["alice"] = alice

@app.post("/call")
def make_call(uri: str):
    call = Call(alice)
    call_param = pj.CallOpParam(True)
    try:
        call.makeCall(uri, call_param)
    except pj.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    call_id = id(call)
    active_calls[call_id] = call
    return {"call_id": call_id, "uri": uri}

@app.post("/hangup")
def hangup(call_id: int):
    call = active_calls.get(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    call.hangup(pj.CallOpParam())
    del active_calls[call_id]
    return {"status": "hung up"}

@app.get("/calls")
def list_calls():
    return [{"call_id": cid, "peer": c.getInfo().remoteUri} for cid, c in active_calls.items()]
