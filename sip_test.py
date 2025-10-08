import pjsua2 as pj
import my_endpoint
import my_account
import my_call
import time


#set up endpoint
ep = my_endpoint.Endpoint()
ep.libCreate()

ep_cfg = pj.EpConfig()
ep_cfg.medConfig.srtpUse = pj.PJMEDIA_SRTP_MANDATORY
ep.libInit(ep_cfg)

# Get a reference to the audio device manager
adm = ep.audDevManager()
adm.setCaptureDev(6)   # pipewire capture
adm.setPlaybackDev(6)  # pipewire playback

#ep.audDevManager().setNullDev()

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

#time.sleep(2)

alice = my_account.Account("sip:alice@127.0.0.1")
bob = my_account.Account("sip:bob@127.0.0.1")

print("Alice is ready at sip:alice@127.0.0.1:5060")
print("Bob is ready at sip:bob@127.0.0.1:5061")

bob_info = bob.getInfo()
bob_call_alice = bob.call(alice.cfg.idUri)

time.sleep(5)

bob_calls = bob.get_active_calls()
alice_calls = alice.get_active_calls()

#bob_call_alice.hangup()
bob.hangup_one(bob_call_alice.getId())
#print("hanging up")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    #bob.hangup_one(bob_call_alice.getId())
    #time.sleep(2)
    ep.libDestroy()
