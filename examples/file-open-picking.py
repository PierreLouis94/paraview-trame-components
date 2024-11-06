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

# Add the toggle_views method to the Viewer class
def toggle_views(self):
    if len(self.views) == 1:
        # Add a second view
        view = simple.CreateRenderView()
        self.views.append(view)
    else:
        # Remove the second view
        self.views = self.views[:1]
    self._build_ui()

# Attach the toggle_views method to the Viewer instance
web_app.toggle_views = toggle_views.__get__(web_app, ptc.Viewer)

with web_app.ui:
    ptc.HoverPoint()

    with web_app.col_left:
        ptc.VSpacer()
        ptc.PipelineBrowser()
        ptc.VSpacer()
        ptc.VSpacer()
        ptc.VSpacer()
        ptc.VSpacer()

    with web_app.side_top:
        with ptc.VRow(classes="ptc-region top-left"):
            
            ptc.OpenFileToggle()
            ptc.VBtn(
                icon=("enable_point_hover ? 'mdi-target' : 'mdi-crosshairs-off'",),
                click="enable_point_hover = !enable_point_hover",
                classes="mx-2",
            )
             # Add the toggle button to the UI
            ptc.VBtn(
                icon="mdi-view-dashboard",
                click=web_app.toggle_views,
                classes="mx-2",
            )

            with ptc.ColorBy() as color:
                with color.prepend:
                    ptc.RepresentBy(classes="mr-2")

            

# Start the web application
web_app.start()