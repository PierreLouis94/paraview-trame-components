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
        # Duplicate the first view
        view = self.views[0]
        duplicated_view = simple.CreateRenderView()
        duplicated_view.CopyFrom(view)
        self.views.append(duplicated_view)
        # Add the duplicated view to the UI
        self.ui.add_view(duplicated_view)
    else:
        # Remove the second view
        view_to_remove = self.views.pop()
        # Remove the view from the UI
        self.ui.remove_view(view_to_remove)

# Attach the toggle_views method to the Viewer instance
web_app.toggle_views = toggle_views.__get__(web_app, ptc.Viewer)

# Add the freeze/unfreeze method to the Viewer class
def toggle_freeze(self):
    self.state.views_frozen = not self.state.views_frozen
    if self.state.views_frozen:
        self.sync_views()
    else:
        self.unsync_views()

def sync_views(self):
    if len(self.views) > 1:
        self.views[1].CameraPosition = self.views[0].CameraPosition
        self.views[1].CameraFocalPoint = self.views[0].CameraFocalPoint
        self.views[1].CameraViewUp = self.views[0].CameraViewUp
        self.views[1].CameraParallelScale = self.views[0].CameraParallelScale

def unsync_views(self):
    pass  # No specific action needed to unsync views

# Attach the freeze/unfreeze methods to the Viewer instance
web_app.toggle_freeze = toggle_freeze.__get__(web_app, ptc.Viewer)
web_app.sync_views = sync_views.__get__(web_app, ptc.Viewer)
web_app.unsync_views = unsync_views.__get__(web_app, ptc.Viewer)

# Add event listeners to synchronize views when frozen
def on_camera_change(view):
    if web_app.state.views_frozen and len(web_app.views) > 1:
        web_app.sync_views()

v1.GetProperty("CameraPosition").AddObserver("ModifiedEvent", lambda obj, event: on_camera_change(v1))
v1.GetProperty("CameraFocalPoint").AddObserver("ModifiedEvent", lambda obj, event: on_camera_change(v1))
v1.GetProperty("CameraViewUp").AddObserver("ModifiedEvent", lambda obj, event: on_camera_change(v1))
v1.GetProperty("CameraParallelScale").AddObserver("ModifiedEvent", lambda obj, event: on_camera_change(v1))

# Add the toggle_view_size method to the Viewer class
def toggle_view_size(self):
    self.state.view_size_full = not self.state.view_size_full
    self.update_view_size()

def update_view_size(self):
    size = "100%" if self.state.view_size_full else "50%"
    for view_html in self.html_views:
        view_html.style = f"width: {size}; height: {size};"

# Attach the toggle_view_size and update_view_size methods to the Viewer instance
web_app.toggle_view_size = toggle_view_size.__get__(web_app, ptc.Viewer)
web_app.update_view_size = update_view_size.__get__(web_app, ptc.Viewer)

# Initialize state variables
web_app.state.views_frozen = False
web_app.state.view_size_full = True

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
                style="z-index: 1",
            )

            
             #Add the toggle button to the UI
            #ptc.VBtn(
            #    icon="mdi-view-dashboard",
            #    click=web_app.toggle_views,
            #    classes="mx-2",
            #    style="z-index: 1",
            #)
            

            # Add the freeze/unfreeze button to the UI
            ptc.VBtn(
                icon=("views_frozen ? 'mdi-lock' : 'mdi-lock-open'",),
                click=web_app.toggle_freeze,
                classes="mx-2",
                style="z-index: 1",
            )
            # Add the toggle view size button to the UI
            # ptc.VBtn(
            #     icon="mdi-aspect-ratio",
            #     click=web_app.toggle_view_size,
            #     classes="mx-2",
            #     style="z-index: 1",
            # )

            with ptc.ColorBy() as color:
                with color.prepend:
                    ptc.RepresentBy(classes="mr-2")

# Start the web application
web_app.start()