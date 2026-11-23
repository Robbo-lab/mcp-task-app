from app.mcp.mcp_tools.converter_interface import Converter

class MilesToKilometersConverter(Converter):
    def convert(self, miles: float) -> float:
        """
        Converter function that stores logic for miles to kilometers conversion.

        Args:
            miles (float): Distance in miles.

        Returns:
            float: Distance in kilometers.
        """
        return (
            miles / 0.621371
        )  # uses the same method what was in "miles_to_km" before it was moved here
