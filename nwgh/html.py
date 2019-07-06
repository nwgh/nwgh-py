import inspect
import jinja2
import os


def render_template(path):
    caller = inspect.stack()[1]
    caller_path = os.path.dirname(caller.filename)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(caller_path))
    template = env.get_template(path)
    return template.render(**caller.frame.f_locals)
