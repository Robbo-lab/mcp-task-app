import pytest
from pydantic import ValidationError

from app.core.settings import Settings, settings


class TestSettings:
    # Type checks
    def test_server_host_is_type_str(self):
        assert isinstance(settings.server_host, str)

    def test_server_port_is_type_int(self):
        assert isinstance(settings.server_port, int)

    def test_mcp_base_url_is_type_str(self):
        assert isinstance(settings.mcp_base_url, str)

    def test_mcp_protocol_version_is_type_str(self):
        assert isinstance(settings.mcp_protocol_version, str)

    def test_settings_is_type_settings(self):
        assert isinstance(settings, Settings)

    # Default Values
    def test_settings_default_server_host(self):
        assert settings.server_host == "localhost"

    def test_settings_default_server_port(self):
        assert settings.server_port == 8003

    def test_settings_default_mcp_base_url(self):
        assert settings.mcp_base_url == "http://localhost:8003"

    def test_settings_default_mcp_protocol_version(self):
        assert settings.mcp_protocol_version == "2026-07-28"

    # Validation
    def test_server_host_invalid_raises_validation_error(self):
        with pytest.raises(ValidationError):
            Settings(server_host=[])

    @pytest.mark.parametrize("port", [-3, "-8003", "word"])
    def test_server_port_invalid_raises_validation_error(self, port):
        with pytest.raises(ValidationError):
            Settings(server_port=port)
