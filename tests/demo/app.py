from server import App, Request
import time
import asyncio

srv = App()

@srv.route("/", "GET")
def home(req: Request):
    return "<h1>Hello</h1>"

@srv.route("/user/<int:id>", "GET")
def user(req: Request, id: int):
    return f"user {id}"

# Синхронный обработчик с видимой блокировкой
@srv.route("/sync-blocking", "GET")
def sync_blocking(req: Request):
    start = time.time()
    time.sleep(5)  # Имитация долгой БЛОКИРУЮЩЕЙ операции
    return f"\nSYNC BLOCKING: {time.time() - start:.2f}s"

# Асинхронный обработчик с конкурентностью
@srv.route("/async-nonblocking", "GET")
async def async_nonblocking(req: Request):
    start = time.time()
    await asyncio.sleep(5)  # Имитация долгой НЕблокирующей операции
    return f"\nASYNC NON-BLOCKING: {time.time() - start:.2f}s"

# Синхронный обработчик в потоке
@srv.route("/sync-threaded", "GET")
async def sync_threaded(req: Request):
    start = time.time()
    # time.sleep(5) — не вызываем прямо, а в потоке
    await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: time.sleep(5)
    )
    return f"\nSYNC THREADED: {time.time() - start:.2f}s"

if __name__ == "__main__":
    srv.start()