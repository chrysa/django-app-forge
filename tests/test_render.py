import pytest

from django_app_forge.render import RenderError, render


def test_render_replaces_placeholders() -> None:
    out = render(
        "class {{ app_class }}Config: name = {{ app_module }}",
        {"app_class": "Billing", "app_module": "apps.billing"},
    )
    assert out == "class BillingConfig: name = apps.billing"


def test_render_tolerates_whitespace() -> None:
    assert render("{{app_name}}/{{  app_name  }}", {"app_name": "x"}) == "x/x"


def test_render_no_placeholder_is_identity() -> None:
    assert render("plain text", {}) == "plain text"


def test_render_unknown_variable_raises() -> None:
    with pytest.raises(RenderError) as exc:
        render("{{ missing }}", {"app_name": "x"})
    assert "missing" in str(exc.value)
    assert "app_name" in str(exc.value)
