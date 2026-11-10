from office_skill.paths import repo_root
from office_skill.profiles import list_domains, load_profile, resolve_domain

EXPECTED = {
    "academic",
    "brand",
    "consulting",
    "education",
    "finance",
    "government",
    "legal",
    "product",
}


def test_all_profiles_load():
    assert set(list_domains()) == EXPECTED
    root = repo_root() / "profiles"
    for domain in EXPECTED:
        profile = load_profile(domain)
        assert profile["id"] == domain
        assert (root / f"{domain}.md").is_file()
        assert profile["labels"]["zh"]["illustrative"]
        assert profile["labels"]["en"]["illustrative"]


def test_aliases():
    assert resolve_domain("marketing") == "brand"
    assert resolve_domain("公文") == "government"
    assert load_profile("tech")["id"] == "product"
