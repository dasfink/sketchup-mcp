"""Ruby code templates for SketchUp MCP furniture tools.

Architecture: Each function returns a Ruby code string sent via eval_ruby.
Key patterns:
- 6-face box construction (never pushpull for new geometry)
- Boolean subtract via Group#subtract for material removal (dados, holes)
- State-before-page for scene creation
- JSON return values from every geometry operation
"""


def boolean_subtract_ruby(target: str, cutter_type: str, position: list,
                          dimensions: list, axis: list = None) -> str:
    """Boolean subtract a shape from a component using SketchUp Pro Solid Tools.

    target: component definition name
    cutter_type: 'box' or 'cylinder'
    position: [x, y, z] in component-local coords
    dimensions: box=[w, d, h], cylinder=[length, radius, 0]
    axis: cylinder direction [nx, ny, nz], default [1, 0, 0]
    """
    x, y, z = position

    if cutter_type == "box":
        w, d, h = dimensions
        cutter_geometry = f'''
    cg = cutter.entities
    cg.add_face([0,0,0],[{w},0,0],[{w},{d},0],[0,{d},0])
    cg.add_face([0,0,{h}],[0,{d},{h}],[{w},{d},{h}],[{w},0,{h}])
    cg.add_face([0,0,0],[{w},0,0],[{w},0,{h}],[0,0,{h}])
    cg.add_face([0,{d},0],[0,{d},{h}],[{w},{d},{h}],[{w},{d},0])
    cg.add_face([0,0,0],[0,0,{h}],[0,{d},{h}],[0,{d},0])
    cg.add_face([{w},0,0],[{w},{d},0],[{w},{d},{h}],[{w},0,{h}])'''
    elif cutter_type == "cylinder":
        length, radius, _ = dimensions
        ax = axis or [1, 0, 0]
        cutter_geometry = f'''
    cg = cutter.entities
    normal = Geom::Vector3d.new({ax[0]}, {ax[1]}, {ax[2]})
    edges = cg.add_circle(Geom::Point3d.new(0, 0, 0), normal, {radius}, 24)
    face = cg.add_face(edges)
    unless face
      face = edges.first.faces.select {{ |f| f.valid? && f.area < 0.5 }}.first rescue nil
    end
    face.pushpull({length}) if face'''
    else:
        raise ValueError(f"Unknown cutter_type: {cutter_type}")

    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Boolean subtract from {target}', true)

inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{target}" }}
raise "Component {target} not found" unless inst

# Convert ComponentInstance to Group for boolean operations
comp_origin = inst.transformation.origin
temp_group = inst.to_group

# Create cutter group at the component's position + local offset
cutter = e.add_group
{cutter_geometry}
    cutter_offset = Geom::Transformation.new([comp_origin.x + {x}, comp_origin.y + {y}, comp_origin.z + {z}])
    cutter.transform!(cutter_offset)

# Boolean subtract — deterministic, no pushpull inversion
result = temp_group.subtract(cutter)

if result
  bb = result.bounds
  m.commit_operation
  '{{"success": true, "bounds": [' + bb.min.x.to_f.round(2).to_s + ',' + bb.min.y.to_f.round(2).to_s + ',' + bb.min.z.to_f.round(2).to_s + ',' + bb.max.x.to_f.round(2).to_s + ',' + bb.max.y.to_f.round(2).to_s + ',' + bb.max.z.to_f.round(2).to_s + ']}}'
else
  cutter.erase! if cutter.valid?
  m.abort_operation
  '{{"success": false, "error": "subtract failed — target or cutter may not be solid"}}'
end
'''


def make_box_ruby(name: str, position: list, dimensions: list,
                  material: str, tag: str, attrs: dict) -> str:
    """Create a box component using 6-face construction. Never pushpull."""
    x, y, z = position
    w, d, h = dimensions
    attr_lines = "\n".join(
        f'inst.set_attribute("woodworking", "{k}", "{v}")'
        for k, v in attrs.items()
    )
    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Create {name}', true)

defn = m.definitions.add("{name}")
de = defn.entities
w, d, h = {w}, {d}, {h}
de.add_face([0,0,0],[w,0,0],[w,d,0],[0,d,0])
de.add_face([0,0,h],[0,d,h],[w,d,h],[w,0,h])
de.add_face([0,0,0],[w,0,0],[w,0,h],[0,0,h])
de.add_face([0,d,0],[0,d,h],[w,d,h],[w,d,0])
de.add_face([0,0,0],[0,0,h],[0,d,h],[0,d,0])
de.add_face([w,0,0],[w,d,0],[w,d,h],[w,0,h])

t = Geom::Transformation.new([{x}, {y}, {z}])
inst = e.add_instance(defn, t)

mat = m.materials["{material}"] || m.materials.add("{material}")
mat.color = Sketchup::Color.new(255, 223, 170) unless mat.color
inst.material = mat

tag_layer = m.layers["{tag}"] || m.layers.add("{tag}")
inst.layer = tag_layer

{attr_lines}

bb = defn.bounds
m.commit_operation
'{{"success": true, "name": "{name}", "bounds": [' + bb.max.x.to_f.round(2).to_s + ',' + bb.max.y.to_f.round(2).to_s + ',' + bb.max.z.to_f.round(2).to_s + ']}}'
'''


