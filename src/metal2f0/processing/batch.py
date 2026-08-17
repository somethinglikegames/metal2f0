"""Batch discovery and processing of materials."""

from dataclasses import dataclass
from pathlib import Path

from metal2f0.processing.processor import process


@dataclass(frozen=True)
class MaterialPair:
    """BaseColor and Metal files belonging to one material."""

    key: str
    base_color_path: Path | None
    metal_path: Path | None


@dataclass(frozen=True)
class OutputPaths:
    diffuse: Path
    f0: Path


@dataclass(frozen=True)
class BatchSkip:
    material: MaterialPair
    reason: str


@dataclass(frozen=True)
class BatchFailure:
    material: MaterialPair
    error: str


@dataclass(frozen=True)
class BatchResult:
    processed: list[MaterialPair]
    skipped: list[BatchSkip]
    failed: list[BatchFailure]


def process_batch(
    directory: Path,
    base_color_pattern: str,
    metal_pattern: str,
    metal_channel: int,
    specularity: float,
    diffuse_postfix: str,
    f0_postfix: str,
    *,
    overwrite: bool = False,
) -> BatchResult:
    """Find and process all matching materials in a directory."""

    materials = find_materials(
        directory,
        base_color_pattern,
        metal_pattern,
    )

    processed: list[MaterialPair] = []
    skipped: list[BatchSkip] = []
    failed: list[BatchFailure] = []

    for material in materials:
        if (
            material.base_color_path is None
            or material.metal_path is None
        ):
            missing = []

            if material.base_color_path is None:
                missing.append("BaseColor")

            if material.metal_path is None:
                missing.append("Metal")

            skipped.append(BatchSkip(material, "Missing " + " and ".join(missing)))
            continue

        output_paths = build_output_paths(
            material,
            diffuse_postfix,
            f0_postfix,
        )

        if not overwrite:
            existing_outputs = []

            if output_paths.diffuse.exists():
                existing_outputs.append(output_paths.diffuse.name)

            if output_paths.f0.exists():
                existing_outputs.append(output_paths.f0.name)

            if existing_outputs:
                skipped.append(BatchSkip(material, "Output file(s) already exist: " + ", ".join(existing_outputs)))
                continue

        try:
            process(
                base_color_path=material.base_color_path,
                metal_path=material.metal_path,
                metal_channel=metal_channel,
                diffuse_path=output_paths.diffuse,
                f0_path=output_paths.f0,
                specularity=specularity,
            )
        except Exception as exc:
            failed.append(BatchFailure(material, str(exc)))
            continue

        processed.append(material)

    return BatchResult(
        processed=processed,
        skipped=skipped,
        failed=failed,
    )


def find_materials(
    base_folder: Path,
    base_color_pattern: str,
    metal_pattern: str,
) -> list[MaterialPair]:
    """Find BaseColor/Metal pairs in a folder.

    Patterns must consist of a leading '*' followed by a
    non-empty postfix. Matching is case-sensitive.
    """

    base_folder = Path(base_folder)

    if not base_folder.exists():
        raise FileNotFoundError(f"Base folder does not exist: '{base_folder}'")

    if not base_folder.is_dir():
        raise NotADirectoryError(f"Base folder is not a directory: '{base_folder}'")

    base_color_postfix = _validate_pattern(base_color_pattern, "BaseColor")
    metal_postfix = _validate_pattern(metal_pattern, "Metal")

    materials: dict[str, MaterialPair] = {}

    for path in base_folder.iterdir():
        if not path.is_file():
            continue

        filename = path.name

        if filename.endswith(base_color_postfix):
            key = filename[
                : -len(base_color_postfix)
            ]

            material = materials.get(key)

            if material is None:
                materials[key] = MaterialPair(
                    key=key,
                    base_color_path=path,
                    metal_path=None,
                )
            else:
                materials[key] = MaterialPair(
                    key=key,
                    base_color_path=path,
                    metal_path=material.metal_path,
                )

        elif filename.endswith(metal_postfix):
            key = filename[
                : -len(metal_postfix)
            ]

            material = materials.get(key)

            if material is None:
                materials[key] = MaterialPair(
                    key=key,
                    base_color_path=None,
                    metal_path=path,
                )
            else:
                materials[key] = MaterialPair(
                    key=key,
                    base_color_path=material.base_color_path,
                    metal_path=path,
                )

    return [
        materials[key]
        for key in sorted(materials)
    ]


def _validate_pattern(
    pattern: str,
    name: str,
) -> str:
    if not pattern:
        raise ValueError(f"{name} pattern must not be empty")

    if not pattern.startswith("*"):
        raise ValueError(f"{name} pattern must start with '*'")

    if pattern.count("*") != 1:
        raise ValueError(f"{name} pattern must contain exactly one '*'")

    if "/" in pattern or "\\" in pattern:
        raise ValueError(f"{name} pattern must not contain a path separator")

    postfix = pattern[1:]

    if not postfix:
        raise ValueError(f"{name} pattern must have a non-empty postfix")

    return postfix


def build_output_paths(
    material: MaterialPair,
    diffuse_postfix: str,
    f0_postfix: str,
) -> OutputPaths:
    _validate_output_postfix(
        diffuse_postfix,
    )
    _validate_output_postfix(
        f0_postfix,
    )

    if diffuse_postfix == f0_postfix:
        raise ValueError("Diffuse and F0 postfixes must be different")

    if material.base_color_path is None:
        raise ValueError(f"Material '{material.key}' has no BaseColor file")

    folder = material.base_color_path.parent

    return OutputPaths(
        diffuse=folder / f"{material.key}{diffuse_postfix}",
        f0=folder / f"{material.key}{f0_postfix}",
    )


def _validate_output_postfix(
    postfix: str,
) -> None:
    if not postfix:
        raise ValueError("Output postfix must not be empty")

    if "*" in postfix:
        raise ValueError("Output postfix must not contain '*'")