from pathlib import Path
from unittest.mock import patch

import pytest

from metal2f0.processing.batch import (
    BatchFailure,
    BatchResult,
    BatchSkip,
    MaterialPair,
    build_output_paths,
    find_materials,
    process_batch,
)


# ============================================================================
# Complete materials
# ============================================================================


def test_finds_single_complete_material(tmp_path: Path):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"

    base_color.touch()
    metal.touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1

    material = result[0]

    assert material.key == "Material_A"
    assert material.base_color_path == base_color
    assert material.metal_path == metal


def test_finds_multiple_complete_materials(tmp_path: Path):
    files = [
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "Material_B_bc.png",
        "Material_B_ORM.png",
        "Material_C_bc.png",
        "Material_C_ORM.png",
    ]

    for filename in files:
        (tmp_path / filename).touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert [material.key for material in result] == [
        "Material_A",
        "Material_B",
        "Material_C",
    ]


def test_result_is_sorted_by_key(tmp_path: Path):
    files = [
        "Material_C_bc.png",
        "Material_C_ORM.png",
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "Material_B_bc.png",
        "Material_B_ORM.png",
    ]

    for filename in files:
        (tmp_path / filename).touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert [material.key for material in result] == [
        "Material_A",
        "Material_B",
        "Material_C",
    ]


# ============================================================================
# Incomplete materials
# ============================================================================


def test_reports_missing_metal(tmp_path: Path):
    base_color = tmp_path / "Material_A_bc.png"
    base_color.touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1

    material = result[0]

    assert material.key == "Material_A"
    assert material.base_color_path == base_color
    assert material.metal_path is None


def test_reports_missing_base_color(tmp_path: Path):
    metal = tmp_path / "Material_A_ORM.png"
    metal.touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1

    material = result[0]

    assert material.key == "Material_A"
    assert material.base_color_path is None
    assert material.metal_path == metal


def test_ignores_unrelated_files(tmp_path: Path):
    files = [
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "readme.txt",
        "Material_B.jpg",
        "something.png",
    ]

    for filename in files:
        (tmp_path / filename).touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1
    assert result[0].key == "Material_A"


# ============================================================================
# Pattern semantics
# ============================================================================


def test_pattern_must_start_with_wildcard(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="must start with '\\*'",
    ):
        find_materials(
            tmp_path,
            "Material_*_bc.png",
            "*_ORM.png",
        )


def test_pattern_must_contain_exactly_one_wildcard(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="exactly one '\\*'",
    ):
        find_materials(
            tmp_path,
            "*_foo_*_bc.png",
            "*_ORM.png",
        )


def test_pattern_without_wildcard_is_rejected(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="must start with '\\*'",
    ):
        find_materials(
            tmp_path,
            "_bc.png",
            "*_ORM.png",
        )


def test_pattern_cannot_contain_forward_slash(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="path separator",
    ):
        find_materials(
            tmp_path,
            "*/_bc.png",
            "*_ORM.png",
        )


def test_pattern_cannot_contain_backslash(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="path separator",
    ):
        find_materials(
            tmp_path,
            r"*\_bc.png",
            "*_ORM.png",
        )


def test_pattern_cannot_have_empty_postfix(tmp_path: Path):
    with pytest.raises(
        ValueError,
        match="postfix",
    ):
        find_materials(
            tmp_path,
            "*",
            "*_ORM.png",
        )


def test_empty_base_color_pattern_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        find_materials(
            tmp_path,
            "",
            "*_ORM.png",
        )


def test_empty_metal_pattern_is_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        find_materials(
            tmp_path,
            "*_bc.png",
            "",
        )


# ============================================================================
# Case sensitivity
# ============================================================================


def test_matching_is_case_sensitive(tmp_path: Path):
    files = [
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "Material_B_BC.png",
        "Material_B_orm.png",
    ]

    for filename in files:
        (tmp_path / filename).touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1

    material = result[0]

    assert material.key == "Material_A"
    assert material.base_color_path == (
        tmp_path / "Material_A_bc.png"
    )
    assert material.metal_path == (
        tmp_path / "Material_A_ORM.png"
    )


def test_wrong_case_suffix_is_ignored(tmp_path: Path):
    (tmp_path / "Material_A_BC.png").touch()
    (tmp_path / "Material_A_orm.png").touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert result == []


# ============================================================================
# Prefix / postfix behavior
# ============================================================================


