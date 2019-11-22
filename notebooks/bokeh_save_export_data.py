"""
Small code snippet to generate linked plots in Bokeh, plus a dynamic table displaying data with a save button to export cvs of selected data

Best executed in jupyter notebook/lab.  Code from `02_bokeh_chapter.ipynb`
"""

from random import random

from bokeh.io import output_notebook  # prevent opening separate tab with graph
from bokeh.io import show

from bokeh.layouts import row
from bokeh.layouts import grid
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.models import Button  # for saving data
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.models import HoverTool
from bokeh.plotting import figure


# create data
x = [random() for x in range(500)]
y = [random() for y in range(500)]

# create first subplot
plot_width = 400
plot_height = 400

s1 = ColumnDataSource(data=dict(x=x, y=y))
fig01 = figure(
    plot_width=plot_width,
    plot_height=plot_height,
    tools=["lasso_select", "reset", "save"],
    title="Select Here",
)
fig01.circle("x", "y", source=s1, alpha=0.6)

# create second subplot
s2 = ColumnDataSource(data=dict(x=[], y=[]))

fig02 = figure(
    plot_width=400,
    plot_height=400,
    x_range=(0, 1),
    y_range=(0, 1),
    tools=["box_zoom", "wheel_zoom", "reset", "save"],
    title="Watch Here",
)

fig02.circle("x", "y", source=s2, alpha=0.6, color="firebrick")

# create dynamic table showing only selected points from s1
columns = [
    TableColumn(field="x", title="X axis"),
    TableColumn(field="y", title="Y axis"),
]

table = DataTable(
    source=s2,
    columns=columns,
    width=400,
    height=600,
    sortable=True,
    selectable=True,
    editable=True,
)

# fancy javascript to link subplots
# js pushes selected points into ColumnDataSource of 2nd plot and table
# inspiration for this from:
# credit: https://stackoverflow.com/users/1456857/jake
# via: https://stackoverflow.com/questions/34164587/get-selected-data-contained-within-box-select-tool-in-bokeh
# credit: Marko_Baros
# via: https://discourse.bokeh.org/t/how-to-save-selected-points-in-a-pandas-data-frame/1659/2

s1.selected.js_on_change(
    "indices",
    CustomJS(
        args=dict(s1=s1, s2=s2, table=table),
        code="""
        var inds = cb_obj.indices;
        var d1 = s1.data;
        var d2 = s2.data;
        d2['x'] = []
        d2['y'] = []
        for (var i = 0; i < inds.length; i++) {
            d2['x'].push(d1['x'][inds[i]])
            d2['y'].push(d1['y'][inds[i]])
        }
        s2.change.emit();
        table.change.emit();
    """,
    ),
)

# create save button - saves selected datapoints to text file
# inspiration for this code:
# credit:  https://stackoverflow.com/users/8412027/joris
# via: https://stackoverflow.com/questions/31824124/is-there-a-way-to-save-bokeh-data-table-content
# note: savebutton line `var out = "x, y\\n";` defines the header of the exported file,
# headers are helpful to have for downstream processing (e.g. in pandas or another python script).

savebutton = Button(label="Save", button_type="success")
savebutton.callback = CustomJS(
    args=dict(source_data=s1),
    code="""
        var inds = source_data.selected.indices;
        var data = source_data.data;
        var out = "x, y\\n";
        for (i = 0; i < inds.length; i++) {
            out += data['x'][inds[i]] + "," + data['y'][inds[i]] + "\\n";
        }
        var file = new Blob([out], {type: 'text/plain'});
        var elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(file);
        elem.download = 'selected-data.txt';
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
        """,
)

# add Hover tool
# define what is displayed in the tooltip
tooltips = [
    ("X:", "@x"),
    ("Y:", "@y"),
    ("static text", "static text"),
]

fig02.add_tools(HoverTool(tooltips=tooltips))

# display results
# demo linked plots
# demo zooms and reset
# demo hover tool
# demo table
# demo save selected results to file

layout = grid([fig01, fig02, table, savebutton], ncols=3)

output_notebook()
show(layout)

# things to try:
# select random shape of blue dots with lasso tool in 'Select Here' graph
# only selected points appear as red dots in 'Watch Here' graph -- try zooming, saving that graph separately
# selected points also appear in the table, which is sortable
# click the 'Save' button to export a csv