"""Transfer a report's active custom theme between enhanced Power BI projects."""

import argparse
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def report_folder(path):
    if path.suffix.lower() == ".pbip":
        reports = [item["report"]["path"] for item in read_json(path)["artifacts"] if "report" in item]
        if len(reports) != 1:
            raise ValueError("Pass the intended .Report folder for this project.")
        path = path.parent / reports[0]
    if not (path / "definition" / "report.json").is_file():
        raise ValueError("Expected an enhanced PBIR .pbip or .Report folder. For PBIX, use Desktop's theme menu.")
    return path.resolve()


def resource_path(folder, package, item):
    root = (folder / "StaticResources").resolve()
    path = (root / package["name"] / item["path"]).resolve()
    if not path.is_relative_to(root) or not root.is_relative_to(folder):
        raise ValueError("The resource points outside the report's StaticResources folder.")
    return path


def active_resource(folder, report):
    active = report["themeCollection"].get("customTheme")
    if not active:
        return None
    paths = [
        resource_path(folder, package, item)
        for package in report.get("resourcePackages", [])
        if package["type"] == active["type"]
        for item in package["items"]
        if item["type"] == "CustomTheme" and item["name"] == active["name"]
    ]
    if len(paths) != 1 or not paths[0].is_file():
        raise ValueError("The active custom theme does not resolve to one registered file. Export it from Desktop.")
    return paths[0]


def read_theme(path):
    data = path.read_bytes()
    theme = json.loads(data.decode("utf-8-sig"))
    if not isinstance(theme, dict) or not isinstance(theme.get("name"), str):
        raise ValueError(f"Expected a Power BI theme with a name in {path}.")
    return data, theme


@contextmanager
def staged_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as output:
        staged = Path(output.name)
    try:
        staged.write_bytes(data)
        yield staged
    finally:
        staged.unlink(missing_ok=True)


def write_new(path, data):
    """Publish a complete file without replacing another export or resource."""
    with staged_file(path, data) as staged:
        try:
            if os.name == "nt":
                staged.rename(path)  # Windows rename fails if the destination exists.
            else:
                os.link(staged, path)
        except FileExistsError:
            if path.read_bytes() != data:
                raise ValueError(f"{path} already contains different data. Choose a fresh output path.")


def extract(folder, report, output):
    if output.resolve().is_relative_to(folder) or output.suffix.lower() != ".json":
        raise ValueError("Choose a .json output outside the source report.")
    active = active_resource(folder, report)
    if active is None:
        raise ValueError("This report uses only a base theme. Export its current theme from Desktop and inspect local formatting.")
    data, theme = read_theme(active)
    write_new(output, data)
    print(f"Extracted {theme['name']} to {output}")


def apply_theme(folder, report, source):
    data, theme = read_theme(source)
    collection = report["themeCollection"]
    active = active_resource(folder, report)
    if active and read_theme(active)[1] == theme:
        print(f"{theme['name']} is already active.")
        return
    metadata = collection.get("customTheme") or collection.get("baseTheme")
    if not metadata or "reportVersionAtImport" not in metadata:
        raise ValueError("The target has no theme version metadata. Import the theme using Desktop.")

    filename = "Theme-" + hashlib.sha256(data).hexdigest()[:16] + ".json"
    packages = report.setdefault("resourcePackages", [])
    package = next((p for p in packages if p["name"] == "RegisteredResources"), None)
    if package is None:
        package = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
        packages.append(package)
    if package["type"] != "RegisteredResources":
        raise ValueError("Unexpected resource package type. Import the theme using Desktop.")
    item = {"name": filename, "path": filename, "type": "CustomTheme"}
    matches = [i for i in package["items"] if filename in (i["name"], i["path"])]
    if matches and matches != [item]:
        raise ValueError("The resource name is already registered to another item.")
    if not matches:
        package["items"].append(item)
    collection["customTheme"] = {
        "name": filename,
        "type": package["type"],
        "reportVersionAtImport": metadata["reportVersionAtImport"],
    }

    # Land the resource before atomically switching the active theme.
    write_new(resource_path(folder, package, item), data)
    definition = folder / "definition" / "report.json"
    encoded = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with staged_file(definition, encoded) as staged:
        staged.replace(definition)
    print(f"Applied {theme['name']} to {folder.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("extract", "apply"))
    parser.add_argument("project", type=Path, help="Source for extract or target for apply (.pbip or .Report folder)")
    parser.add_argument("theme", type=Path, help="Theme JSON output for extract or input for apply")
    args = parser.parse_args()
    try:
        folder = report_folder(args.project)
        report = read_json(folder / "definition" / "report.json")
        operation = extract if args.operation == "extract" else apply_theme
        operation(folder, report, args.theme)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Theme transfer failed: {exc}\n")


if __name__ == "__main__":
    main()
