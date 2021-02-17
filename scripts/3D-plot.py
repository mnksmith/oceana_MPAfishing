from collections import Counter
from collections import namedtuple
from random import randint

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


Category = namedtuple('Category', ['name', 'rank'])
Warehouse = namedtuple('Warehouse', ['name', 'rank'])
Bar = namedtuple('Bar', ['instance', 'height'])
DataRow = namedtuple('DataRow', ['category', 'warehouse'])

CATEGORIES = [Category('C_NAME', i) for i in range(20)]  # cats ranking
WAREHOUSES = [Warehouse('W_NAME', i) for i in range(20)]  # warehouses ranking

c_count = len(CATEGORIES)
wh_count = len(WAREHOUSES)

ROWS_COUNT = 100  # number of rows to render in test case

DATA = [DataRow(randint(0, c_count), randint(0, wh_count)) for i in range(ROWS_COUNT)]  # test data

COLOR_MAP = {}  # can specify colors for certain cat / wh
CACHE_CHUNK_SIZE = 5


# define update function
def update(num, bars_collection: dict) -> dict:
    cache = [DATA.pop(0) for i in range(CACHE_CHUNK_SIZE) if DATA]
    if cache:
        prepared_cache = Counter(cache)
        for row, count in prepared_cache.items():
            if row in bars_collection:
                current_bar: Bar = bars_collection[row]
                bars_collection[row]: dict = Bar(ax.bar3d(
                    row.category, row.warehouse, 0, 1, 1, current_bar.height + count,
                    color=COLOR_MAP.get(row, 'b'),
                    alpha=0.8), current_bar.height + count)
            else:
                bars_collection[row] = Bar(ax.bar3d(
                    row.category, row.warehouse, 0, 1, 1, 1,
                    color=COLOR_MAP.get(row, 'b'),
                    alpha=0.2), 1)  # tuple

    return bars_collection

# create figure
fig = plt.figure()
ax = p3.Axes3D(fig)

line_ani = animation.FuncAnimation(fig, update, 100, fargs=[dict()], interval=50, blit=False)

# add labels
ax.w_xaxis.set_ticklabels([c.name for c in CATEGORIES])
ax.w_yaxis.set_ticklabels([w.name for w in WAREHOUSES])
ax.set_xlabel('Categories')
ax.set_ylabel('Warehouses')
ax.set_zlabel('SKU count')

# perform
plt.show()