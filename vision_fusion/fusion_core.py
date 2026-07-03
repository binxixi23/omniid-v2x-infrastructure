import json
import math
import time

class OmniIDVisionFusionEngine:
    def __init__(self, tolerance_degrees=5.0, timeout_seconds=1.5):
        self.tolerance_degrees = tolerance_degrees
        self.timeout_seconds = timeout_seconds
        
        # State tracking registries
        self.active_v2x_registry = {}
        self.last_seen_v2x_timestamps = {}

    def update_v2x_identity(self, telemetry_packet_str):
        """Ingests live streams from the V2X receiver layer."""
        try:
            data = json.loads(telemetry_packet_str)
            entity_id = data["entity_id"]
            
            # Cache the identity payload and refresh the heartbeat timestamp
            self.active_v2x_registry[entity_id] = data
            self.last_seen_v2x_timestamps[entity_id] = time.time()
            return entity_id, "SUCCESS"
        except Exception as e:
            return None, f"CORRUPTED_PACKET_ERROR: {str(e)}"

    def process_vision_inference(self, yolo_inference_str):
        """
        Processes rough optical data from YOLO and cross-references it with V2X.
        Includes safety logic for missing, mismatched, or dropped signals.
        """
        current_time = time.time()
        yolo_data = json.loads(yolo_inference_str)
        detected_class = yolo_data["detected_class"]
        camera_angle = yolo_data["bearing_angle"]

        print(f"\n[YOLO Vision] Object spotted visually: '{detected_class}' at bearing {camera_angle}°")

        # Clean up stale/expired digital IDs (Signal Dropout Check)
        expired_ids = [
            eid for eid, t_stamp in self.last_seen_v2x_timestamps.items()
            if (current_time - t_stamp) > self.timeout_seconds
        ]
        for eid in expired_ids:
            print(f"⚠️ [V2X DROPOUT] Identity '{eid}' lost telemetry signal (Timeout exceeded).")
            del self.active_v2x_registry[eid]
            del self.last_seen_v2x_timestamps[eid]

        # Spatial cross-verification matching logic
        matched_identity = None
        for entity_id, identity in self.active_v2x_registry.items():
            v2x_angle = identity["telemetry"]["heading"]
            
            # Geometry check: Does the broadcast angle align with physical sight?
            if math.isclose(camera_angle, v2x_angle, abs_tol=self.tolerance_degrees):
                matched_identity = identity
                break

        # Decision Matrix & Cooperative Intelligence Policy Execution
        if matched_identity:
            print(f"🎯 [VERIFIED - 100%] Visual object matches digital ID: '{matched_identity['entity_id']}'")
            print(f"   ↳ Direct Metadata Ingest -> Scale: {matched_identity['dimensions']}")
            print(f"   ↳ Fail-Safe Rule Imposed: {matched_identity['safety_policy']}")
            return "VERIFIED", matched_identity['entity_id']
            
        else:
            # Anomalous State: Camera sees something, but there is no matching digital broadcast
            print("🚨 [CRITICAL ANOMALY DETECTED] Visual structure lacks valid V2X authentication!")
            print("   ↳ System Flag: Potential spoofing attack, hardware failure, or un-tagged hazard.")
            print("   ↳ Fallback Action: ENGAGE MAXIMUM DISTANCE BUFFER / EMERGENCY BRAKE KINETICS.")
            return "UNVERIFIED_HAZARD", None

# --- Local Simulation Execution Loop ---
if __name__ == '__main__':
    # Initialize the fusion workspace node
    fusion_node = OmniIDVisionFusionEngine(tolerance_degrees=5.0, timeout_seconds=1.5)
    
    # 1. Normal Operation Scenario (V2X matches Camera exactly)
    print("--- SCENARIO 1: Cooperative State Sync ---")
    mock_v2x_packet = json.dumps({
        "entity_id": "DOCK-ZONE-04A",
        "class": "static_infrastructure",
        "sub_class": "charging_station",
        "dimensions": {"width": 0.4, "length": 0.4, "height": 0.6},
        "telemetry": {"lat_offset": 1.25, "long_offset": -0.82, "heading": 180.0},
        "safety_policy": "innate_yield_priority"
    })
    mock_yolo_input_1 = json.dumps({"detected_class": "box_structure", "bearing_angle": 181.2})
    
    fusion_node.update_v2x_identity(mock_v2x_packet)
    fusion_node.process_vision_inference(mock_yolo_input_1)
    
    time.sleep(0.5)

    # 2. Critical Mismatch / Spoofing Anomaly Scenario
    print("\n--- SCENARIO 2: Geometry Tampering / Signal Disparity ---")
    # Camera sees something at 45° but no V2X module is broadcasting at 45°
    mock_yolo_input_2 = json.dumps({"detected_class": "unknown_vehicle", "bearing_angle": 45.0})
    fusion_node.process_vision_inference(mock_yolo_input_2)
    
    time.sleep(1.1) # Exceed timeout parameters to trigger signal drop

    # 3. Hardware / Blackout Dropout Scenario
    print("\n--- SCENARIO 3: Telemetry Infrastructure Dropout ---")
    # Checking for previous DOCK-ZONE-04A node at 180° after tracking timed out
    mock_yolo_input_3 = json.dumps({"detected_class": "box_structure", "bearing_angle": 180.0})
    fusion_node.process_vision_inference(mock_yolo_input_3)
