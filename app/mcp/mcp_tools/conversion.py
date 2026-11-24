from typing import override

from app.mcp.mcp_tools.converter_interface import Converter


class MilesToKilometersConverter(Converter):
    @override
    def convert(self, miles: float) -> float:
        """
        Converter function that stores logic for miles to kilometers conversion.

        Args:
            miles (float): Distance in miles.

        Returns:
            float: Distance in kilometers.
        """
        return miles / 0.621371
