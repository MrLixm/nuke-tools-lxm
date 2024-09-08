import nuke
import nukescripts

import localorender
import logging

# install option 1.
nukescripts.showRenderDialog = localorender.nukescript_showRenderDialog

# install option 2.
menu = nuke.menu("Nuke").menu("Render")
menu.addCommand("Open LocaloRender", lambda: localorender.open_as_panel(), "F8")

# install option 3.
localorender.LocaloRenderPanel.register()

localorender.configure_logging(logging.DEBUG)