def safe_cut_dado_ruby(component_name: str, face: str,
                       z_start: float, z_end: float, depth: float) -> str:
    """Cut a dado via boolean subtract. No pushpull inversion possible.

    face: 'x+', 'x-', 'y+', 'y-' — which face to cut into.
    """
    height = z_end - z_start

    # Map face orientation to cutter position/dimensions relative to component bounds
    # The Ruby code queries bounds at runtime to get actual dimensions
    cutter_configs = {
        "x+": {
            "pos": f"[bb_max_x - {depth}, 0, {z_start}]",
            "dims": f"[{depth}, bb_max_y, {height}]",
        },
        "x-": {
            "pos": f"[0, 0, {z_start}]",
            "dims": f"[{depth}, bb_max_y, {height}]",
        },
        "y+": {
            "pos": f"[0, bb_max_y - {depth}, {z_start}]",
            "dims": f"[bb_max_x, {depth}, {height}]",
        },
        "y-": {
            "pos": f"[0, 0, {z_start}]",
            "dims": f"[bb_max_x, {depth}, {height}]",
        },
    }
    cfg = cutter_configs[face]

    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Dado in {component_name} ({face})', true)

inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{component_name}" }}
raise "Component {component_name} not found" unless inst

# Get bounds to compute cutter position
bb = inst.definition.bounds
bb_max_x = bb.max.x.to_f
bb_max_y = bb.max.y.to_f
comp_origin = inst.transformation.origin

# Convert to group for boolean
temp_group = inst.to_group

# Build cutter box
pos = {cfg["pos"]}
dims = {cfg["dims"]}
cutter = e.add_group
cg = cutter.entities
w, d, h = dims[0], dims[1], dims[2]
cg.add_face([0,0,0],[w,0,0],[w,d,0],[0,d,0])
cg.add_face([0,0,h],[0,d,h],[w,d,h],[w,0,h])
cg.add_face([0,0,0],[w,0,0],[w,0,h],[0,0,h])
cg.add_face([0,d,0],[0,d,h],[w,d,h],[w,d,0])
cg.add_face([0,0,0],[0,0,h],[0,d,h],[0,d,0])
cg.add_face([w,0,0],[w,d,0],[w,d,h],[w,0,h])
cutter.transform!(Geom::Transformation.new([comp_origin.x + pos[0], comp_origin.y + pos[1], comp_origin.z + pos[2]]))

result = temp_group.subtract(cutter)

if result
  rbb = result.bounds
  m.commit_operation
  '{{"success": true, "face": "{face}", "bounds": [' + rbb.min.x.to_f.round(2).to_s + ',' + rbb.min.y.to_f.round(2).to_s + ',' + rbb.min.z.to_f.round(2).to_s + ',' + rbb.max.x.to_f.round(2).to_s + ',' + rbb.max.y.to_f.round(2).to_s + ',' + rbb.max.z.to_f.round(2).to_s + ']}}'
else
  cutter.erase! if cutter.valid?
  m.abort_operation
  '{{"success": false, "error": "subtract failed for dado on {face}"}}'
end
'''


def safe_drill_hole_ruby(component_name: str, center: list, normal: list,
                         radius: float, depth: float) -> str:
    """Drill a hole via boolean subtract. No add_face nil issues."""
    return boolean_subtract_ruby(component_name, "cylinder",
                                 center, [depth, radius, 0], normal)


def verify_bounds_ruby(expected: dict) -> str:
    """Check component bounds against expected dimensions."""
    checks = []
    for name, dims in expected.items():
        for axis, (lo, hi) in dims.items():
            checks.append(f'''
  inst = e.find {{ |ent| ent.is_a?(Sketchup::ComponentInstance) && ent.definition.name == "{name}" }}
  if inst
    bb = inst.definition.bounds
    issues << "{name} {axis} min=#{{bb.min.{axis}.to_f.round(2)}} exp={lo}" if (bb.min.{axis}.to_f - {lo}).abs > 0.01
    issues << "{name} {axis} max=#{{bb.max.{axis}.to_f.round(2)}} exp={hi}" if (bb.max.{axis}.to_f - {hi}).abs > 0.01
  else
    issues << "{name}: NOT FOUND"
  end''')

    checks_code = "\n".join(checks)
    return f'''
m = Sketchup.active_model
e = m.active_entities
issues = []
{checks_code}
if issues.empty?
  '{{"all_clean": true}}'
else
  '{{"all_clean": false, "issues": [' + issues.map {{ |i| '"' + i + '"' }}.join(",") + ']}}'
end
'''


def take_screenshot_ruby(scene_name: str = None, width: int = 1920,
                         height: int = 1080, hide_tags: list = None) -> str:
    """Activate a scene, disable transitions, capture screenshot."""
    scene_code = ""
    if scene_name:
        scene_code = f'''
