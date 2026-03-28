# SketchUp Ruby API Reference for Furniture Design

## Model Access
```ruby
model = Sketchup.active_model
entities = model.active_entities    # root-level drawing context
definitions = model.definitions     # all component definitions
materials = model.materials         # all materials
layers = model.layers              # all tags/layers
pages = model.pages                # all scenes
view = model.active_view           # current viewport
selection = model.selection        # currently selected entities
```

## Creating Lumber as Components

Components (not groups) are required for cut lists. Each distinct part is a ComponentDefinition; repeated parts share a definition.

```ruby
# Define a board once
defn = model.definitions.add("Side Rail")
defn.description = "Pine 2x4 side rail, 75 inches long"

# Draw cross-section and extrude (use make_box helper for reliability)
# Or for a component: create faces at origin within the definition
ents = defn.entities
face = ents.add_face([0,0,0],[1.5,0,0],[1.5,3.5,0],[0,3.5,0])
face.reverse! if face.normal.z < 0
face.pushpull(75)

# Place instances
t = Geom::Transformation.new([10, 0, 52])
instance = model.active_entities.add_instance(defn, t)
```

## Component Hierarchy for Furniture
```
Model Root
  [Group] "Loft Bed Assembly"
    [Group] "Module 0 - Core Frame"
      [Component] "Leg" x 4 (instances of same definition)
      [Component] "Side Rail" x 2
      [Component] "Slat" x N
    [Group] "Module 2 - Storage Stairs"
      [Group] "Column B1"
        [Component] "Side Panel" x 2
        [Component] "Shelf" x N
        [Component] "Drawer Box" x N
    [Group] "Hardware"
      [Component] "Hex Bolt M8x100" x N
```

## Tags (Layers) for Visibility
```ruby
frame_tag = model.layers.add("Frame")
hardware_tag = model.layers.add("Hardware")
joinery_tag = model.layers.add("Joinery")
dims_tag = model.layers.add("Dimensions")

instance.layer = frame_tag
```

## Materials by Wood Species
```ruby
pine = model.materials.add("Pine")
pine.color = [255, 223, 165]

oak = model.materials.add("White Oak")
oak.color = [210, 180, 130]

poplar = model.materials.add("Poplar")
poplar.color = [220, 210, 190]

birch = model.materials.add("Birch")
birch.color = [240, 220, 195]

instance.material = pine
```

## Custom Attributes (Metadata for Cut Lists)
```ruby
instance.set_attribute("woodworking", "species", "Pine")
instance.set_attribute("woodworking", "nominal_size", "1x12")
instance.set_attribute("woodworking", "finish", "Rubio Monocoat Pure")
instance.set_attribute("woodworking", "module", "2 - Storage Stairs")

species = instance.get_attribute("woodworking", "species")
```

## Transformations
```ruby
# Move
t_move = Geom::Transformation.translation([10, 0, 52])

# Rotate
origin = Geom::Point3d.new(0, 0, 0)
axis = Geom::Vector3d.new(0, 0, 1)
t_rot = Geom::Transformation.rotation(origin, axis, 90.degrees)

# Combined
t = t_move * t_rot
instance.transformation = t
```

## Scenes for Shop Drawings
```ruby
# Front Elevation (orthographic)
cam = Sketchup::Camera.new
cam.set(
  Geom::Point3d.new(22.5, -100, 40),
  Geom::Point3d.new(22.5, 37.5, 40),
  Geom::Vector3d.new(0, 0, 1)
)
cam.perspective = false
cam.height = 90

page = model.pages.add("Front Elevation")
page.use_camera = true
page.update(1)
```

Typical scene set:
1. Overall Assembly - Isometric
2. Front Elevation
3. Side Elevation
4. Top/Plan View
5. Exploded Assembly
6. Section: Cross-Section details
7. Joinery Detail views

## Section Planes
```ruby
sp = entities.add_section_plane([22.5, 37.5, 0], [0, 1, 0])
sp.name = "Platform Cross-Section"
sp.activate

# Deactivate
entities.active_section_plane = nil
```

## Dimensions & Annotations
```ruby
dim = entities.add_dimension_linear(
  [0, 0, 0], [45, 0, 0],
  [0, 0, 10]  # offset vector
)
dim.layer = model.layers["Dimensions"]

text = entities.add_text("Through-wedged tenon", [10, 20, 30], [0, 0, 15])
```

