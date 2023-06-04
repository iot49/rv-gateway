include("$(PORT_DIR)/boards/manifest.py")
freeze("$(BOARD_DIR)/modules")

# individual modules
module("boot.py")
module("main.py")

# packages
package("aioble")
package("app")
package("collections")
package("utilities")

# directories modules
freeze("lib")
freeze("tests")
freeze("webserver")

# adafruit: a mix of modules and packages
include("adafruit/manifest.py")