m.options["PageOptions"]["ShowTransition"] = false
page = m.pages.find {{ |p| p.name == "{scene_name}" }}
m.pages.selected_page = page if page'''

    hide_code = ""
    if hide_tags:
        hide_list = ", ".join(f'"{t}"' for t in hide_tags)
        hide_code = f'''
[{hide_list}].each {{ |t| l = m.layers[t]; l.visible = false if l }}'''

    return f'''
m = Sketchup.active_model
{scene_code}
{hide_code}
path = File.join(Dir.tmpdir, "sketchup_screenshot_#{{Time.now.to_i}}.png")
m.active_view.write_image(path, {width}, {height}, true)
path
'''


def create_scene_ruby(name: str, eye: list, target: list, up: list,
                      perspective: bool = True, height: float = 90,
                      visible_tags: list = None,
                      section_point: list = None,
                      section_normal: list = None) -> str:
    """Create a scene. Sets layers, camera, section plane BEFORE pages.add."""
    vis_code = ""
    if visible_tags:
        tag_list = ", ".join(f'"{t}"' for t in visible_tags)
        vis_code = f'''
visible = [{tag_list}]
m.layers.each {{ |l| next if l.name == "Layer0"; l.visible = visible.include?(l.name) }}'''

    section_code = ""
    if section_point and section_normal:
        sp, sn = section_point, section_normal
        section_code = f'''
sp = m.active_entities.add_section_plane([{sp[0]}, {sp[1]}, {sp[2]}], [{sn[0]}, {sn[1]}, {sn[2]}])
sp.activate'''

    persp = "true" if perspective else "false"
    height_line = "" if perspective else f"\ncam.height = {height}"

    return f'''
m = Sketchup.active_model
v = m.active_view

# 1. Set layer visibility
{vis_code}

# 2. Section plane
{section_code}

# 3. Set camera
cam = Sketchup::Camera.new
cam.set(
  Geom::Point3d.new({eye[0]}, {eye[1]}, {eye[2]}),
  Geom::Point3d.new({target[0]}, {target[1]}, {target[2]}),
  Geom::Vector3d.new({up[0]}, {up[1]}, {up[2]})
)
cam.perspective = {persp}{height_line}
v.camera = cam

# 4. Add page (captures current state)
page = m.pages.add("{name}")
page.use_camera = true

'{{"success": true, "scene": "{name}", "perspective": ' + cam.perspective?.to_s + ', "visible_tags": [' + m.layers.select {{ |l| l.visible? && l.name != "Layer0" }}.map {{ |l| '"' + l.name + '"' }}.join(",") + ']}}'
'''


def verify_scenes_ruby() -> str:
    """Cycle through all scenes and report camera + layer state."""
    return '''
m = Sketchup.active_model
m.options["PageOptions"]["ShowTransition"] = false
results = []

m.pages.each do |page|
  m.pages.selected_page = page
  visible = m.layers.select { |l| l.visible? && l.name != "Layer0" }.map(&:name)
  cam = page.camera
  results << '{"name": "' + page.name + '", "perspective": ' + (cam ? cam.perspective?.to_s : "null") + ', "visible_tags": [' + visible.map { |v| '"' + v + '"' }.join(",") + ']}'
end

'[' + results.join(",") + ']'
'''


def generate_cutlist_ruby(auto_orient: bool = True,
                          part_folding: bool = True) -> str:
    """Invoke OpenCutList and return structured JSON."""
    ao = "true" if auto_orient else "false"
    pf = "true" if part_folding else "false"
    return f'''
worker = Ladb::OpenCutList::CutlistGenerateWorker.new(
  auto_orient: {ao},
  smart_material: true,
  part_folding: {pf}
)
cl = worker.run

parts = []
cl.groups.each do |g|
  g.parts.each do |p|
    parts << '{{"name": "' + p.name + '", "qty": ' + p.count.to_s + ', "length": "' + p.cutting_length.to_s + '", "width": "' + p.cutting_width.to_s + '", "thickness": "' + p.cutting_thickness.to_s + '"}}'
  end
end

'{{"success": true, "parts": [' + parts.join(",") + ']}}'
'''


def exploded_view_ruby(offsets: dict, tag_name: str = "Exploded") -> str:
    """Duplicate components at Z offsets onto a separate tag."""
    offset_cases = "\n".join(
        f'    when "{tag}" then {z_off}'
        for tag, z_off in offsets.items()
    )
    return f'''
m = Sketchup.active_model
e = m.active_entities
m.start_operation('Create exploded view', true)

exploded_tag = m.layers["{tag_name}"] || m.layers.add("{tag_name}")
count = 0

e.each do |ent|
  next unless ent.is_a?(Sketchup::ComponentInstance)
  tag = ent.layer.name
  z_off = case tag
{offset_cases}
  else next
  end

  copy = ent.copy
  copy.transform!(Geom::Transformation.translation([0, 0, z_off]))
  copy.layer = exploded_tag
  count += 1
end

m.commit_operation
'{{"success": true, "copies": ' + count.to_s + ', "tag": "{tag_name}"}}'
'''
