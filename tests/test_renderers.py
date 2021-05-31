from jinja2 import Template
from pytest import fixture, mark, raises

from incipyt._internal.templates import RenderContext
from incipyt.system import Environment
from tests.utils import mock_stdin


class _Context:
    @fixture
    def env(self):
        env = Environment(auto_confirm=True)
        env["VARIABLE_NAME"] = "value"
        env["EMPTY_VARIABLE"] = ""
        return env

    @fixture
    def simple_ctx(self, env):
        return RenderContext(env)

    @fixture
    def no_error_ctx(self, env):
        return RenderContext(env, value_error=False)

    @fixture
    def populated_ctx(self, simple_ctx):
        simple_ctx.render_string("{VARIABLE_NAME}")
        return simple_ctx


class TestRenderContext(_Context):
    def test_contains(self, simple_ctx):
        assert "VARIABLE_NAME" in simple_ctx

    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_contains_undefined(self, ctx, monkeypatch, request):
        mock_stdin(monkeypatch, "value")
        ctx = request.getfixturevalue(ctx)
        assert "OTHER_NAME" in ctx
        assert ctx["OTHER_NAME"] == "value"

    def test_getitem_empty_simple(self, simple_ctx):
        with raises(ValueError):
            simple_ctx["EMPTY_VARIABLE"]

    def test_getitem_empty_no_error(self, no_error_ctx):
        assert no_error_ctx["EMPTY_VARIABLE"] == ""

    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_getitem_sanitized(self, ctx, request):
        ctx = request.getfixturevalue(ctx)
        ctx._sanitizer = lambda k, v: v.upper()
        assert ctx["VARIABLE_NAME"] == "VALUE"

    @mark.parametrize(
        "ctx, res",
        (
            ("simple_ctx", set()),
            ("no_error_ctx", set()),
            ("populated_ctx", {"VARIABLE_NAME"}),
        ),
    )
    def test_iteration(self, ctx, res, request):
        ctx = request.getfixturevalue(ctx)
        assert set(ctx) == res
        assert len(ctx) == len(res)

    @mark.parametrize(
        "ctx, keys, values",
        (
            ("simple_ctx", [], []),
            ("no_error_ctx", [], []),
            ("populated_ctx", ["VARIABLE_NAME"], ["value"]),
        ),
    )
    def test_key_values(self, ctx, keys, values, request):
        ctx = request.getfixturevalue(ctx)
        assert list(ctx.keys()) == keys
        assert list(ctx.values()) == values
        assert list(ctx.items()) == list(zip(keys, values))


class TestRenderString(_Context):
    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_interp(self, ctx, request):
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_string("{VARIABLE_NAME}") == "value"

    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_interp_kwarg(self, ctx, request):
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_string("{OTHER_NAME}", OTHER_NAME="value") == "value"

    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_interp_undefined(self, ctx, monkeypatch, request):
        mock_stdin(monkeypatch, "value")
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_string("{OTHER_NAME}") == "value"

    @mark.parametrize(
        "ctx, res",
        (
            ("simple_ctx", None),
            ("no_error_ctx", "value"),
        ),
    )
    def test_interp_empty(self, ctx, res, request):
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_string("{VARIABLE_NAME}{EMPTY_VARIABLE}") == res


class TestRenderTemplate(_Context):
    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_interp(self, ctx, request):
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_template(Template("{{ VARIABLE_NAME }}")) == "value"

    @mark.parametrize("ctx", ("simple_ctx", "no_error_ctx"))
    def test_iterp_undefined(self, ctx, monkeypatch, request):
        mock_stdin(monkeypatch, "value")
        ctx = request.getfixturevalue(ctx)
        assert ctx.render_template(Template("{{ OTHER_NAME }}")) == "value"

    @mark.parametrize(
        "ctx, res",
        (
            ("simple_ctx", None),
            ("no_error_ctx", "value"),
        ),
    )
    def test_iterp_empty(self, ctx, res, request):
        ctx = request.getfixturevalue(ctx)
        assert (
            ctx.render_template(Template("{{ VARIABLE_NAME }}{{ EMPTY_VARIABLE }}"))
            == res
        )
