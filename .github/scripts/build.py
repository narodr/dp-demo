# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "jinja2==3.1.3",
#     "fire==0.7.0",
#     "loguru==0.7.0"
# ]
# ///

import subprocess
from typing import List, Union
from pathlib import Path

import fire

from loguru import logger


def _export_html_wasm(notebook_path: Path, output_dir: Path, as_app: bool = False
                      ) -> bool:
    """Export a single marimo notebook to HTML/WebAssembly format.

    This function takes a marimo notebook (.py file) and exports it to HTML/WebAssembly
    format. If as_app is True, the notebook is exported in "run" mode with code hidden,
    suitable for applications. Otherwise, it's exported in "edit" mode, suitable 
    for interactive notebooks.

    Args:
        notebook_path (Path): Path to the marimo notebook (.py file) to export.
        output_dir (Path): Directory where the exported HTML file will be saved.
        as_app (bool, optional): Whether to export as an app (run mode) or notebook
        (edit mode).

    Returns:
        bool: True if export succeeded, False otherwise
    """

    output_path: Path = notebook_path.with_suffix(".html")
    cmd: List[str] = ["uvx", "marimo", "export", "html-wasm", "--sandbox"]

    if as_app:
        logger.info(f"Exporting {notebook_path} to {output_path} as app")
        cmd.extend(["--mode", "run", "--no-show-code"])
    else:
        logger.info(f"Exporting {notebook_path} to {output_path} as notebook")
        cmd.extend(["--mode", "edit"])

    try:
        # Create full output path and ensure directory exists
        output_file: Path = output_dir / notebook_path.with_suffix(".html")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Add notebook path and output file to command
        cmd.extend([str(notebook_path), "-o", str(output_file)])

        # Run marimo export command
        logger.debug(f"Running command: {cmd}")
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Successfully exported {notebook_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error exporting {notebook_path}:")
        logger.error(f"Command output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error exporting {notebook_path}: {e}")
        return False


def main(
    output_dir: Union[str, Path] = "_site"
) -> None:
    """Main function to export marimo notebooks.

    This function:
    1. Parses command line arguments
    2. Exports all marimo notebooks in the 'notebooks' and 'apps' directories
    3. Generates an index.html file that lists all the notebooks

    Command line arguments:
        --output-dir: Directory where the exported files will be saved.

    Returns:
        None
    """
    logger.info("Starting marimo build process")
    output_dir: Path = Path(output_dir)
    logger.info(f"Output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    notebooks_data = _export_html_wasm(Path("notebooks/notebook.py"), 
                                       output_dir, as_app=True)
    if not notebooks_data:
        logger.warning("No notebooks or apps found!")
        return
    logger.info(f"Build completed successfully. Output directory: {output_dir}")


if __name__ == '__main__':
    fire.Fire(main)