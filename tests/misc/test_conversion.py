import pytest
from app.mcp.mcp_tools.conversion import MilesToKilometersConverter
from app.mcp.mcp_tools.converter_interface import Converter

def test_miles_to_kilometers_conversion():
    converter = MilesToKilometersConverter()
    result = converter.convert(10)
    assert result == 10 / 0.621371

def test_miles_zero_conversion():
    converter = MilesToKilometersConverter()
    result = converter.convert(0)
    assert result == 0

def test_interface_converter():
    converter = MilesToKilometersConverter()
    assert isinstance(converter, Converter)

def test_one_mile_conversion():
    converter = MilesToKilometersConverter()
    result = converter.convert(1)

    assert result == pytest.approx(1 / 0.621371)