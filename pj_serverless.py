import time
import pjsua2 as pj

active_calls = {}

class MyAccount(pj.Account):
    def onIncomingCall(self, prm):
        call = pj.Call(self, prm.callId)
        ci = call.getInfo()
        active_calls[prm.callId] = call
        print(f"Incoming Call from {ci.remoteUri}")
        # time.sleep(5)

        while True:
            answer = input("Accept call? (y/n): ").strip().lower()
            if answer in ("y", "n"):
                break
            print("Please enter 'y' or 'n'.")
        call_param = pj.CallOpParam()
        
        if answer == "y":
            # Accept the call (200 OK)
            call_param.statusCode = pj.PJSIP_SC_OK
            call.answer(call_param)
            print("Call accepted.")
        else:
            # Reject the call (486 Busy Here)
            call_param.statusCode = pj.PJSIP_SC_BUSY_HERE
            call.answer(call_param)
            print("Call rejected.")


# === Step 1: Initialize endpoint (SIP engine) ===
ep = pj.Endpoint()
ep.libCreate()

ep_cfg = pj.EpConfig()
ep.libInit(ep_cfg)

ep.audDevManager().setNullDev()

# Transport for Alice (UDP 5060)
alice_cfg = pj.TransportConfig()
alice_cfg.port = 5060
ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, alice_cfg)

# Transport for Bob (UDP 5061)
bob_cfg = pj.TransportConfig()
bob_cfg.port = 5061
ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, bob_cfg)

ep.libStart()


# === Step 2: Create accounts ===
acc_cfg_alice = pj.AccountConfig()
acc_cfg_alice.idUri = "sip:alice@127.0.0.1"
alice = MyAccount()
alice.create(acc_cfg_alice)

acc_cfg_bob = pj.AccountConfig()
acc_cfg_bob.idUri = "sip:bob@127.0.0.1"
bob = MyAccount()
bob.create(acc_cfg_bob)

print("Alice is ready at sip:alice@127.0.0.1:5060")
print("Bob is ready at sip:bob@127.0.0.1:5061")

# Give Alice time to “register”
time.sleep(1)

# === Step 3: Bob dials Alice ===
print("Bob is dialing Alice...")
call = pj.Call(bob)
bob_call_param = pj.CallOpParam()
call.makeCall("sip:alice@127.0.0.1:5060", bob_call_param)

try:
    while True:
        awnser = input("Press X to quit...\n").strip().lower()
        if awnser == "x":
            break
finally:
    ep.libDestroy()
