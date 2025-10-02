import pjsua2 as pj
import my_endpoint
import my_account
import my_call
import time


#set up endpoint
ep = my_endpoint.Endpoint()
ep.libCreate()

ep_cfg = pj.EpConfig()
ep.libInit(ep_cfg)

ep.audDevManager().setNullDev()

#set up transport for accounts
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
#acc_cfg_alice = pj.AccountConfig()
#acc_cfg_alice.idUri = "sip:alice@127.0.0.1"
alice = my_account.Account("sip:alice@127.0.0.1")
#alice.create(acc_cfg_alice)
time.sleep(1)
#acc_cfg_bob = pj.AccountConfig()
#acc_cfg_bob.idUri = "sip:bob@127.0.0.1"
bob = my_account.Account("sip:bob@127.0.0.1")
#bob.create(acc_cfg_bob)

print("Alice is ready at sip:alice@127.0.0.1:5060")
print("Bob is ready at sip:bob@127.0.0.1:5061")

time.sleep(1)

bob_info = bob.getInfo()
bob_call_alice = bob.call(alice.cfg.idUri)

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ep.libDestroy()
