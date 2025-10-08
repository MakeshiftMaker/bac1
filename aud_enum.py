import pjsua2 as pj

# 1️⃣ Create and initialize endpoint
ep = pj.Endpoint()
ep.libCreate()

ep_cfg = pj.EpConfig()
ep.libInit(ep_cfg)

# 2️⃣ Start endpoint
ep.libStart()

# 3️⃣ Access the audio device manager instance via endpoint
adm = ep.audDevManager()  # ⚠️ this is already an instance

# 4️⃣ Enumerate audio devices
devices = adm.enumDev2()  # ✅ call on the instance, not the class

# 5️⃣ Print devices
print("Available audio devices:")
for i, dev in enumerate(devices):
    print(f"{i}: {dev.name}")
    print(f"   Input channels: {dev.inputCount}")
    print(f"   Output channels: {dev.outputCount}")
    #print(f"   Default input: {dev.isDefaultInput}")
    #print(f"   Default output: {dev.isDefaultOutput}")
    print()

# 6️⃣ Shutdown endpoint
ep.libDestroy()
