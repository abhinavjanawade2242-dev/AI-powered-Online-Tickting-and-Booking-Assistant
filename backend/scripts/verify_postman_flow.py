import asyncio
import json
import os
import re
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db

async def test_all_postman_flows():
    postman_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "PS-07_Postman_Collection.json")
    if not os.path.exists(postman_path):
        postman_path = os.path.join("..", "docs", "PS-07_Postman_Collection.json")

    with open(postman_path, "r", encoding="utf-8") as f:
        col = json.load(f)

    # Initialize env variables
    env_vars = {
        "host": "http://testserver",
        "base_url": "http://testserver/api/v1",
        "auth_token": "",
        "booking_ref": "",
        "ticket_code": "",
        "qr_payload": "",
        "session_id": "test_postman_session_01"
    }

    # Flatten requests
    requests_to_run = []
    def extract_requests(items, folder_name=""):
        for item in items:
            if "item" in item:
                extract_requests(item["item"], folder_name=f"{folder_name} > {item['name']}" if folder_name else item["name"])
            elif "request" in item:
                requests_to_run.append((folder_name, item["name"], item["request"]))

    extract_requests(col["item"])
    print(f"Total requests found in Postman Collection: {len(requests_to_run)}")

    await init_db()

    results = []
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for folder, name, req in requests_to_run:
            method = req["method"]
            raw_url = req["url"]["raw"]
            
            # Interpolate variables in URL
            for k, v in env_vars.items():
                raw_url = raw_url.replace(f"{{{{{k}}}}}", str(v))

            # Headers
            headers = {}
            for h in req.get("header", []):
                val = h["value"]
                for k, v in env_vars.items():
                    val = val.replace(f"{{{{{k}}}}}", str(v))
                headers[h["key"]] = val

            # Body
            body_data = None
            if "body" in req and req["body"].get("mode") == "raw":
                raw_body = req["body"]["raw"]
                for k, v in env_vars.items():
                    raw_body = raw_body.replace(f"{{{{{k}}}}}", str(v))
                if name == "Register New Customer":
                    import uuid
                    unique_email = f"adithya_{uuid.uuid4().hex[:6]}@example.com"
                    raw_body = re.sub(r'"email":\s*"[^"]+"', f'"email": "{unique_email}"', raw_body)
                try:
                    body_data = json.loads(raw_body)
                except Exception:
                    body_data = raw_body

            # Relative path for ASGI client
            path = raw_url.replace("http://testserver", "")
            if not path.startswith("/"):
                path = "/" + path

            # Send request
            try:
                if method == "GET":
                    resp = await client.get(path, headers=headers)
                elif method == "POST":
                    if isinstance(body_data, dict):
                        resp = await client.post(path, json=body_data, headers=headers)
                    else:
                        resp = await client.post(path, content=body_data, headers=headers)
                elif method == "PUT":
                    resp = await client.put(path, json=body_data, headers=headers)
                elif method == "DELETE":
                    resp = await client.delete(path, headers=headers)
                else:
                    resp = None

                status_code = resp.status_code if resp else 0
                resp_json = {}
                try:
                    resp_json = resp.json()
                except Exception:
                    resp_json = {"text": resp.text[:100] if resp else ""}

                # Extract variables for downstream requests
                if "access_token" in resp_json:
                    env_vars["auth_token"] = resp_json["access_token"]
                if "booking_reference" in resp_json and resp_json["booking_reference"]:
                    env_vars["booking_ref"] = resp_json["booking_reference"]
                if "tickets" in resp_json and len(resp_json["tickets"]) > 0:
                    env_vars["ticket_code"] = resp_json["tickets"][0]["ticket_code"]
                    env_vars["qr_payload"] = resp_json["tickets"][0]["qr_payload"]

                is_ok = 200 <= status_code < 400
                results.append({
                    "folder": folder,
                    "name": name,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "ok": is_ok,
                    "error": None if is_ok else resp_json
                })
            except Exception as e:
                results.append({
                    "folder": folder,
                    "name": name,
                    "method": method,
                    "path": path,
                    "status_code": 500,
                    "ok": False,
                    "error": str(e)
                })

    print("\n" + "=" * 80)
    print("POSTMAN FLOW VERIFICATION RESULTS:")
    print("=" * 80)
    passed_count = sum(1 for r in results if r["ok"])
    failed_count = len(results) - passed_count
    for r in results:
        status_icon = "✅" if r["ok"] else "❌"
        print(f"{status_icon} [{r['status_code']}] {r['method']} {r['path']} - {r['name']}")
        if not r["ok"]:
            print(f"   ⚠️ ERROR DETAILS: {json.dumps(r['error'], indent=2)}")

    print("=" * 80)
    print(f"Summary: {passed_count} PASSED | {failed_count} FAILED out of {len(results)} Postman requests.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_all_postman_flows())
