import copy
from pathlib import Path
import pytest
from run import validate_rate_migration


def fixture(tmp_path):
    previous = dict(code_sha256={"run.py":"old"}, config={"max_requests":12200,"government_tick":2},
        input_sha256={"roster":"same"}, mode="openai", dry_run=False, upstream_commit="same",
        upstream_url="same", numpy_version="same", total_steps=10)
    current = copy.deepcopy(previous)
    current["code_sha256"]={"run.py":"new"}
    current["config"].update(rate_limit_max_retries=6, rate_limit_wait_seconds=2)
    manifest = dict(parent_run=str(tmp_path.resolve()), old_code_sha256=previous["code_sha256"],
        new_code_sha256=current["code_sha256"],old_config=previous["config"], new_config=current["config"])
    return previous,current,manifest


def test_exact_migration(tmp_path):
    a,b,m=fixture(tmp_path)
    validate_rate_migration(a,b,tmp_path,m)


@pytest.mark.parametrize('field', ['input_sha256','mode','upstream_commit','total_steps','code_sha256'])
def test_reject_drift(tmp_path,field):
    a,b,m=fixture(tmp_path)
    b[field]='changed'
    with pytest.raises(ValueError): validate_rate_migration(a,b,tmp_path,m)


@pytest.mark.parametrize('field', ['max_requests','government_tick'])
def test_manifest_cannot_authorize_research_or_budget_change(tmp_path,field):
    a,b,m=fixture(tmp_path)
    b['config'][field]=99999
    with pytest.raises(ValueError): validate_rate_migration(a,b,tmp_path,m)


def test_wrong_parent(tmp_path):
    a,b,m=fixture(tmp_path)
    with pytest.raises(ValueError): validate_rate_migration(a,b,tmp_path/'other',m)
