import unittest
from app import app, geocode_address, get_nearby_schools, get_house_info
from unittest.mock import patch


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.geocode_address')
    @patch('app.get_nearby_schools')
    @patch('app.get_house_info')
    @patch('app.model.generate_content')
    def test_search_property(self, mock_generate_content, mock_get_house_info, mock_get_nearby_schools, mock_geocode_address):
        
        form_data = {
            "house_number": "5727",
            "street": "Sagewell Way",
            "city": "San Jose",
            "state": "CA",
            "zip_code": "95138"
        }

        response = self.app.post('/search', data=form_data)
        self.assertIsNotNone(response.data)

    

    def test_index_page(self):
       
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Search Property and Nearby Schools", response.data)

    def test_geocode_address(self):
        """Test the geocode_address function."""
        with patch('app.geolocator.geocode') as mock_geolocator:
            mock_geolocator.return_value = type(
                'MockLocation', (), {"latitude": 37.7749, "longitude": -122.4194})
            lat, lon = geocode_address("123 Main St, San Francisco, CA, 94105")
            self.assertEqual(lat, 37.7749)
            self.assertEqual(lon, -122.4194)

    def test_wrong_address(self):
        with patch('app.geolocator.geocode') as mock_geolocator:
            mock_geolocator.return_value = None
            lat, lon = geocode_address("123 Main St, San Francisco, CA, 94105")
            self.assertIsNone(lat)
            self.assertIsNone(lon)
            

    def test_get_nearby_schools(self):
        with patch('requests.get') as mock_requests:
            mock_requests.return_value.json.return_value = {
                "elements": [{"tags": {"name": "Mock School"}}]
            }
            schools = get_nearby_schools(37.7749, -122.4194)
            self.assertIsNotNone(schools)

    def test_get_house_info(self):
        with patch('app.GoogleSearch') as mock_google_search:
            mock_google_search.return_value.get_dict.return_value = {
                "property": "Mock Property Data"
            }
            result = get_house_info("5727 Sagewell Way, San Jose, CA, 95138")
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
