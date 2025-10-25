from event_bus import EventBus
from last_n import LastNStrategy
from fastapi import APIRouter

from fastapi import Request
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
from event_bus import EventBus

router = APIRouter()


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body style="background-color: antiquewhite;">
    
<h1>hello</h1>
<pre id="log"></pre>


<script>
    const log_id = document.getElementById('log');
    const es = new EventSource("/stream");
    es.onmessage = function(event) {
        if (event.data) {
            log_id.textContent += event.data + "\\n";
        }
    }
</script>

</body>
</html>
"""



def mount_routes(bus: EventBus, lastn: LastNStrategy, log_path:str) -> APIRouter:

    @router.get("/log", response_class=HTMLResponse)
    async def log_page():
        return HTML_PAGE

    @router.get("/stream")
    async def sse_log_stream(request : Request):
        # we can have sub
        # read initial last lines [:10]
        # return a generator func in EventSourceResponse

        sub = bus.subscribe()

        # Now get initial last 10 lines
        last_lines = lastn.read_last_n(log_path, 10)
        for i in last_lines:
            sub.put(i)

        async def event_generator():
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    # new_line = "new_line 123"
                    # yield {"data" : new_line}
                    line = sub.get(timeout=1.0)
                    if line is not None:
                        yield {"data": line}
            except Exception as E:
                print("[E]: ", E)
            finally:
                print("[Close]: ")
                bus.unsubscribe(sub)
        return EventSourceResponse(event_generator())
    
    return router

    # uvicorn main:router --host localhost --port 8000