def test_key_is_filename_without_postfix(tmp_path: Path):
    base_color = tmp_path / "Environment_Wall_01_bc.png"
    metal = tmp_path / "Environment_Wall_01_ORM.png"

    base_color.touch()
    metal.touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1
    assert result[0].key == "Environment_Wall_01"


def test_postfix_is_removed_only_from_end(tmp_path: Path):
    base_color = tmp_path / "bc_Material_bc.png"
    metal = tmp_path / "bc_Material_ORM.png"

    base_color.touch()
    metal.touch()

    result = find_materials(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
    )

    assert len(result) == 1
    assert result[0].key == "bc_Material"


# ============================================================================
# Filesystem validation
# ============================================================================


def test_rejects_missing_base_folder(tmp_path: Path):
    missing_folder = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        find_materials(
            missing_folder,
            "*_bc.png",
            "*_ORM.png",
        )


def test_rejects_file_as_base_folder(tmp_path: Path):
    file = tmp_path / "not-a-folder.txt"
    file.touch()

    with pytest.raises(NotADirectoryError):
        find_materials(
            file,
            "*_bc.png",
            "*_ORM.png",
        )


# ============================================================================
# Output paths
# ============================================================================


def test_builds_default_output_paths(tmp_path: Path):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    result = build_output_paths(
        material,
        "_diffuse.png",
        "_f0.png",
    )

    assert result.diffuse == (
        tmp_path / "WoodFloor_diffuse.png"
    )
    assert result.f0 == (
        tmp_path / "WoodFloor_f0.png"
    )


def test_builds_custom_output_paths(tmp_path: Path):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    result = build_output_paths(
        material,
        "_albedo.png",
        "_specular.png",
    )

    assert result.diffuse == (
        tmp_path / "WoodFloor_albedo.png"
    )
    assert result.f0 == (
        tmp_path / "WoodFloor_specular.png"
    )


def test_output_paths_support_material_names_with_underscores(
    tmp_path: Path,
):
    material = MaterialPair(
        key="Environment_Wall_01",
        base_color_path=(
            tmp_path / "Environment_Wall_01_bc.png"
        ),
        metal_path=(
            tmp_path / "Environment_Wall_01_ORM.png"
        ),
    )

    result = build_output_paths(
        material,
        "_diffuse.png",
        "_f0.png",
    )

    assert result.diffuse == (
        tmp_path / "Environment_Wall_01_diffuse.png"
    )
    assert result.f0 == (
        tmp_path / "Environment_Wall_01_f0.png"
    )


def test_output_postfix_must_not_contain_wildcard(
    tmp_path: Path,
):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    with pytest.raises(
        ValueError,
        match="must not contain '\\*'",
    ):
        build_output_paths(
            material,
            "*_diffuse.png",
            "_f0.png",
        )


def test_empty_diffuse_postfix_is_rejected(tmp_path: Path):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    with pytest.raises(
        ValueError,
        match="postfix must not be empty",
    ):
        build_output_paths(
            material,
            "",
            "_f0.png",
        )


def test_empty_f0_postfix_is_rejected(tmp_path: Path):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    with pytest.raises(
        ValueError,
        match="postfix must not be empty",
    ):
        build_output_paths(
            material,
            "_diffuse.png",
            "",
        )


def test_output_postfixes_must_be_different(
    tmp_path: Path,
):
    material = MaterialPair(
        key="WoodFloor",
        base_color_path=tmp_path / "WoodFloor_bc.png",
        metal_path=tmp_path / "WoodFloor_ORM.png",
    )

    with pytest.raises(
        ValueError,
        match="must be different",
    ):
        build_output_paths(
            material,
            "_result.png",
            "_result.png",
        )



# ============================================================================
# Batch processing
# ============================================================================


def test_process_batch_processes_complete_materials(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"

    base_color.touch()
    metal.touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
        )

    assert len(result.processed) == 1
    assert result.processed[0].key == "Material_A"

    assert result.skipped == []
    assert result.failed == []

    process.assert_called_once_with(
        base_color_path=base_color,
        metal_path=metal,
        metal_channel=1,
        specularity=0.1,
        diffuse_path=tmp_path / "Material_A_diffuse.png",
        f0_path=tmp_path / "Material_A_f0.png",
    )


