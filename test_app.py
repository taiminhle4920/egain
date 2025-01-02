import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import app, geocode_address


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config["TESTING"] = True

    @patch("app.geocode_address")
    @patch("requests.get")
    @patch("app.model.generate_content")
    def test_search_property_valid_address(self, mock_generate_content, mock_requests_get, mock_geocode_address):
        mock_geocode_address.return_value = True
        
        mock_requests_get.return_value.json.return_value = {
            "property": {
                "lotSize": "5600 sqft",
                "bathrooms": 3.5,
                "bedrooms": 5,
                "schools": ["Example Elementary School", "Example High School"],
                "estimatedValue": 1400700
            }
        }
        
        mock_generate_content.return_value.text = "Sample AI-generated summary"

        response = self.client.post(
            "/search",
            data={
                "house_number": "5727",
                "street": "Sagewell Way",
                "city": "San Jose",
                "state": "CA",
                "zip_code": "95138"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Sample AI-generated summary", response.get_data(as_text=True))

    @patch("app.geocode_address")
    def test_search_property_invalid_address(self, mock_geocode_address):
        mock_geocode_address.return_value = False

        response = self.client.post(
            "/search",
            data={
                "house_number": "9999",
                "street": "Invalid Way",
                "city": "Unknown City",
                "state": "XX",
                "zip_code": "00000"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid address", response.get_data(as_text=True))

    def test_geocode_address_valid(self):
        """Test the geocode_address function with a valid address."""
        with patch("app.geolocator.geocode") as mock_geocode:
            mock_geocode.return_value = MagicMock()
            result = geocode_address(
                "1600 Amphitheatre Parkway, Mountain View, CA 94043")
            self.assertTrue(result)

    def test_geocode_address_invalid(self):
        """Test the geocode_address function with an invalid address."""
        with patch("app.geolocator.geocode") as mock_geocode:
            mock_geocode.return_value = None
            result = geocode_address("Invalid Address")
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
