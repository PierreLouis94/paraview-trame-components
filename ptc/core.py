from pathlib import Path

from paraview import simple
from trame.app import get_server
from trame.decorators import TrameApp, change, controller
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import paraview as pv_widgets
from trame.widgets import vuetify3 as v3

from .layouts import create_layout_manager


class InvalidContainerNameError(Exception):
    def __init__(self, name):
        super().__init__(f"Container {name} not available")


@TrameApp()
class Viewer:
    def __init__(self, views=None, from_state=False, server=None, template_name="main"):
        self.layout_factory = create_layout_manager(self)
        self.template_name = template_name
        self.server = get_server(server)

        # Serve our http directory
        self.server.enable_module(
            {
                "serve": {
                    "ptc": str(Path(__file__).with_name("assets") / "http"),
                },
                "styles": ["ptc/style.css"],
            }
        )

        self.views = views
        self.html_views = []
        self.interactive_modes = None
        self.proxy_views = []
        self.ui = None
        if self.views is None or len(self.views) == 0:
            view = simple.GetActiveView()
            if view is None:
                view = simple.CreateRenderView()
            self.views = [view]

        if from_state:
            for view in self.views:
                view.MakeRenderWindowInteractor(True)

        self._build_ui()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def start(self, *args, **kwargs):
        self.ui.flush_content()
        self.server.start(*args, **kwargs)

    @change("active_view_id")
    def _active_view(self, active_view_id, **_):
        if active_view_id < len(self.proxy_views):
            simple.SetActiveView(self.proxy_views[active_view_id])
            if self.server.controller.on_active_view_change.exists():
                self.server.controller.on_active_view_change()

    @change("first_view_full_size")
    def _update_view_sizes(self, first_view_full_size, **_):
        for i, view_html in enumerate(self.html_views):
            if i == 0:
                size_class = "flex-grow-1 flex-shrink-1" if first_view_full_size else "flex-grow-1 flex-shrink-1 w-50"
            else:
                size_class = "d-none" if first_view_full_size else "flex-grow-1 flex-shrink-1 w-50"
            if view_html.parent:
                view_html.parent.classes = size_class
                print(f"View {i}: size_class updated to {size_class}")
            else:
                print(f"View {i}: parent is None")
        self.ui.flush_content()
        print("flush_content called after size class update")

    def _build_ui(self):
        self.state.active_view_id = 0
        self.state.remote_view_mouse = None
        self.state.html_view_space = None
        self.state.client_only("html_view_space")
        self.state.first_view_full_size = True

        with VAppLayout(self.server, template_name=self.template_name, full_height=True) as layout:
            self.ui = layout
            with html.Div(classes="d-flex align-stretch fill-height"):
                v3.VBtn(
                    icon="mdi-view-grid",
                    click="first_view_full_size = !first_view_full_size",
                    classes="position-absolute",
                    style="bottom: 1rem !important; left: 1rem !important; top: unset !important; z-index: 1;",
                    variant="outlined",
                    size="small",
                )
                print("Button added to toggle view size")
                for i, view in enumerate(self.views):
                    view_id = len(self.html_views)
                    size_class = "flex-grow-1 flex-shrink-1" if (i == 0 and self.state.first_view_full_size) else ("flex-grow-1 flex-shrink-1 w-50" if not self.state.first_view_full_size else "d-none")
                    print(f"View {i}: size_class = {size_class}")
                    with html.Div(classes=f"{size_class} border-thin position-relative",
                                  style=(f"{{ overflow: 'hidden', zIndex: 0, padding: '1px', margin: '1px', outline: active_view_id === {view_id} ? 'solid 1.5px blue' : 'none' }}",),
                                  click=f"active_view_id = {view_id}") as parent_div:
                        view_html = pv_widgets.VtkRemoteView(view, interactive_ratio=1, enable_picking=("enable_picking", False), style="z-index: -1;", interactor_events=("remote_view_events", ["EndAnimation", "MouseMove"]), MouseMove="remote_view_mouse = $event.position", mouse_enter="html_view_space = $event.target.getBoundingClientRect()", __events=[("mouse_enter", "mouseenter")])
                        v3.VBtn(icon="mdi-crop-free", click=view_html.reset_camera, classes="position-absolute", style="bottom: 1rem !important; right: 1rem !important; top: unset !important; z-index: 1;", variant="outlined", size="small")
                        self.ctrl.view_update.add(view_html.update)
                        self.ctrl.view_reset_camera.add(view_html.reset_camera)
                        self.ctrl.on_data_loaded.add(view_html.reset_camera)
                        view_html.parent = parent_div  # Ensure the parent is assigned
                        self.html_views.append(view_html)
                        self.proxy_views.append(view)
                        print(f"View {i} added with view_id {view_id}")

    @controller.add("on_data_change")
    def update(self):
        print("update method called")
        self.ctrl.view_update()
        print("view_update called")

    @controller.set("enable_selection")
    def enable_selection(self, selection=True):
        if self.interactive_modes is None:
            self.interactive_modes = [
                str(v.InteractionMode).replace("'", "") for v in self.proxy_views
            ]

        if selection:
            for v in self.proxy_views:
                v.InteractionMode = "Selection"
        else:
            for v, mode in zip(self.proxy_views, self.interactive_modes, strict=False):
                v.InteractionMode = mode

    def reset_camera(self):
        self.ctrl.view_reset_camera()

    def __getattr__(self, key):
        """Lookup a layout specific container."""
        manager = self.layout_factory.get_manager(key)

        if manager is None:
            raise InvalidContainerNameError(key)

        with self.ui:
            return manager.create_container(key)