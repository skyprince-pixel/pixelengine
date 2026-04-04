# Educational Features

PixelEngine includes purpose-built visualization tools for math, computer science, and science education.

---

## Math Objects

### ValueTracker

Animate numeric values and bind them to object properties:

```python
tracker = ValueTracker(0)
bar = Rect(10, 50, x=100, y=60, color="#FF004D")
bar.add_updater(lambda obj, dt: setattr(obj, 'height', max(1, int(50 * tracker.value / 100))))
self.add(bar)
self.play(tracker.animate_to(100), duration=2.0)
```

### NumberLine

```python
nl = NumberLine(x=50, y=135, length=380, num_ticks=10, color="#FFFFFF")
self.add(nl)
```

### Axes

```python
axes = Axes(x=50, y=30, width=200, height=150, x_label="x", y_label="f(x)", tick_count=5)
self.add(axes)
```

### Graph (Function Plotter)

```python
import math
graph = Graph(x=50, y=30, width=200, height=150,
              function=math.sin, x_range=(-3.14, 3.14), step=0.1, color="#00E436")
self.add(graph)
self.play(graph.animate_draw(), duration=2.0)
```

### AnimatedNumber

```python
counter = AnimatedNumber(value=0, x=200, y=100, color="#FFEC27", scale=2)
self.add(counter)
self.play(counter.animate_to(1000), duration=3.0)
```

---

## Charts

### BarChart

```python
chart = BarChart(x=50, y=30, width=180, height=120,
                 data=[30, 70, 50, 90],
                 labels=["Q1", "Q2", "Q3", "Q4"],
                 colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27"])
self.add(chart)
self.play(chart.animate_build(), duration=2.0)
```

### PieChart

```python
pie = PieChart(x=200, y=120, radius=50,
               data=[40, 30, 20, 10],
               labels=["A", "B", "C", "D"],
               colors=["#FF004D", "#00E436", "#29ADFF", "#FFEC27"])
self.add(pie)
self.play(pie.animate_build(), duration=2.0)
```

### ScatterPlot

```python
scatter = ScatterPlot(x=50, y=30, width=200, height=150,
                      points=[(10, 20), (30, 50), (60, 40), (80, 90)],
                      colors=["#FF004D"])
self.add(scatter)
self.play(scatter.animate_build(), duration=1.5)
```

### Histogram

```python
hist = Histogram(x=50, y=30, width=200, height=150,
                 data=[1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5, color="#29ADFF")
self.add(hist)
self.play(hist.animate_build(), duration=1.5)
```

---

## Tables & Matrices

### Table

```python
table = Table(rows=3, columns=4, cell_width=40, cell_height=20, x=50, y=50)
table.set_cell(0, 0, "Name")
table.set_cell(0, 1, "Age")
self.add(table)
```

### Matrix

```python
matrix = Matrix(rows=3, columns=3, x=100, y=50,
                elements=[[1, 0, 0], [0, 1, 0], [0, 0, 1]])
self.add(matrix)
```

---

## Data Structures

### DSArray

```python
arr = DSArray(elements=[5, 3, 8, 1, 9], x=50, y=100, width=200, height=40)
self.add(arr)
arr.highlight(2, color="#FF004D")  # Highlight index 2
arr.set_value(2, 99)               # Update value
```

### DSStack

```python
stack = DSStack(x=50, y=50, width=60, height=150)
self.add(stack)
stack.push(42)
stack.push(17)
stack.pop()
```

### DSQueue

```python
queue = DSQueue(x=50, y=100, width=200, height=40)
self.add(queue)
queue.enqueue(10)
queue.enqueue(20)
queue.dequeue()
```

### DSLinkedList

```python
ll = DSLinkedList(x=50, y=100, width=250, height=40)
self.add(ll)
ll.add_node(1)
ll.add_node(2)
ll.add_node(3)
```

### DSBinaryTree

```python
tree = DSBinaryTree(x=150, y=30, width=200, height=150)
self.add(tree)
for val in [5, 3, 7, 1, 4, 6, 8]:
    tree.insert(val)
```

### DSHeap

```python
heap = DSHeap(x=150, y=30, width=200, height=150)
self.add(heap)
for val in [10, 5, 20, 3, 8]:
    heap.insert(val)
```

### DSHashTable

```python
ht = DSHashTable(x=50, y=50, width=200, height=150)
self.add(ht)
ht.insert("name", "Alice")
ht.insert("age", "25")
```

### AlgorithmStepper

Step-by-step algorithm visualization:

```python
stepper = AlgorithmStepper(data=[5, 3, 8, 1])
self.add(stepper)
stepper.next_step()  # Advance algorithm one step
stepper.reset()      # Reset to beginning
```

---

## Graph Theory

### GraphViz

```python
graph = GraphViz(
    edges=[(0, 1), (1, 2), (2, 3), (0, 3), (1, 3)],
    node_count=4,
    x=50, y=30, width=200, height=150,
    directed=False,
    node_color="#29ADFF",
    edge_color="#FFFFFF"
)
self.add(graph)
graph.highlight_node(0, color="#FF004D")
graph.highlight_edge(0, 1, color="#00E436")
```

