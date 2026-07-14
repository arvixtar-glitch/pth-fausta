from pathlib import Path

from app.core.paths import ProjectPaths


def test_project_paths_resolve_root() -> None:
    paths = ProjectPaths()

    assert paths.project_root == Path(__file__).resolve().parents[1]
    assert paths.src == paths.project_root / "src"
    assert paths.app == paths.src / "app"
    assert paths.core == paths.app / "core"
    assert paths.logs == paths.project_root / "logs"


def test_create_runtime_directories(tmp_path: Path) -> None:
    custom_root = tmp_path / "project"
    custom_root.mkdir()
    project_paths = ProjectPaths(project_root=custom_root)
    project_paths.create_runtime_directories()

    assert project_paths.logs.exists()
    assert project_paths.logs.is_dir()
    assert not (project_paths.project_root / "src").exists()


def test_validate_missing_required_directories(tmp_path: Path) -> None:
    custom_root = tmp_path / "project"
    custom_root.mkdir()
    project_paths = ProjectPaths(project_root=custom_root)

    (project_paths.src).mkdir(parents=True)
    (project_paths.app).mkdir(parents=True)
    (project_paths.core).mkdir(parents=True)
    (project_paths.database).mkdir()
    (project_paths.docs).mkdir()
    (project_paths.resources).mkdir()
    # Intentionally omit tests directory.

    try:
        project_paths.validate()
        assert False, "validate() should raise FileNotFoundError for missing directories"
    except FileNotFoundError as error:
        assert "tests" in str(error)
