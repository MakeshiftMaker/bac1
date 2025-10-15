# backend.py
# Minimal FastAPI WebSocket control for your pjsua2-based demo

import asyncio
import json
import logging
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

import pjsua2 as pj

# Import your existing pjsua2 wrapper modules
import my_endpoint
import my_account
import my_call

# NOTE: pjsua2 is not async; we will call its blocking operations using asyncio.to_thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pjsip-demo")

app = FastAPI()

# Global pjsip objects
EP = None
TRANSPORTS = []
ACCOUNTS: Dict[str, my_account.Account] = {}

# Connected WebSocket clients
clients: Set[WebSocket] = set()

# Poll interval to check call states (seconds)
POLL_INTERVAL = 0.5

# ---------------------------------------------------------------------
# Helper: broadcast message to all WebSocket clients
# ---------------------------------------------------------------------
async def broadcast(msg: dict):
    text = json.dumps(msg)
    to_remove = []
    for ws in clients:
        try:
            await ws.send_text(text)
        except Exception:
            to_remove.append(ws)
    for ws in to_remove:
        clients.discard(ws)


# ---------------------------------------------------------------------
# FastAPI startup and shutdown hooks
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    global EP, TRANSPORTS
    logger.info("Starting PJSIP endpoint")

    # Initialize endpoint (using your my_endpoint.Endpoint wrapper)
    EP = my_endpoint.Endpoint()
    EP.libCreate()

    # Minimal EpConfig — keep it simple for demo
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.threadCnt = 0
    EP.libInit(ep_cfg)

    # Create a default UDP transport on port 5060
    tcfg = pj.TransportConfig()
    tcfg.port = 5060
    TRANSPORTS.append(EP.transportCreate(pj.PJSIP_TRANSPORT_UDP, tcfg))

    EP.libStart()
    logger.info("PJSIP library started")

    # Start background state poller
    asyncio.create_task(call_state_poller())


@app.on_event("shutdown")
async def shutdown_event():
    global EP
    logger.info("Shutting down PJSIP")
    try:
        if EP:
            EP.libDestroy()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ---------------------------------------------------------------------
# Example background task to poll call states
# ---------------------------------------------------------------------
async def call_state_poller():
    while True:
        await asyncio.sleep(POLL_INTERVAL)
        try:
            for acc_uri, acc in ACCOUNTS.items():
                calls = acc.get_active_calls()
                for call_id, call in calls.items():
                    ci = call.getInfo()
                    await broadcast({
                        "event": "call_state",
                        "account": acc_uri,
                        "call_id": call_id,
                        "state": ci.stateText,
                        "remote_uri": ci.remoteUri
                    })
        except Exception as e:
            logger.debug(f"Poller error: {e}")


# ---------------------------------------------------------------------
# WebSocket endpoint for GUI communication
# ---------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    logger.info("WebSocket client connected")

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            action = msg.get("action")

            if action == "create_account":
                uri = msg.get("uri")
                if uri not in ACCOUNTS:
                    acc = my_account.Account(uri)
                    ACCOUNTS[uri] = acc
                    await ws.send_json({"event": "account_created", "uri": uri})
                else:
                    await ws.send_json({"event": "error", "message": "Account already exists"})

            elif action == "call":
                src = msg.get("from")
                dst = msg.get("target")
                acc = ACCOUNTS.get(src)
                if acc:
                    await asyncio.to_thread(acc.call, dst)
                    await ws.send_json({"event": "calling", "from": src, "to": dst})
                else:
                    await ws.send_json({"event": "error", "message": f"No account {src}"})

            elif action == "hangup_all":
                for acc in ACCOUNTS.values():
                    await asyncio.to_thread(acc.hangup_all)
                await ws.send_json({"event": "calls_hungup"})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        clients.discard(ws)


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting FastAPI backend at ws://localhost:8000/ws")
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, log_level="info")
