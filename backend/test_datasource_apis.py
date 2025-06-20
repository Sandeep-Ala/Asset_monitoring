# backend/test_datasource_apis_comprehensive.py
import requests
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

class ComprehensiveDataSourceTester:
    """Comprehensive tester for all DataSource APIs"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed_tests"] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.test_results["failed_tests"] += 1
            print(f"❌ {test_name}: {message}")
        
        self.test_results["test_details"].append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def print_response(self, response: requests.Response, test_name: str) -> Optional[Dict]:
        """Print and log API response"""
        try:
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test(test_name, True, f"Status: {response.status_code}", data)
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                return data
            else:
                error_msg = f"Status: {response.status_code}, Response: {response.text[:200]}"
                self.log_test(test_name, False, error_msg)
                return None
        except Exception as e:
            error_msg = f"Failed to parse response: {str(e)}"
            self.log_test(test_name, False, error_msg)
            return None

    # ---------- Health and Basic Tests ----------
    def test_health_check(self) -> bool:
        """Test backend health"""
        print("🔍 Testing Backend Health...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = self.print_response(response, "Health Check")
            return result is not None
        except Exception as e:
            self.log_test("Health Check", False, f"Connection failed: {str(e)}")
            return False

    # ---------- Connection Testing ----------
    def test_influxdb_connection(self, config: Dict[str, Any]) -> bool:
        """Test InfluxDB connection"""
        print("🔌 Testing InfluxDB Connection...")
        
        payload = {
            "source_type": "influxdb",
            "connection_config": config
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/test-connection",
                json=payload
            )
            result = self.print_response(response, "InfluxDB Connection Test")
            return result and result.get("success", False)
        except Exception as e:
            self.log_test("InfluxDB Connection Test", False, f"Request failed: {str(e)}")
            return False

    def test_parquet_connection(self, config: Dict[str, Any]) -> bool:
        """Test Parquet connection"""
        print("🔌 Testing Parquet Connection...")
        
        payload = {
            "source_type": "parquet",
            "connection_config": config
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/test-connection",
                json=payload
            )
            result = self.print_response(response, "Parquet Connection Test")
            return result and result.get("success", False)
        except Exception as e:
            self.log_test("Parquet Connection Test", False, f"Request failed: {str(e)}")
            return False

    # ---------- Data Source CRUD ----------
    def create_data_source(self, name: str, source_type: str, config: Dict[str, Any]) -> Optional[str]:
        """Create a new data source"""
        print(f"➕ Creating Data Source: {name}")
        
        payload = {
            "source_name": name,
            "source_type": source_type,
            "connection_config": config
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/",
                json=payload
            )
            result = self.print_response(response, f"Create Data Source: {name}")
            return result.get("source_id") if result else None
        except Exception as e:
            self.log_test(f"Create Data Source: {name}", False, f"Request failed: {str(e)}")
            return None

    def get_all_data_sources(self) -> Optional[List[Dict]]:
        """Get all data sources"""
        print("📋 Getting All Data Sources...")
        
        try:
            response = self.session.get(f"{self.base_url}/datasources/")
            result = self.print_response(response, "Get All Data Sources")
            return result if isinstance(result, list) else None
        except Exception as e:
            self.log_test("Get All Data Sources", False, f"Request failed: {str(e)}")
            return None

    def get_data_source_by_id(self, source_id: str) -> Optional[Dict]:
        """Get data source by ID"""
        print(f"🔍 Getting Data Source: {source_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/datasources/{source_id}")
            result = self.print_response(response, f"Get Data Source: {source_id}")
            return result
        except Exception as e:
            self.log_test(f"Get Data Source: {source_id}", False, f"Request failed: {str(e)}")
            return None

    def update_data_source(self, source_id: str, updates: Dict[str, Any]) -> bool:
        """Update data source"""
        print(f"✏️ Updating Data Source: {source_id}")
        
        try:
            response = self.session.put(
                f"{self.base_url}/datasources/{source_id}",
                json=updates
            )
            result = self.print_response(response, f"Update Data Source: {source_id}")
            return result is not None
        except Exception as e:
            self.log_test(f"Update Data Source: {source_id}", False, f"Request failed: {str(e)}")
            return False

    def toggle_data_source(self, source_id: str) -> bool:
        """Toggle data source active status"""
        print(f"🔄 Toggling Data Source: {source_id}")
        
        try:
            response = self.session.post(f"{self.base_url}/datasources/{source_id}/toggle")
            result = self.print_response(response, f"Toggle Data Source: {source_id}")
            return result is not None
        except Exception as e:
            self.log_test(f"Toggle Data Source: {source_id}", False, f"Request failed: {str(e)}")
            return False

    def delete_data_source(self, source_id: str) -> bool:
        """Delete data source"""
        print(f"🗑️ Deleting Data Source: {source_id}")
        
        try:
            response = self.session.delete(f"{self.base_url}/datasources/{source_id}")
            result = self.print_response(response, f"Delete Data Source: {source_id}")
            return result is not None
        except Exception as e:
            self.log_test(f"Delete Data Source: {source_id}", False, f"Request failed: {str(e)}")
            return False

    # ---------- Discovery Operations ----------
    def discover_measurements(self, source_type: str, config: Dict[str, Any]) -> Optional[List[str]]:
        """Discover measurements via POST endpoint"""
        print(f"🔍 Discovering Measurements for {source_type.upper()}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": config
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/discover/measurements",
                json=payload
            )
            result = self.print_response(response, f"Discover Measurements: {source_type}")
            return result.get("measurements", []) if result else None
        except Exception as e:
            self.log_test(f"Discover Measurements: {source_type}", False, f"Request failed: {str(e)}")
            return None

    def discover_measurements_by_id(self, source_id: str) -> Optional[List[str]]:
        """Discover measurements via GET endpoint with source ID"""
        print(f"🔍 Discovering Measurements for Source: {source_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/datasources/{source_id}/discover/measurements")
            result = self.print_response(response, f"Discover Measurements by ID: {source_id}")
            return result.get("measurements", []) if result else None
        except Exception as e:
            self.log_test(f"Discover Measurements by ID: {source_id}", False, f"Request failed: {str(e)}")
            return None

    def discover_tags(self, source_type: str, config: Dict[str, Any], measurement: str) -> Optional[List[str]]:
        """Discover tags for a measurement"""
        print(f"🏷️ Discovering Tags for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": config,
            "measurement": measurement
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/discover/tags",
                json=payload
            )
            result = self.print_response(response, f"Discover Tags: {measurement}")
            return result.get("tags", []) if result else None
        except Exception as e:
            self.log_test(f"Discover Tags: {measurement}", False, f"Request failed: {str(e)}")
            return None

    def discover_fields(self, source_type: str, config: Dict[str, Any], measurement: str) -> Optional[List[Dict]]:
        """Discover fields for a measurement"""
        print(f"📊 Discovering Fields for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": config,
            "measurement": measurement
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/discover/fields",
                json=payload
            )
            result = self.print_response(response, f"Discover Fields: {measurement}")
            return result.get("fields", []) if result else None
        except Exception as e:
            self.log_test(f"Discover Fields: {measurement}", False, f"Request failed: {str(e)}")
            return None

    def get_sample_data(self, source_type: str, config: Dict[str, Any], measurement: str) -> Optional[List[Dict]]:
        """Get sample data for a measurement"""
        print(f"📝 Getting Sample Data for {measurement}...")
        
        payload = {
            "source_type": source_type,
            "connection_config": config,
            "measurement": measurement
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/discover/sample",
                json=payload
            )
            result = self.print_response(response, f"Sample Data: {measurement}")
            return result.get("sample_data", []) if result else None
        except Exception as e:
            self.log_test(f"Sample Data: {measurement}", False, f"Request failed: {str(e)}")
            return None

    # ---------- Equipment Operations ----------
    def get_equipments(self) -> Optional[List[Dict]]:
        """Get all equipments"""
        print("⚙️ Getting All Equipments...")
        
        try:
            response = self.session.get(f"{self.base_url}/equipments")
            result = self.print_response(response, "Get All Equipments")
            return result if isinstance(result, list) else None
        except Exception as e:
            self.log_test("Get All Equipments", False, f"Request failed: {str(e)}")
            return None

    # ---------- Mapping Operations ----------
    def create_mapping(self, source_id: str, equipment_id: int, measurement: str, 
                      tag_mappings: Dict[str, str], field_mappings: Dict[str, str]) -> Optional[str]:
        """Create source mapping"""
        print(f"🔗 Creating Mapping: {measurement} -> Equipment {equipment_id}")
        
        payload = {
            "source_id": source_id,
            "equipment_id": equipment_id,
            "measurement_name": measurement,
            "tag_mappings": tag_mappings,
            "field_mappings": field_mappings
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/datasources/mappings",
                json=payload
            )
            result = self.print_response(response, f"Create Mapping: {measurement}")
            return result.get("mapping_id") if result else None
        except Exception as e:
            self.log_test(f"Create Mapping: {measurement}", False, f"Request failed: {str(e)}")
            return None

    def get_mappings_by_source(self, source_id: str) -> Optional[List[Dict]]:
        """Get mappings for a data source"""
        print(f"📋 Getting Mappings for Source: {source_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/datasources/{source_id}/mappings")
            result = self.print_response(response, f"Get Mappings: {source_id}")
            return result if isinstance(result, list) else None
        except Exception as e:
            self.log_test(f"Get Mappings: {source_id}", False, f"Request failed: {str(e)}")
            return None

    def get_mappings_by_equipment(self, equipment_id: int) -> Optional[List[Dict]]:
        """Get mappings for an equipment"""
        print(f"📋 Getting Mappings for Equipment: {equipment_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/datasources/mappings/equipment/{equipment_id}")
            result = self.print_response(response, f"Get Equipment Mappings: {equipment_id}")
            return result if isinstance(result, list) else None
        except Exception as e:
            self.log_test(f"Get Equipment Mappings: {equipment_id}", False, f"Request failed: {str(e)}")
            return None

    def update_mapping(self, mapping_id: str, updates: Dict[str, Any]) -> bool:
        """Update source mapping"""
        print(f"✏️ Updating Mapping: {mapping_id}")
        
        try:
            response = self.session.put(
                f"{self.base_url}/datasources/mappings/{mapping_id}",
                json=updates
            )
            result = self.print_response(response, f"Update Mapping: {mapping_id}")
            return result is not None
        except Exception as e:
            self.log_test(f"Update Mapping: {mapping_id}", False, f"Request failed: {str(e)}")
            return False

    def delete_mapping(self, mapping_id: str) -> bool:
        """Delete source mapping"""
        print(f"🗑️ Deleting Mapping: {mapping_id}")
        
        try:
            response = self.session.delete(f"{self.base_url}/datasources/mappings/{mapping_id}")
            result = self.print_response(response, f"Delete Mapping: {mapping_id}")
            return result is not None
        except Exception as e:
            self.log_test(f"Delete Mapping: {mapping_id}", False, f"Request failed: {str(e)}")
            return False

    def auto_map_measurements(self, source_id: str) -> Optional[Dict]:
        """Auto-create mappings"""
        print(f"🤖 Auto-mapping Measurements for Source: {source_id}")
        
        try:
            response = self.session.post(f"{self.base_url}/datasources/{source_id}/auto-map")
            result = self.print_response(response, f"Auto-map: {source_id}")
            return result
        except Exception as e:
            self.log_test(f"Auto-map: {source_id}", False, f"Request failed: {str(e)}")
            return None

    # ---------- Test Summary ----------
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({'✅' if passed > 0 else '❌'})")
        print(f"Failed: {failed} ({'❌' if failed > 0 else '✅'})")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results["test_details"]:
                if not test["success"]:
                    print(f"   - {test['test']}: {test['message']}")
        
        print("\n" + "="*80)


def main():
    """Main comprehensive test function"""
    print("🚀 Starting Comprehensive DataSource API Tests")
    print("="*80)
    
    tester = ComprehensiveDataSourceTester()
    
    # 1. Health Check
    if not tester.test_health_check():
        print("❌ Backend is not running. Please start FastAPI server first.")
        return
    
    # 2. Get connection details
    print("\n" + "="*80)
    print("📝 INFLUXDB CONNECTION CONFIGURATION")
    print("="*80)
    
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
    
    # 3. Connection Tests
    print("\n" + "="*80)
    print("🔌 CONNECTION TESTING")
    print("="*80)
    
    if not tester.test_influxdb_connection(influx_config):
        print("❌ InfluxDB connection failed. Continuing with other tests...")
    
    # 4. Data Source CRUD Tests
    print("\n" + "="*80)
    print("📁 DATA SOURCE CRUD OPERATIONS")
    print("="*80)
    
    # Create data source
    source_id = tester.create_data_source("Test InfluxDB", "influxdb", influx_config)
    if not source_id:
        print("❌ Failed to create data source. Aborting further tests.")
        tester.print_test_summary()
        return
    
    # Get all sources
    tester.get_all_data_sources()
    
    # Get source by ID
    tester.get_data_source_by_id(source_id)
    
    # Update source
    tester.update_data_source(source_id, {"source_name": "Updated Test InfluxDB"})
    
    # Toggle source
    tester.toggle_data_source(source_id)
    tester.toggle_data_source(source_id)  # Toggle back
    
    # 5. Discovery Tests
    print("\n" + "="*80)
    print("🔍 SCHEMA DISCOVERY OPERATIONS")
    print("="*80)
    
    # Discover measurements (both methods)
    measurements_post = tester.discover_measurements("influxdb", influx_config)
    measurements_get = tester.discover_measurements_by_id(source_id)
    
    if not measurements_post and not measurements_get:
        print("⚠️ No measurements found. Creating some sample data...")
        # Continue with remaining tests anyway
        measurements = ["sample_measurement"]
    else:
        measurements = measurements_post or measurements_get or []
    
    # Test discovery for first measurement if available
    if measurements:
        first_measurement = measurements[0]
        print(f"\n🔬 Testing Discovery for: {first_measurement}")
        
        tags = tester.discover_tags("influxdb", influx_config, first_measurement)
        fields = tester.discover_fields("influxdb", influx_config, first_measurement)
        sample_data = tester.get_sample_data("influxdb", influx_config, first_measurement)
        
        print(f"   Tags found: {len(tags) if tags else 0}")
        print(f"   Fields found: {len(fields) if fields else 0}")
        print(f"   Sample records: {len(sample_data) if sample_data else 0}")
    
    # 6. Equipment Tests
    print("\n" + "="*80)
    print("⚙️ EQUIPMENT OPERATIONS")
    print("="*80)
    
    equipments = tester.get_equipments()
    if not equipments:
        print("⚠️ No equipments found. Please create equipment first for mapping tests.")
        tester.print_test_summary()
        return
    
    print(f"✅ Found {len(equipments)} equipments")
    for eq in equipments[:3]:  # Show first 3
        print(f"   - ID: {eq['id']}, Name: {eq['name']}")
    
    # 7. Mapping Tests
    print("\n" + "="*80)
    print("🔗 MAPPING OPERATIONS")
    print("="*80)
    
    if measurements and equipments:
        # Create manual mapping
        first_equipment = equipments[0]
        measurement = measurements[0]
        
        tag_mappings = {"rack": "rack", "bank": "bank"} if tags and len(tags) >= 2 else {}
        field_mappings = {"soc": "soc", "voltage": "voltage"} if fields and len(fields) >= 2 else {}
        
        mapping_id = tester.create_mapping(
            source_id, 
            first_equipment['id'], 
            measurement, 
            tag_mappings, 
            field_mappings
        )
        
        if mapping_id:
            # Test mapping operations
            tester.get_mappings_by_source(source_id)
            tester.get_mappings_by_equipment(first_equipment['id'])
            
            # Update mapping
            tester.update_mapping(mapping_id, {"tag_mappings": {"rack": "rack_number"}})
            
            # Auto-mapping test
            if len(measurements) > 1:
                tester.auto_map_measurements(source_id)
            
            # Clean up - delete mapping
            #tester.delete_mapping(mapping_id)
    
    # 8. Cleanup
    print("\n" + "="*80)
    print("🧹 CLEANUP")
    print("="*80)
    
    # Delete test data source
    #tester.delete_data_source(source_id)
    
    # 9. Final Summary
    tester.print_test_summary()
    
    print("\n🎉 Comprehensive API testing completed!")


if __name__ == "__main__":
    main()