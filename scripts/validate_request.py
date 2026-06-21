"""Validate figure inputs, mappings, and profile constraints before rendering."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import load_yaml, profile_path, read_table, resolve_request_path
from validate_profile import validate


REQUIRED = {"figure_id", "research_field", "profile", "layout", "data_paths", "analysis_script", "claim", "caption_takeaway", "figure", "output_dir"}
FIGURE_REQUIRED = {"type", "source", "x", "y", "xlabel", "ylabel"}


def validate_request(request_path: str | Path, profiles_dir: str | Path | None = None) -> list[str]:
    request = load_yaml(request_path)
    errors = [f"missing request key: {key}" for key in sorted(REQUIRED - set(request))]
    if errors:
        return errors
    if request["layout"] not in {"single", "double"}:
        errors.append("layout must be single or double")
    for value in request["data_paths"]:
        if not resolve_request_path(request_path, value).exists():
            errors.append(f"data path does not exist: {value}")
    analysis = resolve_request_path(request_path, request["analysis_script"])
    if not analysis.exists():
        errors.append(f"analysis script does not exist: {request['analysis_script']}")
    profile_file = profile_path(request["profile"], profiles_dir)
    if not profile_file.exists():
        errors.append(f"profile does not exist: {request['profile']}")
    else:
        errors.extend(validate(load_yaml(profile_file), require_current=profile_file.parent.name == "named"))
    figure = request["figure"]
    errors.extend(f"missing figure key: {key}" for key in sorted(FIGURE_REQUIRED - set(figure)))
    source = resolve_request_path(request_path, figure.get("source", ""))
    if source.exists():
        try:
            columns = set(read_table(source).columns)
            for key in ("x", "y", "group", "lower", "upper"):
                value = figure.get(key)
                if value and value not in columns:
                    errors.append(f"figure.{key} is not a column in {figure['source']}: {value}")
        except ValueError as exc:
            errors.append(str(exc))
    else:
        errors.append(f"figure source does not exist: {figure.get('source')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--profiles-dir")
    args = parser.parse_args()
    errors = validate_request(args.request, args.profiles_dir)
    if errors:
        print("Figure request validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Figure request is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
