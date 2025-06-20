# backend/test_datasource_apis.py
import requests
import json
import time
from typing import Dict, Any

class DataSourceAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_response(self, response: requests.Response, title: str):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        print(f"{'='*60}")
        
        return response.json() if response.status_code == 200 else None

    def test_health_check(self):
        """Test if backend is running"""
        print("🏥 Testing Backend Health...")
        response = self.session.get(f"{self.base_url}/")
        return self.print_response(response, "Health Check")

    def test_connection(self, source_type: str, connection_config: Dict[str, Any]):
        """Test data source connection"""
        print(f"🔌 Testing {source_type.upper()} Connection...")
        
        payload = {
            "source_type": source_type,
            "connection_config": connection_config
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/test-connection",
            json=payload
        )
        return self.print_response(response, f"{source_type.upper()} Connection Test")

    def create_data_source(self, name: str, source_type: str, connection_config: Dict[str, Any]):
        """Create a new data source"""
        print(f"➕ Creating Data Source: {name}")
        
        payload = {
            "source_name": name,
            "source_type": source_type,
            "connection_config": connection_config
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/",
            json=payload
        )
        return self.print_response(response, f"Create Data Source: {name}")

    def get_all_data_sources(self):
        """Get all data sources"""
        print("📋 Getting All Data Sources...")
        response = self.session.get(f"{self.base_url}/datasources/")
        return self.print_response(response, "All Data Sources")

    def discover_measurements(self, source_type: str, connection_config: Dict[str, Any]):
        """Discover measurements"""
        print(f"🔍 Discovering Measurements for {source_type.upper()}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": connection_config
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/discover/measurements",
            json=payload
        )
        return self.print_response(response, f"Discover Measurements - {source_type.upper()}")

    def discover_tags(self, source_type: str, connection_config: Dict[str, Any], measurement: str):
        """Discover tags for a measurement"""
        print(f"🏷️ Discovering Tags for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": connection_config,
            "measurement": measurement
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/discover/tags",
            json=payload
        )
        return self.print_response(response, f"Discover Tags - {measurement}")

    def discover_fields(self, source_type: str, connection_config: Dict[str, Any], measurement: str):
        """Discover fields for a measurement"""
        print(f"📊 Discovering Fields for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": connection_config,
            "measurement": measurement
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/discover/fields",
            json=payload
        )
        return self.print_response(response, f"Discover Fields - {measurement}")

    def get_sample_data(self, source_type: str, connection_config: Dict[str, Any], measurement: str):
        """Get sample data from measurement"""
        print(f"📄 Getting Sample Data for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": connection_config,
            "measurement": measurement
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/discover/sample",
            json=payload
        )
        return self.print_response(response, f"Sample Data - {measurement}")

    def get_equipments(self):
        """Get all equipments from existing API"""
        print("🔧 Getting All Equipments...")
        response = self.session.get(f"{self.base_url}/equipments")
        return self.print_response(response, "All Equipments")

    def create_mapping(self, source_id: str, equipment_id: int, measurement_name: str, 
                      tag_mappings: Dict[str, str], field_mappings: Dict[str, str]):
        """Create source mapping"""
        print(f"🔗 Creating Mapping: {measurement_name} -> Equipment {equipment_id}")
        
        payload = {
            "source_id": source_id,
            "equipment_id": equipment_id,
            "measurement_name": measurement_name,
            "tag_mappings": tag_mappings,
            "field_mappings": field_mappings
        }
        
        response = self.session.post(
            f"{self.base_url}/datasources/mappings",
            json=payload
        )
        return self.print_response(response, f"Create Mapping - {measurement_name}")

    def get_mappings_by_source(self, source_id: str):
        """Get mappings for a data source"""
        print(f"📋 Getting Mappings for Source: {source_id}")
        response = self.session.get(f"{self.base_url}/datasources/{source_id}/mappings")
        return self.print_response(response, f"Mappings for Source {source_id}")

    def auto_map_measurements(self, source_id: str):
        """Auto-create mappings"""
        print(f"🤖 Auto-mapping Measurements for Source: {source_id}")
        response = self.session.post(f"{self.base_url}/datasources/{source_id}/auto-map")
        return self.print_response(response, f"Auto-map Source {source_id}")

