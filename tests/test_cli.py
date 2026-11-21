import os

from handover_relay_decay.cli import main


def test_cli_census(capsys):
    assert main(["census", "--patients", "10"]) == 0
    out = capsys.readouterr().out
    assert "Patients: 10" in out
    assert "critical" in out


def test_cli_demo(capsys):
    assert main(["demo", "--policy", "sbar", "--patient", "0"]) == 0
    out = capsys.readouterr().out
    assert "Policy: sbar" in out
    assert "After relay 8" in out


def test_cli_evaluate_writes_results(capsys, tmp_path):
    out_dir = str(tmp_path)
    code = main(["evaluate", "--patients", "20", "--out", out_dir])
    assert code == 0
    assert os.path.exists(os.path.join(out_dir, "evaluation.json"))
    text = capsys.readouterr().out
    assert "relay 4" in text


def test_cli_no_command_prints_help(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "handover" in out.lower()