### Algorithm Animations

```python
# Breadth-first search
self.play(BFSAnimation(graph, start_node=0), duration=3.0)

# Depth-first search
self.play(DFSAnimation(graph, start_node=0), duration=3.0)

# Dijkstra's shortest path
self.play(DijkstraAnimation(graph, start_node=0), duration=4.0)
```

---

## Diagrams

### FlowChart

```python
flow = FlowChart(x=50, y=30)
# Add nodes and connectors to build process diagrams
self.add(flow)
```

### StateDiagram

```python
state = StateDiagram(x=50, y=30)
# Define states and transitions
self.add(state)
```

---

## Neural Networks

### NeuralNetwork

```python
nn = NeuralNetwork(
    layers=[3, 4, 4, 2],    # 3 input, two hidden(4), 2 output
    x=40, y=30, width=200, height=150,
    node_radius=6,
    node_color="#29ADFF",
    active_color="#FF004D",
    show_labels=True
)
self.add(nn)

# Build animation
self.play(nn.animate_build(), duration=1.5)

# Forward pass visualization
self.play(ForwardPassAnimation(nn, input_values=[0.5, 0.8, 0.3]), duration=3.0)

# Manual control
nn.set_activations(0, [1.0, 0.5, 0.8])
nn.activate_layer(1)
nn.clear_activations()
```

---

## Science

### Molecule

```python
# Preset molecules
water = Molecule.water()
methane = Molecule.methane()

# Custom
mol = Molecule(atoms=[...], bonds=[...], x=100, y=100, scale=2.0)
mol.rotate(0.5)  # Rotate by radians
self.add(mol)
```

### Circuit

```python
circuit = Circuit(components=[...], x=50, y=50, scale=1.0)
self.add(circuit)
```

### CellDiagram

```python
cell = CellDiagram(organelles=[...], x=150, y=120, scale=1.5)
self.add(cell)
```

---

## Geography

### WorldMap

```python
world = WorldMap(x=20, y=20, width=240, height=150,
                 ocean_color="#29ADFF", land_color="#00E436")
self.add(world)

# Highlight regions
world.highlight_region("europe", color="#FF004D")
world.highlight_region("asia", color="#FFEC27")

# Build animation
self.play(world.animate_build(), duration=3.0)
```

Available continents: `north_america`, `south_america`, `europe`, `africa`, `asia`, `oceania`

---

## Code Visualization

### CodeBlock

```python
code = CodeBlock(
    code="def hello():\n    print('Hi!')",
    language="python",     # "python", "javascript", "generic"
    theme="monokai",
    x=20, y=20, scale=1,
    show_line_numbers=True
)
self.add(code)

code.highlight_line(2, color="#FF004D")
code.show_variables({"x": "42", "name": "'Alice'"})
```

### CodeTrace

Step through code execution:

```python
trace = CodeTrace(code_block, steps=[
    {"line": 1, "vars": {"x": 0}},
    {"line": 2, "vars": {"x": 1}},
    {"line": 3, "vars": {"x": 2}},
])
self.play(trace, duration=3.0)
```

### DiffView

Side-by-side code comparison for showing before/after changes.

---

## Annotations

### Callout

```python
Callout(text="Note this!", target_x=100, target_y=50,
        x=150, y=30, style="bubble",      # "bubble", "arrow", "box"
        bg_color="#1D2B53", text_color="#FFFFFF")
```

### Label

```python
Label(text="Important", x=100, y=50, color="#FFFFFF",
      bg_color="#FF004D", scale=1, padding=2)
```

### Marker

```python
Marker(number=1, x=100, y=50, color="#FF004D", radius=6)
```

### HighlightBox

```python
HighlightBox(target=some_obj, color="#FFEC27", padding=3, thickness=1)
```

### PointerArrow

```python
PointerArrow(from_x=50, from_y=30, to_x=100, to_y=80,
             label="See here", color="#FFFFFF", head_size=6)
```

### AnnotationLayer

Group annotations into sequential steps:

```python
layer = AnnotationLayer(x=0, y=0)
layer.add_step(marker=Marker(1, 100, 50), highlight=HighlightBox(...))
layer.add_step(marker=Marker(2, 200, 80), arrow=PointerArrow(...))
self.add(layer)
self.play(layer.animate_to_step(1), duration=0.5)
self.play(layer.animate_to_step(2), duration=0.5)
```

---

## LaTeX

### MathTex

Render LaTeX equations (requires matplotlib):

```python
eq = MathTex(r"E = mc^2", x=135, y=240, color="#FFEC27", scale=1)
self.add(eq)
self.play(Create(eq), duration=1.5)

# Update equation
eq.set_tex(r"\int_0^\infty e^{-x} dx = 1")
```

---

## Music Notation

### MusicStaff

```python
staff = MusicStaff(x=20, y=100, width=200, line_spacing=4, note_spacing=20)
staff.add_note("C4", "quarter")
staff.add_note("E4", "quarter")
staff.add_note("G4", "half")
self.add(staff)
self.play(staff.animate_build(), duration=2.0)
```

**Note pitches:** C4 through B5
**Durations:** "whole", "half", "quarter", "eighth", "sixteenth"
