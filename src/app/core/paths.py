from pathlib import Path


__all__ = ["ProjectPaths"]


class ProjectPaths:
    """Centralize project directory paths.

    Instances of this class compute absolute paths for the project root and
    the most important project directories.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize the project paths.

        Args:
            project_root: Optional override for the project root directory.
                If omitted, the root is resolved automatically from the
                location of this module.
        """
        self.project_root = (
            project_root.resolve() if project_root is not None else self._resolve_project_root()
        )
        self.src = self.project_root / "src"
        self.app = self.src / "app"
        self.core = self.app / "core"
        self.database = self.project_root / "database"
        self.docs = self.project_root / "docs"
        self.resources = self.project_root / "resources"
        self.tests = self.project_root / "tests"
        self.logs = self.project_root / "logs"

    def _resolve_project_root(self) -> Path:
        """Resolve the project root directory from this module location."""
        return Path(__file__).resolve().parents[3]

    def validate(self) -> None:
        """Validate that required project directories exist.

        Raises:
            FileNotFoundError: When at least one required directory is missing or
                is not a directory.
        """
        missing_directories = [
            directory
            for directory in self._required_directories()
            if not directory.is_dir()
        ]
        if missing_directories:
            missing = ", ".join(str(directory) for directory in missing_directories)
            raise FileNotFoundError(
                f"Missing required project directories: {missing}"
            )

    def create_runtime_directories(self) -> None:
        """Create missing runtime directories needed during execution."""
        for directory in self._runtime_directories():
            directory.mkdir(parents=True, exist_ok=True)

    def _required_directories(self) -> tuple[Path, ...]:
        """Return a tuple of directories that must exist for the project."""
        return (
            self.src,
            self.app,
            self.core,
            self.database,
            self.docs,
            self.resources,
            self.tests,
        )

    def _runtime_directories(self) -> tuple[Path, ...]:
        """Return a tuple of directories that are created at runtime.

        These directories are optional at source time and can be created when
        the application starts.
        """
        return (
            self.logs,
        )
