import paraview.web.venv
from paraview import simple
import ptc

# Create render views
v1 = simple.CreateRenderView()
v2 = simple.CreateRenderView()

# Dictionary to keep track of visible objects in each view
visible = {
    v1: [],
    v2: [],
}

# Function to update representation visibility
def update_representation(v, s):
    r = simple.Show(s, v)
    r.Visibility = 1 if s in visible[v] else 0

# Function to load a file into the active view
def load_file(file_path, active_view):
    data = simple.OpenDataFile(file_path)
    visible[active_view].append(data)
    update_representation(active_view, data)

# Initialize the web application with the views
web_app = ptc.Viewer(views=[v1, v2])

# Variable to keep track of the active view
active_view = v1

with web_app.ui:
    ptc.HoverPoint()

    with web_app.col_left:
        ptc.PipelineBrowser()

    with web_app.side_top:
        with ptc.VRow(classes="ptc-region align-center"):
            ptc.VSpacer()
            ptc.OpenFileToggle()
            ptc.VBtn(
                icon=("enable_point_hover ? 'mdi-target' : 'mdi-crosshairs-off'",),
                click="enable_point_hover = !enable_point_hover",
                classes="mx-2",
            )
            ptc.VBtn(
                icon=(
                    "hover_mode === 'points' ? 'mdi-dots-triangle' : 'mdi-triangle-outline'",
                ),
                click="hover_mode = hover_mode === 'points' ? 'cells' : 'points'",
                classes="mx-2",
            )
            with ptc.ColorBy() as color:
                with color.prepend:
                    ptc.RepresentBy(classes="mr-2")
            ptc.VSpacer()
            ptc.VBtn(
                icon=("active_view === v1 ? 'mdi-view-dashboard' : 'mdi-view-dashboard-outline'",),
                click="active_view = active_view === v1 ? v2 : v1",
                classes="mx-2",
                text="Switch View"
            )

# Start the web application
web_app.start()