## Exploded View
```ruby
center = Geom::Point3d.new(22.5, 37.5, 30)
model.active_entities.each do |e|
  next unless e.is_a?(Sketchup::ComponentInstance)
  pos = e.bounds.center
  dir = pos - center
  dir.normalize! if dir.length > 0
  offset = Geom::Transformation.translation(
    Geom::Vector3d.new(dir.x * 15, dir.y * 15, dir.z * 15)
  )
  e.transform!(offset)
end
```

## Exporting
```ruby
# Screenshot
view.write_image({
  filename: '/path/to/view.png',
  width: 2400, height: 1800,
  antialias: true, transparent: true
})

# Save model
model.save('/path/to/project.skp')

# Export formats
model.export('/path/to/model.dae')  # Collada
model.export('/path/to/model.obj')  # OBJ
```

## Operations (Undo Support)
```ruby
model.start_operation('Create Stairs', true)
# ... all geometry changes ...
model.commit_operation
# Now all changes can be undone as one step
```

## Pushpull Inversion Helpers

The pushpull bug affects dados and bolt holes. These helpers handle verification and cleanup.

### drill_hole — Safe Bolt Hole Drilling
```ruby
def self.drill_hole(ents, center, normal, radius, depth)
  edges = ents.add_circle(center, normal, radius, 16)
  face = ents.add_face(edges)
  unless face
    face = edges.first.faces.select { |f| f.valid? && f.area < 0.5 }.first rescue nil
  end
  if face
    face.pushpull(-depth)
    true
  else
    false
  end
rescue => err
  false
end
```

### trim_extrusion — Fix Pushpull Inversions
```ruby
def self.trim_extrusion(defn, axis, max_val)
  to_del = []
  defn.entities.each do |ent|
    next unless ent.is_a?(Sketchup::Face) || ent.is_a?(Sketchup::Edge)
    verts = ent.is_a?(Sketchup::Face) ? ent.vertices : [ent.start, ent.end]
    over = case axis
    when :x then verts.any? { |v| v.position.x.to_f > max_val + 0.01 }
    when :y then verts.any? { |v| v.position.y.to_f > max_val + 0.01 }
    when :z then verts.any? { |v| v.position.z.to_f > max_val + 0.01 }
    when :neg_x then verts.any? { |v| v.position.x.to_f < max_val - 0.01 }
    when :neg_y then verts.any? { |v| v.position.y.to_f < max_val - 0.01 }
    end
    to_del << ent if over
  end
  to_del.each { |td| td.erase! if td.valid? }
end
```

**Usage pattern:** After every pushpull, check bounds. If they grew, trim:
```ruby
face.pushpull(-1.5)
if defn.bounds.max.y.to_f > 77.01
  trim_extrusion(defn, :y, 77.0)
  # Re-add the face that was removed
  defn.entities.add_face([0, 77, 0], [0, 77, h], [w, 77, h], [w, 77, 0])
end
```

### verify_all_bounds — Batch Verification
```ruby
def self.verify_bounds(entities, expected)
  # expected = { "RailB" => {x: [0,1.5], y: [0,77], z: [0,11.25]}, ... }
  issues = []
  expected.each do |name, dims|
    inst = entities.find { |e| e.is_a?(Sketchup::ComponentInstance) && e.definition.name == name }
    next unless inst
    bb = inst.definition.bounds
    dims.each do |axis, range|
      min_val = axis == :x ? bb.min.x : axis == :y ? bb.min.y : bb.min.z
      max_val = axis == :x ? bb.max.x : axis == :y ? bb.max.y : bb.max.z
      issues << "#{name} #{axis} min=#{min_val.to_f.round(2)}" if (min_val.to_f - range[0]).abs > 0.01
      issues << "#{name} #{axis} max=#{max_val.to_f.round(2)}" if (max_val.to_f - range[1]).abs > 0.01
    end
  end
  issues
end
```

## OpenCutList Compatibility

For models to work with OpenCutList:
- Parts MUST be Components (not Groups)
- Components must have volume > 0
- Axis orientation: red = length (grain), green = width, blue = thickness
- Materials must be applied per component
- Name components descriptively ("Side Panel - B1", not "Group#12")
