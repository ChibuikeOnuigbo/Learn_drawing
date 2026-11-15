"""Agent onboarding, packaged guidance, templates and honest readiness checks."""
import importlib.resources
import json
from pathlib import Path
import re
import sys

import pytest
from pydantic import ValidationError

from animation_mcp.skills_index import index, read_skill
from animation_mcp.scene import Scene
from animation_mcp.blender_scene import Scene3D
from animation_mcp.edit import Edit
from animation_mcp import doctor

ROOT = Path(__file__).resolve().parents[1]


def test_skill_catalog_and_frontmatter_are_consistent():
    catalog = index()
    names = [entry['name'] for entry in catalog['skills']]
    assert len(names) == len(set(names)) == 16
    assert catalog['entry_skill'] == 'animation-director'
    assert {p.name for p in (ROOT/'skills').iterdir() if p.is_dir() and p.name != '__pycache__'} == set(names)
    for entry in catalog['skills']:
        result = read_skill(entry['name'])
        text = result['content']
        assert text.startswith('---\n')
        assert f"name: {entry['name']}\n" in text
        assert 'description:' in text
        assert (ROOT/'skills'/entry['path']).read_text() == text


def test_unknown_skill_cannot_read_arbitrary_files():
    for name in ['../server', '../../README', '/etc/passwd', 'missing']:
        with pytest.raises(ValueError, match='Unknown skill'):
            read_skill(name)


def test_starter_templates_match_current_schemas():
    templates = importlib.resources.files('animation_mcp.templates')
    Scene.model_validate(json.loads(templates.joinpath('scene-2d.json').read_text()))
    Scene3D.model_validate(json.loads(templates.joinpath('scene-3d.json').read_text()))
    Edit.model_validate(json.loads(templates.joinpath('edit.json').read_text()))
    with pytest.raises(ValidationError):
        Scene3D.model_validate({"objects": [{"name": "X", "kind": "sphere", "lens": 50}]})


def test_active_markdown_links_resolve():
    files = [ROOT/name for name in ('README.md', 'AGENTS.md', 'CLAUDE.md', 'CHANGELOG.md')]
    for folder in ('docs', 'skills', 'templates', 'training'):
        files.extend((ROOT/folder).rglob('*.md'))
    files.extend(ROOT/path for path in ('scripts/README.md', 'references/README.md',
                                         'examples/README.md', 'projects/README.md',
                                         '.github/copilot-instructions.md'))
    for path in files:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if target.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            local = target.split('#')[0]
            assert (path.parent/local).exists(), f'{path.relative_to(ROOT)} -> {target}'


def test_missing_engines_are_reported_not_faked(tmp_path, monkeypatch):
    monkeypatch.setattr(doctor, 'resolve_command', lambda name: None)
    monkeypatch.delenv('ANIMATION_BLENDER', raising=False)
    report = doctor.run_checks(workspace=tmp_path)
    assert not report['ok'] and not report['ready']['2d'] and not report['ready']['3d']
    assert {'engine:ffmpeg', 'engine:ffprobe'} <= set(report['failures'])
    blender = next(c for c in report['checks'] if c['name'] == 'engine:blender')
    assert blender['status'] == 'warn'
    assert 'no downloads' in report['scope']


def test_invalid_blender_override_is_not_capability(tmp_path, monkeypatch):
    monkeypatch.setenv('ANIMATION_BLENDER', str(tmp_path/'missing-blender'))
    assert doctor.resolve_command('blender') is None
    report = doctor.run_checks(workspace=tmp_path)
    assert 'engine:blender' in report['failures']


def test_cli_doctor_smoke_is_real_and_machine_readable(tmp_path, monkeypatch, capsys):
    from animation_mcp.cli import main
    monkeypatch.setattr(sys, 'argv', ['animation-studio', 'doctor', '--smoke', '--json', '--workspace', str(tmp_path)])
    code = main()
    report = json.loads(capsys.readouterr().out)
    assert code == 0 and report['ok']
    proof = next(c for c in report['checks'] if c['name'] == 'smoke:2d')
    assert proof['status'] == 'pass' and 'decoded' in proof['detail']
    assert not list(tmp_path.iterdir())
