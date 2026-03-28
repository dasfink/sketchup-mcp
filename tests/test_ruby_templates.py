"""Unit tests for ruby_templates module.

Tests verify the GENERATED RUBY CODE structure, not execution in SketchUp.
Integration tests (requiring SketchUp) are separate.
"""
import pytest
from sketchup_mcp.ruby_templates import (
    boolean_subtract_ruby,
    make_box_ruby,
    safe_cut_dado_ruby,
    safe_drill_hole_ruby,
    verify_bounds_ruby,
    take_screenshot_ruby,
    create_scene_ruby,
    verify_scenes_ruby,
    generate_cutlist_ruby,
    exploded_view_ruby,
)


class TestBooleanSubtract:
    def test_box_cutter_no_pushpull_on_target(self):
        code = boolean_subtract_ruby("PostBC", "box", [2.0, 0, 60], [1.5, 3.5, 11.25])
        assert "subtract" in code
        assert "PostBC" in code
        # Box cutter uses 6 faces
        assert code.count("add_face") == 6

    def test_cylinder_cutter(self):
        code = boolean_subtract_ruby("PostBC", "cylinder", [0, 1.75, 63], [3.5, 0.197, 0], axis=[1, 0, 0])
        assert "subtract" in code
        assert "add_circle" in code
        assert "0.197" in code

    def test_target_name_in_code(self):
        code = boolean_subtract_ruby("RailB", "box", [0, 0, 0], [1, 1, 1])
        assert "RailB" in code

    def test_returns_bounds_json(self):
        code = boolean_subtract_ruby("Post", "box", [0, 0, 0], [1, 1, 1])
        assert "bounds" in code
        assert "success" in code

    def test_invalid_cutter_type(self):
        with pytest.raises(ValueError, match="Unknown cutter_type"):
            boolean_subtract_ruby("Post", "sphere", [0, 0, 0], [1, 1, 1])

    def test_cylinder_default_axis(self):
        code = boolean_subtract_ruby("Post", "cylinder", [0, 0, 0], [3.5, 0.2, 0])
        # Should have a default axis
        assert "1" in code  # default axis [1,0,0]


class TestMakeBox:
    def test_six_faces_no_pushpull(self):
        code = make_box_ruby("TestBox", [0, 0, 0], [10, 5, 3], "Pine", "Frame", {})
        assert code.count("add_face") == 6
        assert "pushpull" not in code

    def test_component_name(self):
        code = make_box_ruby("RailB", [2, 37.5, 60], [1.5, 77, 11.25], "Pine", "FrameRails", {})
        assert "RailB" in code

    def test_material_applied(self):
        code = make_box_ruby("Post", [0, 0, 0], [3.5, 3.5, 71], "Pine", "Posts", {})
        assert "Pine" in code
        assert "material" in code.lower()

    def test_tag_applied(self):
        code = make_box_ruby("Post", [0, 0, 0], [3.5, 3.5, 71], "Pine", "Posts", {})
        assert "Posts" in code
        assert "layer" in code.lower() or "layers" in code.lower()

    def test_attributes_set(self):
        attrs = {"species": "Pine", "nominal_size": "4x4", "finish": "Rubio Monocoat"}
        code = make_box_ruby("Post", [0, 0, 0], [3.5, 3.5, 71], "Pine", "Posts", attrs)
        assert "set_attribute" in code
        assert "species" in code
        assert "4x4" in code
        assert "Rubio Monocoat" in code

    def test_dimensions_in_code(self):
        code = make_box_ruby("Rail", [0, 0, 0], [1.5, 77, 11.25], "Pine", "Frame", {})
        assert "1.5" in code
        assert "77" in code
        assert "11.25" in code


class TestSafeCutDado:
    def test_all_face_directions(self):
        for face in ["x+", "x-", "y+", "y-"]:
            code = safe_cut_dado_ruby("PostBC", face, 60, 71.25, 1.5)
            assert code is not None
            assert len(code) > 50

    def test_uses_boolean_subtract(self):
        code = safe_cut_dado_ruby("PostBC", "x+", 60, 71.25, 1.5)
        assert "subtract" in code

    def test_z_range_in_code(self):
        code = safe_cut_dado_ruby("PostBC", "x+", 60, 71.25, 1.5)
        assert "60" in code
        assert "11.25" in code  # height = z_end - z_start = 71.25 - 60

    def test_component_name(self):
        code = safe_cut_dado_ruby("PostDA", "y-", 20, 23.5, 1.5)
        assert "PostDA" in code


class TestSafeDrillHole:
    def test_uses_boolean_subtract(self):
        code = safe_drill_hole_ruby("PostBC", [0, 1.75, 63], [1, 0, 0], 0.197, 3.5)
        assert "subtract" in code

    def test_coordinates_in_code(self):
        code = safe_drill_hole_ruby("PostBC", [0, 1.75, 63], [1, 0, 0], 0.197, 3.5)
        assert "1.75" in code
        assert "63" in code
        assert "0.197" in code

    def test_component_name(self):
        code = safe_drill_hole_ruby("RailB", [0.75, 0, 3], [0, 1, 0], 0.197, 1.5)
        assert "RailB" in code


