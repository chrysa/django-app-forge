import pytest

from django_app_forge.naming import derived_context, to_pascal, to_snake


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("billing", "billing"),
        ("Api-Gateway", "api_gateway"),
        ("my app", "my_app"),
        ("My_App", "my_app"),
    ],
)
def test_to_snake(raw: str, expected: str) -> None:
    assert to_snake(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("billing", "Billing"),
        ("my_app", "MyApp"),
        ("api-gateway", "ApiGateway"),
    ],
)
def test_to_pascal(raw: str, expected: str) -> None:
    assert to_pascal(raw) == expected


def test_derived_context_with_base_path() -> None:
    ctx = derived_context("Billing", "apps")
    assert ctx == {
        "app_name": "billing",
        "app_label": "billing",
        "app_class": "Billing",
        "app_module": "apps.billing",
    }


def test_derived_context_root_base_path() -> None:
    ctx = derived_context("catalog", ".")
    assert ctx["app_module"] == "catalog"
