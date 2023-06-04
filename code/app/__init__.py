# deliberate re-exports (move into main to avoid)

def load_utilities():
    from .default_config import DEFAULT_CONFIG
    try:
        from custom_config import CUSTOM_CONFIG
    except ImportError:
        CUSTOM_CONFIG = {}

    from utilities import config
    config.load(DEFAULT_CONFIG, CUSTOM_CONFIG)

load_utilities()


def load_tasks(task='wifi'):
    # back-door for debugging
    # Note: takes long if modules need compilation
    from . import tasks
    return tasks


async def main():

    import uasyncio as asyncio 
    from utilities import config
    from . import tasks

    def exception_handler(loop, context):
        # hmm, this isn't async - can't call webapp.error
        import sys
        from io import StringIO
        buf = StringIO()
        buf.write("***** global asyncio exception:\n")
        sys.print_exception(context["exception"], buf)
        print(buf.getvalue())

    # set exception handler
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)

    print("Starting tasks ...")

    task_array = [
        tasks.blink.main(300),
        tasks.wifi.main(60),
        tasks.httpd.main(),
        tasks.ble_scanner.main(),        
        tasks.gps.main(),
        tasks.imu.main(5),
        tasks.rvc.main(),
        tasks.auto_save_config.main(),
        tasks.gc.main(),
        tasks.stats.main(),
    ]

    try:
        res = await asyncio.gather(*task_array)
    except KeyboardInterrupt as e:
        print("***** KeyboardInterrupt in main", e)
        # BAIL!
    except Exception as e:
        print("***** Exception in main", e)
        # Recover?

    loop.run_forever()

"""
sample main.py:

```
import uasyncio as asyncio
from app import main

asyncio.run(main())
```

Press ctrl-C to interrupt. `import main` restarts the program.
"""
