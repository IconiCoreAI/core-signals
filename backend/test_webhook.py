import httpx
import time
import asyncio

PAYLOADS = [
    {
        "source": "typeform",
        "type": "form",
        "title": "New lead submitted",
        "body": "Sarah Johnson filled out the Contact Us form",
        "metadata": {"form_id": "abc123", "email": "sarah@example.com"}
    },
    {
        "source": "stripe",
        "type": "payment",
        "title": "Payment received $299",
        "body": "Pro plan subscription from mike@company.com",
        "metadata": {"amount": 29900, "currency": "usd"}
    },
    {
        "source": "notion",
        "type": "notion",
        "title": "Database row updated",
        "body": "CRM record for Acme Corp moved to 'Closed Won'",
        "metadata": {"page_id": "xyz789"}
    },
    {
        "source": "ai-agent",
        "type": "ai-agents",
        "title": "Research task complete",
        "body": "Agent finished competitor analysis — 12 companies reviewed",
        "metadata": {"task_id": "task_001", "duration_seconds": 143}
    },
    {
        "source": "typeform",
        "type": "form",
        "title": "Survey response received",
        "body": "NPS score: 9 from john@startup.io",
        "metadata": {"score": 9}
    }
]

async def send_payloads():
    url = "http://localhost:8000/webhook"
    
    async with httpx.AsyncClient() as client:
        # Wait for the server to be completely up
        for _ in range(5):
            try:
                # We expect a 404 or 405 for GET /webhook, but if it connects the server is up
                await client.get(url)
                print("Server is up!")
                break
            except httpx.ConnectError:
                print("Waiting for server to start...")
                await asyncio.sleep(1)
        
        for i, payload in enumerate(PAYLOADS, 1):
            response = await client.post(url, json=payload)
            if response.status_code == 201:
                print(f"[{i}/5] Successfully sent: {payload['title']}")
                print(f"      Response: {response.json()}")
            else:
                print(f"[{i}/5] Failed to send: {payload['title']}")
                print(f"      Status: {response.status_code}, Response: {response.text}")
            
            # small delay to simulate real events and ensure order in db if desired
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(send_payloads())
