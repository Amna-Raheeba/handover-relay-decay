import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_reproduce_script_passes():
    script = os.path.join(ROOT, "scripts", "reproduce_results.py")
    proc = subprocess.run(
        [sys.executable, script], capture_output=True, text=True,
        cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout


def test_notebook_demo_runs():
    script = os.path.join(ROOT, "notebooks", "01_demo_run.py")
    proc = subprocess.run(
        [sys.executable, script], capture_output=True, text=True,
        cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "free_text" in proc.stdout


def test_notebook_evaluation_runs():
    script = os.path.join(ROOT, "notebooks", "02_evaluation_experiment.py")
    proc = subprocess.run(
        [sys.executable, script], capture_output=True, text=True,
        cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "checklist_pinning_readback" in proc.stdout


def test_example_runs():
    script = os.path.join(ROOT, "examples", "run_relay.py")
    proc = subprocess.run(
        [sys.executable, script], capture_output=True, text=True,
        cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "DEMO-001" in proc.stdout
