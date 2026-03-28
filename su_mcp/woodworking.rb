# WW — Woodworking Helper Library for SketchUp MCP
# Provides high-level woodworking operations called via eval_ruby.
# All dimensions in inches (SketchUp native unit).

module WW
  # Nominal lumber size → [thickness, width] in actual inches
  LUMBER = {
    "1x2"   => [0.75, 1.5],
    "1x3"   => [0.75, 2.5],
    "1x4"   => [0.75, 3.5],
    "1x6"   => [0.75, 5.5],
    "1x8"   => [0.75, 7.25],
    "1x10"  => [0.75, 9.25],
    "1x12"  => [0.75, 11.25],
    "2x2"   => [1.5, 1.5],
    "2x3"   => [1.5, 2.5],
    "2x4"   => [1.5, 3.5],
    "2x6"   => [1.5, 5.5],
    "2x8"   => [1.5, 7.25],
    "2x10"  => [1.5, 9.25],
    "2x12"  => [1.5, 11.25],
    "4x4"   => [3.5, 3.5],
    "4x6"   => [3.5, 5.5],
    "6x6"   => [5.5, 5.5],
    "5/4x4" => [1.0, 3.5],
    "5/4x6" => [1.0, 5.5],
    "5/4x8" => [1.0, 7.25],
  }.freeze

  # Named material colors
  MATERIALS = {
    "Pine"       => [255, 223, 170],
    "White Oak"  => [210, 180, 130],
    "Red Oak"    => [190, 140, 90],
    "Walnut"     => [90, 60, 40],
    "Cherry"     => [180, 100, 60],
    "Maple"      => [240, 220, 190],
    "Birch"      => [235, 215, 185],
    "Poplar"     => [210, 210, 180],
    "Cedar"      => [180, 120, 80],
  }.freeze

  @boards = {}

  class << self
    # ─── STOCK & STRUCTURE ───────────────────────────────────────

    # Create a board from nominal lumber size or exact dimensions.
    #
    # Usage:
    #   WW.board("Side Rail", "2x8", 83)                    # nominal
    #   WW.board("Shelf Cap", [1.0, 5.0, 78], material: "White Oak")  # exact [t, w, l]
    #   WW.board("Panel", [0.75, 11.25], length: 28.5)     # exact [t, w] + length
    #
    # Default orientation: length along X, width along Y, thickness along Z.
    # This means the board lies flat. Use WW.orient() to stand it on edge.
    def board(name, size, length = nil, material: nil)
      model = Sketchup.active_model
      entities = model.active_entities

      if size.is_a?(String)
        dims = LUMBER[size]
        raise "Unknown lumber size: #{size}. Known sizes: #{LUMBER.keys.join(', ')}" unless dims
        raise "Length required for nominal lumber" unless length
        thickness, width = dims
        nominal = size
      elsif size.is_a?(Array)
        if size.length == 3
          thickness, width, length = size
        elsif size.length == 2
          thickness, width = size
          raise "Length required when size is [thickness, width]" unless length
        else
          raise "Size array must be [t, w] or [t, w, l]"
        end
        nominal = "#{thickness}x#{width}"
      else
        raise "Size must be a String (nominal like '2x8') or Array ([t, w, l])"
      end

      group = entities.add_group
      group.name = name

      # Create board: length along X, width along Y, thickness along Z
      pts = [
        Geom::Point3d.new(0, 0, 0),
        Geom::Point3d.new(length, 0, 0),
        Geom::Point3d.new(length, width, 0),
        Geom::Point3d.new(0, width, 0),
      ]
      face = group.entities.add_face(pts)
      face.reverse! if face.normal.z < 0
      face.pushpull(thickness)

      # Apply material
      if material
        apply_material(group, material)
      end

      # Store metadata
      group.set_attribute("WW", "type", "board")
      group.set_attribute("WW", "name", name)
      group.set_attribute("WW", "nominal", nominal)
      group.set_attribute("WW", "length", length.to_f)
      group.set_attribute("WW", "width", width.to_f)
      group.set_attribute("WW", "thickness", thickness.to_f)
      group.set_attribute("WW", "material", material.to_s)

      @boards[name] = group
      group
    end

    # Create an edge-glued panel (same as board but semantically different)
    def panel(name, size, width: nil, depth: nil, material: nil)
      if size.is_a?(String)
        dims = LUMBER[size]
        raise "Unknown lumber size: #{size}" unless dims
        thickness = dims[0]
        w = width || dims[1]
        d = depth || dims[1]
      else
        thickness = size
        w = width
        d = depth
      end
      board(name, [thickness, w, d], material: material)
    end

    # Create an organizational group (module/assembly container)
    def module_group(name)
      model = Sketchup.active_model
      group = model.active_entities.add_group
      group.name = name
      group.set_attribute("WW", "type", "module")
      group.set_attribute("WW", "name", name)
      group
    end

    # Move entities into a group
    def add_to(group, *ents)
      ents.flatten.each do |ent|
        next unless ent.valid?
        # Move entity into the group by transforming to group's local space
        temp = group.entities.add_group(ent)
        temp.explode
      end
    end

    # Position an entity at [x, y, z]
    def place(entity, position = nil, x: nil, y: nil, z: nil)
      entity = resolve(entity)
      if position
        px, py, pz = position
      else
        px = x || 0
        py = y || 0
        pz = z || 0
      end
      # Move from current position to target
      current = entity.bounds.min
      vec = Geom::Vector3d.new(px - current.x, py - current.y, pz - current.z)
      entity.transform!(Geom::Transformation.translation(vec))
      entity
    end

    # Rotate entity around an axis
    def rotate(entity, axis, angle_degrees)
      entity = resolve(entity)
      center = entity.bounds.center
      axis_vec = case axis
                 when :x then Geom::Vector3d.new(1, 0, 0)
                 when :y then Geom::Vector3d.new(0, 1, 0)
                 when :z then Geom::Vector3d.new(0, 0, 1)
                 when Array then Geom::Vector3d.new(*axis)
                 else axis
                 end
      angle_rad = angle_degrees * Math::PI / 180.0
      t = Geom::Transformation.rotation(center, axis_vec, angle_rad)
      entity.transform!(t)
      entity
    end

    # Orient a board to stand on edge (swap Y and Z)
    # Useful for rails, posts, etc. that stand upright.
    def on_edge(entity)
      entity = resolve(entity)
      center = entity.bounds.center
      t = Geom::Transformation.rotation(center, Geom::Vector3d.new(1, 0, 0), -90.degrees)
      entity.transform!(t)
      entity
    end

    # ─── JOINERY ─────────────────────────────────────────────────

    # Cut a dado (channel across the board).
    # Uses direct geometry editing inside the group (no boolean subtract needed).
    # face: :top, :bottom, :front, :back, :inner
    # at: distance from X=0 end (left end) to the start of the dado
    # width: width of the dado along X
    # depth: depth of the cut into the board
    def dado(board_ref, face: :top, at:, width:, depth:)
      grp = resolve(board_ref)
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]

      ents = grp.entities
      case face
      when :top
        # Draw rectangle on top face (Z = bthk) and push down
        pts = [
          Geom::Point3d.new(at, 0, bthk),
          Geom::Point3d.new(at + width, 0, bthk),
          Geom::Point3d.new(at + width, bwid, bthk),
          Geom::Point3d.new(at, bwid, bthk),
        ]
        f = ents.add_face(pts)
        f.pushpull(-depth) if f
      when :bottom
        pts = [
          Geom::Point3d.new(at, 0, 0),
          Geom::Point3d.new(at + width, 0, 0),
          Geom::Point3d.new(at + width, bwid, 0),
          Geom::Point3d.new(at, bwid, 0),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      when :front, :inner
        # Y=0 face, push into the board (+Y direction)
        pts = [
          Geom::Point3d.new(at, 0, 0),
          Geom::Point3d.new(at + width, 0, 0),
          Geom::Point3d.new(at + width, 0, bthk),
          Geom::Point3d.new(at, 0, bthk),
        ]
        f = ents.add_face(pts)
        f.pushpull(-depth) if f
      when :back
        pts = [
          Geom::Point3d.new(at, bwid, 0),
          Geom::Point3d.new(at + width, bwid, 0),
          Geom::Point3d.new(at + width, bwid, bthk),
          Geom::Point3d.new(at, bwid, bthk),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      end
      grp
    end

    # Cut a rabbet (step along an edge). Uses direct geometry editing.
    # edge: :back_inner, :back, :front, :top_back, :bottom_back
    def rabbet(board_ref, edge: :back_inner, width:, depth:)
      grp = resolve(board_ref)
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]
      ents = grp.entities

      case edge
      when :back_inner, :back
        # Remove strip from back-bottom corner, full length
        pts = [
          Geom::Point3d.new(0, bwid - width, 0),
          Geom::Point3d.new(blen, bwid - width, 0),
          Geom::Point3d.new(blen, bwid, 0),
          Geom::Point3d.new(0, bwid, 0),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      when :front
        pts = [
          Geom::Point3d.new(0, 0, 0),
          Geom::Point3d.new(blen, 0, 0),
          Geom::Point3d.new(blen, width, 0),
          Geom::Point3d.new(0, width, 0),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      when :top_back
        pts = [
          Geom::Point3d.new(0, bwid - width, bthk),
          Geom::Point3d.new(blen, bwid - width, bthk),
          Geom::Point3d.new(blen, bwid, bthk),
          Geom::Point3d.new(0, bwid, bthk),
        ]
        f = ents.add_face(pts)
        f.pushpull(-depth) if f
      when :bottom_back
        pts = [
          Geom::Point3d.new(0, bwid - width, 0),
          Geom::Point3d.new(blen, bwid - width, 0),
          Geom::Point3d.new(blen, bwid, 0),
          Geom::Point3d.new(0, bwid, 0),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      end
      grp
    end

    # Cut a groove (channel with the grain, runs along X). Uses direct geometry editing.
    # from_edge: distance from Y=0 (front) to the groove
    def groove(board_ref, face: :inside, from_edge:, width:, depth:)
      grp = resolve(board_ref)
      dims = board_dims(grp)
      blen = dims[:length]
      bthk = dims[:thickness]
      bwid = dims[:width]
      ents = grp.entities

      case face
      when :inside, :bottom
        pts = [
          Geom::Point3d.new(0, from_edge, 0),
          Geom::Point3d.new(blen, from_edge, 0),
          Geom::Point3d.new(blen, from_edge + width, 0),
          Geom::Point3d.new(0, from_edge + width, 0),
        ]
        f = ents.add_face(pts)
        f.pushpull(depth) if f
      when :top
        pts = [
          Geom::Point3d.new(0, from_edge, bthk),
          Geom::Point3d.new(blen, from_edge, bthk),
          Geom::Point3d.new(blen, from_edge + width, bthk),
          Geom::Point3d.new(0, from_edge + width, bthk),
        ]
        f = ents.add_face(pts)
        f.pushpull(-depth) if f
      end
      grp
    end

    # Cut a mortise (rectangular pocket or through-hole).
    # Uses direct geometry editing (face + pushpull inside the group).
    # face: which face the mortise opens on
    # at: [x_pos, z_pos] position on the face
    # size: [width, height] of the mortise opening
    # depth: how deep
    # through: if true, cuts all the way through
    def mortise(board_ref, face: :front, at:, size:, depth:, through: false)
      grp = resolve(board_ref)
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]
      ents = grp.entities

      mw, mh = size
      mx, mz = at
      actual_depth = through ? bwid : depth

      case face
      when :front
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(x, 0, z) }
        f = ents.add_face(pts)
        f.pushpull(-actual_depth) if f
      when :back
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(x, bwid, z) }
        f = ents.add_face(pts)
        f.pushpull(actual_depth) if f
      when :left
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(0, x, z) }
        f = ents.add_face(pts)
        f.pushpull(-actual_depth) if f
      when :right
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(blen, x, z) }
        f = ents.add_face(pts)
        f.pushpull(actual_depth) if f
      when :top
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(x, z, bthk) }
        f = ents.add_face(pts)
        f.pushpull(-actual_depth) if f
      when :bottom
        pts = rect_pts(mx, mz, mw, mh) { |x, z| Geom::Point3d.new(x, z, 0) }
        f = ents.add_face(pts)
        f.pushpull(actual_depth) if f
      end
      grp
    end

    # Create a tenon on the end of a board.
    # Removes material around the tenon, leaving it proud.
    # end_face: :left (X=0) or :right (X=length)
    # size: [width, height] of the tenon cross-section
    # length: how far the tenon extends
    # kerf: if > 0, adds a wedge kerf slot of that width
    def tenon(board_ref, end_face: :right, size:, length:, kerf: 0)
      grp = resolve(board_ref)
      model = Sketchup.active_model
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]

      tw, th = size
      # Center the tenon on the end face
      cy = bwid / 2.0
      cz = bthk / 2.0

      # We need to cut away the material around the tenon on the end
      # Create 4 cutter boxes (top, bottom, left, right of tenon)
      cutters = []

      shoulder_depth = length  # How much to cut back from the end

      if end_face == :right
        sx = blen - shoulder_depth
        # Bottom strip
        cutters << [sx, 0, 0, shoulder_depth, bwid, cz - th / 2.0]
        # Top strip
        cutters << [sx, 0, cz + th / 2.0, shoulder_depth, bwid, bthk - (cz + th / 2.0)]
        # Front strip (between top and bottom)
        cutters << [sx, 0, cz - th / 2.0, shoulder_depth, cy - tw / 2.0, th]
        # Back strip
        cutters << [sx, cy + tw / 2.0, cz - th / 2.0, shoulder_depth, bwid - (cy + tw / 2.0), th]
      else
        # Left end
        # Bottom strip
        cutters << [0, 0, 0, shoulder_depth, bwid, cz - th / 2.0]
        # Top strip
        cutters << [0, 0, cz + th / 2.0, shoulder_depth, bwid, bthk - (cz + th / 2.0)]
        # Front strip
        cutters << [0, 0, cz - th / 2.0, shoulder_depth, cy - tw / 2.0, th]
        # Back strip
        cutters << [0, cy + tw / 2.0, cz - th / 2.0, shoulder_depth, bwid - (cy + tw / 2.0), th]
      end

      cutter_group = model.active_entities.add_group
      cutters.each do |c|
        x, y, z, w, d, h = c
        next if w <= 0 || d <= 0 || h <= 0
        make_box(cutter_group.entities, x, y, z, w, d, h)
      end

      cutter_group.transform!(grp.transformation)
      result = subtract_and_track(board_ref, grp, cutter_group)

      # Add wedge kerf if requested
      if kerf > 0 && result && result.valid?
        kerf_cutter = model.active_entities.add_group
        if end_face == :right
          kx = blen - length * 0.75
          make_box(kerf_cutter.entities, kx, cy - kerf / 2.0, cz - th / 2.0, length * 0.75, kerf, th)
        else
          make_box(kerf_cutter.entities, 0, cy - kerf / 2.0, cz - th / 2.0, length * 0.75, kerf, th)
        end
        kerf_cutter.transform!(result.transformation)
        result = subtract_and_track(board_ref, result, kerf_cutter)
      end
      result
    end

    # Cut a half-lap notch.
    # at: distance along X to the center of the notch
    # width: width of the notch along X
    # depth: depth into the board (usually half the thickness)
    def half_lap(board_ref, face: :top, at:, width:, depth:)
      dado(board_ref, face: face, at: at - width / 2.0, width: width, depth: depth)
    end

    # ─── SHAPING ─────────────────────────────────────────────────

    # Taper one or more faces of a board.
    # faces: array of face symbols, e.g. [:front, :right]
    # from: original dimension at the start
    # to: final dimension at the end
    # start: distance from X=0 where taper begins
    # over: length of the taper
    def taper(board_ref, faces:, from:, to:, start:, over:)
      grp = resolve(board_ref)
      model = Sketchup.active_model
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]

      taper_amount = (from - to) / 2.0  # per side

      faces = [faces] unless faces.is_a?(Array)
      faces.each do |f|
        cutter = model.active_entities.add_group
        case f
        when :front
          # Taper on Y=0 face: remove a wedge from Y=0
          pts = [
            Geom::Point3d.new(start, 0, 0),
            Geom::Point3d.new(start + over, 0, 0),
            Geom::Point3d.new(start + over, taper_amount, 0),
            Geom::Point3d.new(start, 0, 0),  # no taper at start
          ]
          # Create a triangular face and extrude
          tri_face = cutter.entities.add_face(
            Geom::Point3d.new(start, 0, 0),
            Geom::Point3d.new(start + over, 0, 0),
            Geom::Point3d.new(start + over, taper_amount, 0)
          )
          tri_face.pushpull(bthk) if tri_face

        when :back
          tri_face = cutter.entities.add_face(
            Geom::Point3d.new(start, bwid, 0),
            Geom::Point3d.new(start + over, bwid, 0),
            Geom::Point3d.new(start + over, bwid - taper_amount, 0)
          )
          tri_face.pushpull(bthk) if tri_face

        when :right
          # Taper on the Y dimension from the right side
          tri_face = cutter.entities.add_face(
            Geom::Point3d.new(start, bwid, 0),
            Geom::Point3d.new(start + over, bwid, 0),
            Geom::Point3d.new(start + over, bwid - taper_amount, 0)
          )
          tri_face.pushpull(bthk) if tri_face

        when :left
          tri_face = cutter.entities.add_face(
            Geom::Point3d.new(start, 0, 0),
            Geom::Point3d.new(start + over, 0, 0),
            Geom::Point3d.new(start + over, taper_amount, 0)
          )
          tri_face.pushpull(bthk) if tri_face
        end

        if cutter.entities.length > 0
          cutter.transform!(grp.transformation)
          grp = subtract_and_track(board_ref, grp, cutter)
        else
          cutter.erase! if cutter.valid?
        end
      end
      grp
    end

    # Chamfer edges. Currently applies a simple visual chamfer by
    # cutting corners off the board ends/edges.
    # edges: :all, :top, :front_top, etc.
    # size: chamfer width (e.g., 0.125 for 1/8")
    def chamfer(board_ref, edges: :all, size: 0.125)
      grp = resolve(board_ref)
      # For now, use SketchUp's native edge softening as a visual approximation.
      # Full geometric chamfer requires complex edge detection.
      # A practical approach: add the chamfer attribute and let the user
      # apply it visually, or use the trim router chamfer bit info for the build.
      grp.set_attribute("WW", "chamfer", size)
      grp.set_attribute("WW", "chamfer_edges", edges.to_s)
      grp
    end

    # Roundover / bullnose on an edge.
    # Uses segmented arc approximation.
    def roundover(board_ref, edge: :front, radius: 0.5, both_faces: false)
      grp = resolve(board_ref)
      grp.set_attribute("WW", "roundover_edge", edge.to_s)
      grp.set_attribute("WW", "roundover_radius", radius)
      grp.set_attribute("WW", "roundover_both", both_faces)
      grp
    end

    # Drill a half-moon finger pull on top edge of a board.
    # Uses a cylinder subtraction.
    def finger_pull(board_ref, edge: :top, diameter: 1.25, depth: 0.375)
      grp = resolve(board_ref)
      model = Sketchup.active_model
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]

      radius = diameter / 2.0
      cx = blen / 2.0  # center of board length

      # Create a cylinder cutter centered on the top edge
      cutter = model.active_entities.add_group
      segments = 24
      circle_pts = []
      segments.times do |i|
        angle = Math::PI * 2 * i / segments
        x = cx + radius * Math.cos(angle)
        z = bthk + radius * Math.sin(angle) - depth
        circle_pts << Geom::Point3d.new(x, 0, z)
      end
      circle_face = cutter.entities.add_face(circle_pts)
      circle_face.pushpull(bwid) if circle_face

      cutter.transform!(grp.transformation)
      subtract_and_track(board_ref, grp, cutter)
    end

    # ─── HARDWARE ────────────────────────────────────────────────

    # Drill a bolt hole with optional counterbore.
    # face: which face to drill from
    # at: [x, y] position on that face
    # hole: through-hole diameter
    # cbore: counterbore diameter (nil to skip)
    # cbore_depth: counterbore depth
    # depth: hole depth (nil = through)
    def bolt_hole(board_ref, face: :front, at:, hole:, cbore: nil, cbore_depth: nil, depth: nil)
      grp = resolve(board_ref)
      model = Sketchup.active_model
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]

      px, pz = at
      segments = 16

      # Helper: drill one cylinder and subtract
      do_drill = lambda { |cx, cy, cz, r, len, ax|
        cutter = make_cylinder(model, cx, cy, cz, r, len, ax, segments)
        cutter.transform!(grp.transformation)
        grp = subtract_and_track(board_ref, grp, cutter)
      }

      case face
      when :front, :outer
        hd = depth || bwid
        do_drill.call(px, 0, pz, cbore / 2.0, cbore_depth, :y) if cbore && cbore_depth
        do_drill.call(px, 0, pz, hole / 2.0, hd, :y)
      when :back
        hd = depth || bwid
        do_drill.call(px, bwid - cbore_depth, pz, cbore / 2.0, cbore_depth, :y) if cbore && cbore_depth
        do_drill.call(px, bwid - hd, pz, hole / 2.0, hd, :y)
      when :top
        hd = depth || bthk
        do_drill.call(px, pz, bthk - cbore_depth, cbore / 2.0, cbore_depth, :z) if cbore && cbore_depth
        do_drill.call(px, pz, bthk - hd, hole / 2.0, hd, :z)
      when :left
        hd = depth || blen
        do_drill.call(0, px, pz, cbore / 2.0, cbore_depth, :x) if cbore && cbore_depth
        do_drill.call(0, px, pz, hole / 2.0, hd, :x)
      when :right
        hd = depth || blen
        do_drill.call(blen - cbore_depth, px, pz, cbore / 2.0, cbore_depth, :x) if cbore && cbore_depth
        do_drill.call(blen - hd, px, pz, hole / 2.0, hd, :x)
      end
      grp
    end

    # Drill a pilot hole.
    def pilot_hole(board_ref, face: :top, at:, dia:, depth:)
      bolt_hole(board_ref, face: face, at: at, hole: dia, depth: depth)
    end

    # Drill barrel nut hole: end-grain hole + cross-hole.
    def barrel_nut_hole(board_ref, face: :right, at:, hole:, depth:, cross_hole:, cross_at:)
      grp = resolve(board_ref)
      model = Sketchup.active_model
      dims = board_dims(grp)
      blen, bwid, bthk = dims[:length], dims[:width], dims[:thickness]
      segments = 16
      py, pz = at

      # End-grain hole
      if face == :right
        cutter = make_cylinder(model, blen - depth, py, pz, hole / 2.0, depth, :x, segments)
      else
        cutter = make_cylinder(model, 0, py, pz, hole / 2.0, depth, :x, segments)
      end
      cutter.transform!(grp.transformation)
      grp = subtract_and_track(board_ref, grp, cutter)

      # Cross-hole
      cross_x = face == :right ? blen - cross_at : cross_at
      cutter2 = make_cylinder(model, cross_x, py, 0, cross_hole / 2.0, bthk, :z, segments)
      cutter2.transform!(grp.transformation)
      subtract_and_track(board_ref, grp, cutter2)
    end

    # ─── QUERY & EXPORT ──────────────────────────────────────────

    # Generate a cut list from all WW boards in a group (or entire model).
    def cut_list(group = nil)
      entities = if group
                   group.is_a?(Sketchup::Group) ? group.entities : [group]
                 else
                   Sketchup.active_model.active_entities
                 end

      boards = []
      collect_boards(entities, boards)

      # Group by name for quantities
      by_name = {}
      boards.each do |b|
        key = b[:name]
        if by_name[key]
          by_name[key][:qty] += 1
        else
          by_name[key] = b.merge(qty: 1)
        end
      end

      by_name.values.sort_by { |b| b[:name] }
    end

    # Calculate total board feet.
    def board_feet(group = nil)
      list = cut_list(group)
      total = 0.0
      list.each do |item|
        # Board feet = (T × W × L) / 144 where all in inches
        bf = (item[:thickness] * item[:width] * item[:length]) / 144.0
        total += bf * item[:qty]
      end
      total.round(2)
    end

    # Check which groups are solid (manifold).
    def check_solids(group = nil)
      entities = if group
                   group.is_a?(Sketchup::Group) ? group.entities : [group]
                 else
                   Sketchup.active_model.active_entities
                 end

      results = []
      entities.each do |ent|
        next unless ent.is_a?(Sketchup::Group) || ent.is_a?(Sketchup::ComponentInstance)
        name = ent.name.empty? ? "Unnamed (#{ent.entityID})" : ent.name
        is_solid = ent.manifold?
        results << { name: name, id: ent.entityID, solid: is_solid }
      end
      results
    end

    # List all tracked boards.
    def list_boards
      @boards.map { |name, grp|
        if grp.valid?
          { name: name, id: grp.entityID, valid: true }
        else
          { name: name, id: nil, valid: false }
        end
      }
    end

    # Clear the board tracking cache.
    def reset!
      @boards.clear
    end

    private

    # Resolve a board reference (name string or group entity)
    def resolve(ref)
      if ref.is_a?(String)
        grp = @boards[ref]
        raise "Board '#{ref}' not found. Known boards: #{@boards.keys.join(', ')}" unless grp
        raise "Board '#{ref}' is no longer valid (was it deleted or replaced?)" unless grp.valid?
        grp
      else
        ref
      end
    end

    # Subtract cutter from board, preserving WW attributes and tracking.
    # Returns the new group (or nil on failure).
    def subtract_and_track(board_ref, grp, cutter)
      attrs = cache_attrs(grp)
      result = grp.subtract(cutter)
      update_tracking(board_ref, result, attrs) if result
      result || grp  # return original if subtract failed
    end

    # Cache WW attributes from a group BEFORE a subtract operation
    # (because subtract erases the original group).
    def cache_attrs(grp)
      return {} unless grp && grp.valid?
      dict = grp.attribute_dictionary("WW")
      return {} unless dict
      attrs = {}
      dict.each { |k, v| attrs[k] = v }
      attrs
    rescue
      {}
    end

    # Update tracking when a board is replaced by a boolean operation.
    # cached_attrs: attributes saved before the subtract.
    def update_tracking(ref, new_group, cached_attrs = nil)
      return unless new_group && new_group.valid?

      # Apply cached attributes to the new group
      if cached_attrs && !cached_attrs.empty?
        cached_attrs.each { |k, v| new_group.set_attribute("WW", k, v) }
      end

      if ref.is_a?(String)
        @boards[ref] = new_group
        new_group.name = ref if new_group.name.nil? || new_group.name.empty?
      else
        @boards.each do |name, grp|
          if grp == ref || !grp.valid?
            @boards[name] = new_group
            new_group.name = name if new_group.name.nil? || new_group.name.empty?
            break
          end
        end
      end
    end

    # Get board dimensions from attributes or bounds
    def board_dims(grp)
      length = grp.get_attribute("WW", "length")
      width = grp.get_attribute("WW", "width")
      thickness = grp.get_attribute("WW", "thickness")

      if length && width && thickness
        { length: length.to_f, width: width.to_f, thickness: thickness.to_f }
      else
        # Fall back to bounding box (in local coordinates)
        bb = grp.local_bounds
        { length: bb.width, width: bb.height, thickness: bb.depth }
      end
    end

    # Generate 4 corner points for a centered rectangle
    def rect_pts(cx, cz, w, h, &block)
      [
        block.call(cx - w / 2.0, cz - h / 2.0),
        block.call(cx + w / 2.0, cz - h / 2.0),
        block.call(cx + w / 2.0, cz + h / 2.0),
        block.call(cx - w / 2.0, cz + h / 2.0),
      ]
    end

    # Create a solid box inside a group's entities
    def make_box(entities, x, y, z, w, d, h)
      return if w <= 0 || d <= 0 || h <= 0
      pts = [
        Geom::Point3d.new(x, y, z),
        Geom::Point3d.new(x + w, y, z),
        Geom::Point3d.new(x + w, y + d, z),
        Geom::Point3d.new(x, y + d, z),
      ]
      face = entities.add_face(pts)
      face.reverse! if face.normal.z < 0
      face.pushpull(h)
    end

    # Create a cylinder group for drilling operations
    def make_cylinder(model, cx, cy, cz, radius, length, axis, segments = 16)
      group = model.active_entities.add_group
      circle_pts = []

      segments.times do |i|
        angle = Math::PI * 2 * i / segments
        case axis
        when :x
          circle_pts << Geom::Point3d.new(cx, cy + radius * Math.cos(angle), cz + radius * Math.sin(angle))
        when :y
          circle_pts << Geom::Point3d.new(cx + radius * Math.cos(angle), cy, cz + radius * Math.sin(angle))
        when :z
          circle_pts << Geom::Point3d.new(cx + radius * Math.cos(angle), cy + radius * Math.sin(angle), cz)
        end
      end

      face = group.entities.add_face(circle_pts)
      if face
        case axis
        when :x then face.pushpull(length)
        when :y then face.pushpull(length)
        when :z then face.pushpull(length)
        end
      end
      group
    end

    # Apply a named or hex color material
    def apply_material(group, material_name)
      model = Sketchup.active_model
      mat = model.materials[material_name] || model.materials.add(material_name)

      if MATERIALS[material_name]
        r, g, b = MATERIALS[material_name]
        mat.color = Sketchup::Color.new(r, g, b)
      elsif material_name =~ /^#([0-9a-fA-F]{6})$/
        hex = $1
        mat.color = Sketchup::Color.new(hex[0..1].to_i(16), hex[2..3].to_i(16), hex[4..5].to_i(16))
      end

      # Apply to all faces in the group
      group.entities.grep(Sketchup::Face).each { |f| f.material = mat }
      group.material = mat
    end

    # Recursively collect WW board info from entities
    def collect_boards(entities, results)
      entities.each do |ent|
        if ent.is_a?(Sketchup::Group) || ent.is_a?(Sketchup::ComponentInstance)
          if ent.get_attribute("WW", "type") == "board"
            results << {
              name: ent.get_attribute("WW", "name") || ent.name,
              nominal: ent.get_attribute("WW", "nominal"),
              material: ent.get_attribute("WW", "material"),
              length: ent.get_attribute("WW", "length").to_f,
              width: ent.get_attribute("WW", "width").to_f,
              thickness: ent.get_attribute("WW", "thickness").to_f,
            }
          end
          # Recurse into sub-groups
          sub = ent.is_a?(Sketchup::Group) ? ent.entities : ent.definition.entities
          collect_boards(sub, results)
        end
      end
    end
  end
end