def test_process_batch_processes_multiple_materials(
    tmp_path: Path,
):
    for filename in (
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "Material_B_bc.png",
        "Material_B_ORM.png",
    ):
        (tmp_path / filename).touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
        )

    assert [material.key for material in result.processed] == [
        "Material_A",
        "Material_B",
    ]

    assert result.skipped == []
    assert result.failed == []

    assert process.call_count == 2


def test_process_batch_skips_missing_metal(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    base_color.touch()

    result = process_batch(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
        1,
        0.1,
        "_diffuse.png",
        "_f0.png",
    )

    assert result.processed == []
    assert result.failed == []

    assert len(result.skipped) == 1
    assert result.skipped[0].material.key == "Material_A"
    assert "Metal" in result.skipped[0].reason


def test_process_batch_skips_missing_base_color(
    tmp_path: Path,
):
    metal = tmp_path / "Material_A_ORM.png"
    metal.touch()

    result = process_batch(
        tmp_path,
        "*_bc.png",
        "*_ORM.png",
        1,
        0.1,
        "_diffuse.png",
        "_f0.png",
    )

    assert result.processed == []
    assert result.failed == []

    assert len(result.skipped) == 1
    assert result.skipped[0].material.key == "Material_A"
    assert "BaseColor" in result.skipped[0].reason


def test_process_batch_skips_existing_outputs(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"
    diffuse = tmp_path / "Material_A_diffuse.png"
    f0 = tmp_path / "Material_A_f0.png"

    base_color.touch()
    metal.touch()
    diffuse.touch()
    f0.touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
        )

    assert result.processed == []
    assert result.failed == []

    assert len(result.skipped) == 1
    assert result.skipped[0].material.key == "Material_A"
    assert "exist" in result.skipped[0].reason.lower()

    process.assert_not_called()


def test_process_batch_overwrites_existing_outputs(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"
    diffuse = tmp_path / "Material_A_diffuse.png"
    f0 = tmp_path / "Material_A_f0.png"

    base_color.touch()
    metal.touch()
    diffuse.touch()
    f0.touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
            overwrite=True,
        )

    assert len(result.processed) == 1
    assert result.processed[0].key == "Material_A"

    assert result.skipped == []
    assert result.failed == []

    process.assert_called_once_with(
        base_color_path=base_color,
        metal_path=metal,
        metal_channel=1,
        specularity=0.1,
        diffuse_path=diffuse,
        f0_path=f0,
    )


def test_process_batch_skips_if_only_one_output_exists(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"
    diffuse = tmp_path / "Material_A_diffuse.png"

    base_color.touch()
    metal.touch()
    diffuse.touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
        )

    assert result.processed == []
    assert result.failed == []

    assert len(result.skipped) == 1
    assert result.skipped[0].material.key == "Material_A"

    process.assert_not_called()


def test_process_batch_continues_after_processing_error(
    tmp_path: Path,
):
    for filename in (
        "Material_A_bc.png",
        "Material_A_ORM.png",
        "Material_B_bc.png",
        "Material_B_ORM.png",
    ):
        (tmp_path / filename).touch()

    def process_side_effect(
        base_color_path,
        metal_path,
        metal_channel,
        specularity,
        diffuse_path,
        f0_path,
    ):
        if "Material_A" in base_color_path.name:
            raise RuntimeError("Test processing error")

    with patch(
        "metal2f0.processing.batch.process",
        side_effect=process_side_effect,
    ):
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_diffuse.png",
            "_f0.png",
        )

    print(result)
    assert [material.key for material in result.processed] == ["Material_B"]

    assert len(result.failed) == 1
    assert result.failed[0].material.key == "Material_A"
    assert "Test processing error" in result.failed[0].error

    assert result.skipped == []


def test_process_batch_uses_custom_output_postfixes(
    tmp_path: Path,
):
    base_color = tmp_path / "Material_A_bc.png"
    metal = tmp_path / "Material_A_ORM.png"

    base_color.touch()
    metal.touch()

    with patch(
        "metal2f0.processing.batch.process"
    ) as process:
        result = process_batch(
            tmp_path,
            "*_bc.png",
            "*_ORM.png",
            1,
            0.1,
            "_albedo.png",
            "_specular.png",
        )

    assert len(result.processed) == 1

    process.assert_called_once_with(
        base_color_path=base_color,
        metal_path=metal,
        metal_channel=1,
        specularity=0.1,
        diffuse_path=tmp_path / "Material_A_albedo.png",
        f0_path=tmp_path / "Material_A_specular.png",
    )
