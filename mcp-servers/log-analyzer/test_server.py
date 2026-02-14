#!/usr/bin/env python3
"""
Test script for LogAnalyzer MCP Server
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import search_logs, detect_anomaly

def test_search_logs():
    """Test log search tool"""
    print("\n=== Testing search_logs ===")
    
    # Search for ERROR logs
    result = search_logs("ERROR", "5m", "default")
    print(f"Query: {result['query']}")
    print(f"Matches found: {result['match_count']}")
    
    for log in result['logs'][:3]:  # Show first 3
        print(f"  [{log['timestamp']}] {log['level']}: {log['message']}")
    
    assert result['match_count'] > 0
    print("test_search_logs PASSED")


def test_detect_anomaly():
    """Test anomaly detection tool"""
    print("\n=== Testing detect_anomaly ===")
    
    # Detect ERROR pattern
    result = detect_anomaly("ERROR", 0.3)
    print(f"Pattern: {result['pattern']}")
    print(f"Frequency: {result['frequency']}")
    print(f"Occurrences: {result['occurrence_count']}/{result['total_logs_analyzed']}")
    print(f"Is Anomaly: {result['is_anomaly']}")
    print(f"Severity: {result['severity']}")
    print(f"Spikes detected: {result['spikes_detected']}")
    print(f"Recommendation: {result['recommendation']}")
    
    assert "frequency" in result
    print("test_detect_anomaly PASSED")


if __name__ == "__main__":
    print("Testing LogAnalyzer MCP Server")
    print("=" * 50)
    
    try:
        test_search_logs()
        test_detect_anomaly()
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
