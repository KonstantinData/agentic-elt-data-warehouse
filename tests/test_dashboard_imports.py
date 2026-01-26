import importlib


def test_dashboard_modules_import():
    modules = [
        "src.dashboard.app",
        "src.dashboard.pages.01_executive_overview",
        "src.dashboard.pages.02_explore",
        "src.dashboard.pages.03_run_diagnostics",
        "src.dashboard.pages.04_export",
    ]
    for module in modules:
        importlib.import_module(module)
