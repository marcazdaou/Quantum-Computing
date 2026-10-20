"""Every notebook must run from top to bottom without errors on the pinned Qiskit version.

These are slow (notebook 08 runs thousands of BB84 simulations), so they are marked
`notebooks` and can be skipped locally with:  pytest -m "not notebooks"
"""
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted(ROOT.glob("[0-9][0-9]_*.ipynb"))


@pytest.mark.notebooks
@pytest.mark.parametrize("path", NOTEBOOKS, ids=[p.stem for p in NOTEBOOKS])
def test_notebook_runs_without_errors(path):
    nb = nbformat.read(path, as_version=4)
    NotebookClient(nb, timeout=1200, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
