import paraview.web.venv
from pathlib import Path
from paraview import simple
from ptc import Viewer, PipelineBrowser, ColorBy, PARAVIEW_EXAMPLES

IMAGE_STATE = str(Path(__file__).with_name("diskout-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
web_app = Viewer(from_state=True)

with web_app.col_left:
    PipelineBrowser()

with web_app.col_center:
    ColorBy()

web_app.start()