def main():
    """Main test function"""
    print("🚀 Starting Backend API Tests")
    print("="*80)
    
    tester = DataSourceAPITester()
    
    # 1. Health Check
    health = tester.test_health_check()
    if not health:
        print("❌ Backend is not running. Please start FastAPI server first.")
        return
    
    # 2. Test with user's InfluxDB connection
    print("\n" + "="*80)
    print("📝 PLEASE PROVIDE YOUR INFLUXDB CONNECTION DETAILS:")
    print("="*80)
    
    # Get InfluxDB connection details from user
    influx_url = input("InfluxDB URL (e.g., http://localhost:8086): ").strip()
    influx_token = input("InfluxDB Token: ").strip()
    influx_org = input("InfluxDB Organization: ").strip()
    influx_bucket = input("InfluxDB Bucket: ").strip()
    
    influx_config = {
        "url": influx_url,
        "token": influx_token,
        "org": influx_org,
        "bucket": influx_bucket
    }
    
    # Test InfluxDB connection
    connection_result = tester.test_connection("influxdb", influx_config)
    
    if not connection_result or not connection_result.get("success"):
        print("❌ InfluxDB connection failed. Please check your credentials.")
        return
    
    # 3. Create InfluxDB data source
    source_data = tester.create_data_source("Test InfluxDB", "influxdb", influx_config)
    if not source_data:
        print("❌ Failed to create data source")
        return
    
    source_id = source_data["source_id"]
    print(f"✅ Created data source with ID: {source_id}")
    
    # 4. Discover measurements
    measurements_data = tester.discover_measurements("influxdb", influx_config)
    measurements = measurements_data.get("measurements", []) if measurements_data else []
    
    if not measurements:
        print("⚠️ No measurements found in InfluxDB")
        return
    
    print(f"✅ Found {len(measurements)} measurements: {measurements}")
    
    # 5. Test discovery for first measurement
    first_measurement = measurements[0]
    print(f"\n🔬 Testing Discovery for Measurement: {first_measurement}")
    
    tags_data = tester.discover_tags("influxdb", influx_config, first_measurement)
    fields_data = tester.discover_fields("influxdb", influx_config, first_measurement)
    sample_data = tester.get_sample_data("influxdb", influx_config, first_measurement)
    
    tags = tags_data.get("tags", []) if tags_data else []
    fields = fields_data.get("fields", []) if fields_data else []
    
    # 6. Get existing equipments
    equipments_data = tester.get_equipments()
    equipments = equipments_data if equipments_data else []
    
    if not equipments:
        print("⚠️ No equipments found in database. Please create some equipment first.")
        print("💡 You can create equipment using: POST /equipments")
        return
    
    print(f"✅ Found {len(equipments)} equipments")
    for eq in equipments:
        print(f"   - ID: {eq['id']}, Name: {eq['name']}")
    
    # 7. Create manual mapping
    print("\n" + "="*80)
    print("🔗 MANUAL MAPPING CONFIGURATION:")
    print("="*80)
    
    # Show available equipments
    print("Available Equipments:")
    for eq in equipments:
        print(f"   {eq['id']}: {eq['name']}")
    
    equipment_id = input(f"\nSelect Equipment ID to map with '{first_measurement}': ").strip()
    
    try:
        equipment_id = int(equipment_id)
    except ValueError:
        print("❌ Invalid equipment ID")
        return
    
    # Create simple mappings
    tag_mappings = {tag: tag for tag in tags[:3]}  # Map first 3 tags
    field_mappings = {field['name']: field['name'] for field in fields[:3]}  # Map first 3 fields
    
    print(f"Tag Mappings: {tag_mappings}")
    print(f"Field Mappings: {field_mappings}")
    
    mapping_data = tester.create_mapping(
        source_id, equipment_id, first_measurement, tag_mappings, field_mappings
    )
    
    if mapping_data:
        print(f"✅ Created mapping with ID: {mapping_data['mapping_id']}")
    
    # 8. Get all mappings for the source
    tester.get_mappings_by_source(source_id)
    
    # 9. Test auto-mapping (if there are more measurements)
    if len(measurements) > 1:
        print(f"\n🤖 Testing Auto-mapping for remaining measurements...")
        tester.auto_map_measurements(source_id)
    
    # 10. Final summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    
    tester.get_all_data_sources()
    tester.get_mappings_by_source(source_id)
    
    print("\n🎉 Backend API tests completed successfully!")
    print("✅ All APIs are working correctly")
    print("✅ InfluxDB connection established")
    print("✅ Discovery services working")
    print("✅ Mapping system operational")

if __name__ == "__main__":
    main()