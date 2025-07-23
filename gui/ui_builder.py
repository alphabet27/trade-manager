import json
from search_list import *
from show_table import create_treeview

class UIBuilder:
    def __init__(self, root, layout_file="layouts/basic_form.json"):
        self.root = root
        with open(layout_file) as f:
            self.layout = json.load(f)
        self.class_holder = {"widget_block":widget_block}
        self.custom_frames = {}
        self.widgets = {}  # Stores widget references (e.g., self.widgets["pid_entry"])

    def build(self):
        title = ttk.Label(self.root, text=self.layout["title"], font=head_font)
        title.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nw")
        for frame_name, frame_data in self.layout["frames"].items():
            frame = ttk.Frame(self.root)
            for widget_data in frame_data["widgets"]:
                self._create_widget(frame, widget_data)
            frame.grid(**frame_data["grid"])
            #print(f"Making frame {frame_name}\n{json.dumps(frame_data, indent=4)}")
        for frame_name, frame_data in self.layout["custom_frames"].items():
            #print(f"frame_name : {frame_name}\nframe_data : {frame_data}")
            frame_class = globals()[frame_data["class"]]
            self.custom_frames[frame_name] = frame_class(self.root, **self._filter_kwargs(frame_data))
            self.custom_frames[frame_name].grid(**frame_data["grid"])


    def _create_widget(self, parent, widget_data):
        get_font = True
        if hasattr(ttk, widget_data["class"]):
            widget_class = getattr(ttk, widget_data["class"])
        else:
            widget_class = getattr(tk, widget_data["class"])
            get_font = False
        widget = widget_class(parent, **self._filter_kwargs(widget_data))
        widget.grid(**widget_data["grid"])
        if "name" in widget_data:
            self.widgets[widget_data["name"]] = widget
        if "command" in widget_data:
            if hasattr(self, widget_data["command"]):
                widget.config(command = lambda kw = widget_data["command_kwargs"]: getattr(self, widget_data["command"])(**kw))
            else:
                raise Exception(f"Command {widget_data['command']} not defined")
        if "variable" in widget_data:
            if hasattr(self, widget_data["variable"]):
                widget.config(variable = getattr(self, widget_data["variable"]), value = widget_data["value"])
            else:
                raise Exception(f"Variable {widget_data['variable']} not found!!")

    def _filter_kwargs(self, data, get_font=False):
        # Remove non-Tkinter kwargs (e.g., 'grid', 'name')
        kwargs = {k: v for k, v in data.items() if k not in ("class", "grid", "name", "command", "command_kwargs")}
        if get_font:
            kwargs["font"] = main_font
        return kwargs

def add_tab(app, title, dont_add=False):
    tab_names = [app.notebook.tab(i, option="text") for i in app.notebook.tabs()]
    if (title in tab_names) or dont_add:
        app.notebook.select(tab_names.index(title))
        return
    root = ttk.Frame(app.notebook)
    return root