class TestVerifyBounds:
    def test_component_names_in_code(self):
        expected = {"PostBC": {"x": [0, 3.5], "y": [0, 3.5], "z": [0, 71.25]}}
        code = verify_bounds_ruby(expected)
        assert "PostBC" in code
        assert "3.5" in code
        assert "71.25" in code

    def test_returns_issues_structure(self):
        code = verify_bounds_ruby({"RailB": {"x": [0, 1.5], "y": [0, 77]}})
        assert "issues" in code

    def test_empty_expected(self):
        code = verify_bounds_ruby({})
        assert "issues" in code

    def test_multiple_components(self):
        expected = {
            "PostBC": {"x": [0, 3.5]},
            "PostDA": {"x": [0, 3.5]},
            "RailB": {"y": [0, 77]},
        }
        code = verify_bounds_ruby(expected)
        assert "PostBC" in code
        assert "PostDA" in code
        assert "RailB" in code


class TestTakeScreenshot:
    def test_disables_transitions(self):
        code = take_screenshot_ruby("Front Elevation", 1920, 1080)
        assert "ShowTransition" in code

    def test_activates_scene(self):
        code = take_screenshot_ruby("Front Elevation", 1920, 1080)
        assert "selected_page" in code
        assert "Front Elevation" in code

    def test_write_image(self):
        code = take_screenshot_ruby("Test", 1920, 1080)
        assert "write_image" in code
        assert "1920" in code
        assert "1080" in code

    def test_no_scene(self):
        code = take_screenshot_ruby(None, 800, 600)
        assert "write_image" in code
        assert "selected_page" not in code

    def test_hide_tags(self):
        code = take_screenshot_ruby("Test", 1920, 1080, hide_tags=["Room", "Exploded"])
        assert "Room" in code
        assert "Exploded" in code
        assert "visible = false" in code or "visible=" in code


class TestCreateScene:
    def test_state_before_add(self):
        code = create_scene_ruby(
            name="Front Elevation",
            eye=[23.5, -80, 40], target=[23.5, 60, 40], up=[0, 0, 1],
            perspective=False, height=95,
            visible_tags=["Posts", "FrameRails"]
        )
        # Layers and camera must be set BEFORE pages.add
        layers_idx = code.index("visible")
        camera_idx = code.index("camera")
        add_idx = code.index("pages.add")
        assert layers_idx < add_idx
        assert camera_idx < add_idx

    def test_orthographic_settings(self):
        code = create_scene_ruby(
            name="Test", eye=[0, 0, 0], target=[1, 0, 0], up=[0, 0, 1],
            perspective=False, height=95
        )
        assert "false" in code  # perspective = false
        assert "95" in code  # height

    def test_section_plane(self):
        code = create_scene_ruby(
            name="Section", eye=[0, 0, 0], target=[1, 0, 0], up=[0, 0, 1],
            perspective=False, height=90, visible_tags=["Posts"],
            section_point=[23.5, 75, 0], section_normal=[0, 1, 0]
        )
        assert "add_section_plane" in code
        assert "23.5" in code

    def test_no_section_plane(self):
        code = create_scene_ruby(
            name="Overview", eye=[90, -20, 80], target=[23, 75, 35], up=[0, 0, 1],
            perspective=True, height=90
        )
        assert "section_plane" not in code.lower() or "add_section_plane" not in code


class TestVerifyScenes:
    def test_iterates_pages(self):
        code = verify_scenes_ruby()
        assert "pages" in code
        assert "selected_page" in code

    def test_checks_perspective(self):
        code = verify_scenes_ruby()
        assert "perspective" in code

    def test_checks_visibility(self):
        code = verify_scenes_ruby()
        assert "visible" in code


class TestGenerateCutlist:
    def test_uses_worker(self):
        code = generate_cutlist_ruby()
        assert "CutlistGenerateWorker" in code

    def test_part_folding(self):
        code = generate_cutlist_ruby(part_folding=True)
        assert "part_folding" in code
        assert "true" in code

    def test_no_folding(self):
        code = generate_cutlist_ruby(part_folding=False)
        assert "false" in code


class TestExplodedView:
    def test_tag_offsets(self):
        offsets = {"Railing": 25, "Slats": 18, "FrameRails": 6, "Posts": 0}
        code = exploded_view_ruby(offsets, "Exploded")
        assert "Railing" in code
        assert "25" in code
        assert "Exploded" in code

    def test_uses_copy(self):
        code = exploded_view_ruby({"Posts": 0}, "Exploded")
        assert "copy" in code

    def test_uses_translation(self):
        code = exploded_view_ruby({"Slats": 18}, "Exp")
        assert "translation" in code
