import paraview.web.venv
from paraview import simple
from ptc import Viewer, PipelineBrowser
import ptc

cone = simple.Cone()
sphere = simple.Sphere()
cube = simple.Box(Center=[1, 0, 0])

v1 = simple.GetRenderView()
v2 = simple.CreateRenderView()
v3 = simple.CreateRenderView()

visible = {
    v1: [cone],
    v2: [cone, sphere],
    v3: [sphere, cube],
}


def update_representation(v, s):
    r = simple.Show(s, v)
    r.Visibility = 1 if s in visible[v] else 0


# Create all representations and update visibility
for v in [v1, v2, v3]:
    for s in [cone, sphere, cube]:
        update_representation(v, s)


def hide_render_view(view):
    for s in [cone, sphere, cube]:
        r = simple.Show(s, view)
        r.Visibility = 0


# Hide v2
hide_render_view(v2)

web_app = Viewer(views=[[v1, v2], v3])

# Initial view setup
web_app.views = [[v1],v3]
web_app._build_ui()

# Function to toggle views
def toggle_views():
    print("Toggle views called")
    print(f"Current views: {web_app.views}")
    if web_app.views == [[v1]]:
        web_app.views = [[v1], v3]
        print("Switching to views: [[v1], v3]")
    elif web_app.views == [[v1], v3]:
        web_app.views = [[v1]]
        print("Switching to views: [[v1]]")
    print(f"Updated views: {web_app.views}")
    web_app.update()
    print("web_app.update() called")

# Add the button outside the view container to ensure it remains visible
with web_app.side_top:
    with ptc.VRow(classes="ptc-region align-center"):
        ptc.VSpacer()
        ptc.VBtn("Toggle Views", click=toggle_views)

# Add other UI components
with web_app.col_left:
    PipelineBrowser()

# Start the web application
web_app.start()