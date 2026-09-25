#!/usr/bin/env python3
'''
WatchSleuth Timeline Analysis Tools
Advanced timeline creation and event correlation
'''

import json
import sqlite3
import datetime
from typing import List, Dict, Any
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class TimelineVisualizer:
    '''Create visual timelines and charts from forensic data'''
    
    def __init__(self):
        self.events = []
        
    def load_timeline_data(self, json_file: str):
        '''Load timeline data from JSON file'''
        with open(json_file, 'r') as f:
            data = json.load(f)
            self.events = data.get('timeline', [])
            
    def create_timeline_chart(self, output_file: str, hours: int = 24):
        '''Create visual timeline chart'''
        if not self.events:
            print("[FAIL] No timeline data loaded")
            return
            
        # Convert to DataFrame
        df = pd.DataFrame(self.events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter to specified hours
        end_time = df['timestamp'].max()
        start_time = end_time - pd.Timedelta(hours=hours)
        df_filtered = df[df['timestamp'] >= start_time]
        
        # Create timeline plot
        plt.figure(figsize=(15, 8))
        
        # Group by event type
        event_types = df_filtered['event_type'].unique()
        colors = plt.cm.Set3(range(len(event_types)))
        
        for i, event_type in enumerate(event_types):
            type_events = df_filtered[df_filtered['event_type'] == event_type]
            plt.scatter(type_events['timestamp'], [i] * len(type_events), 
                       label=event_type, color=colors[i], alpha=0.7, s=50)
        
        plt.xlabel('Timeline')
        plt.ylabel('Event Types')
        plt.title(f'Forensic Timeline - Last {hours} Hours')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[PASS] Timeline chart saved: {output_file}")
        
    def create_activity_heatmap(self, output_file: str):
        '''Create activity heatmap by hour and day'''
        if not self.events:
            print("[FAIL] No timeline data loaded")
            return
            
        # Convert to DataFrame
        df = pd.DataFrame(self.events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        # Create activity matrix
        activity_matrix = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
        
        # Create heatmap
        plt.figure(figsize=(15, 6))
        plt.imshow(activity_matrix.values, cmap='YlOrRd', aspect='auto')
        plt.colorbar(label='Activity Count')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.title('Activity Heatmap')
        plt.xticks(range(24), range(24))
        plt.yticks(range(len(activity_matrix.index)), activity_matrix.index)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[PASS] Activity heatmap saved: {output_file}")

class EventCorrelator:
    '''Correlate and analyze relationships between timeline events'''
    
    def __init__(self):
        self.events = []
        
    def load_events(self, events: List[Dict[str, Any]]):
        '''Load events for correlation analysis'''
        self.events = events
        
    def find_event_clusters(self, time_window_minutes: int = 5) -> List[List[Dict]]:
        '''Find clusters of events within time windows'''
        clusters = []
        
        # Sort events by timestamp
        sorted_events = sorted(self.events, key=lambda x: x['timestamp'])
        
        current_cluster = []
        for event in sorted_events:
            if not current_cluster:
                current_cluster.append(event)
                continue
                
            # Check if event is within time window of cluster
            cluster_start = datetime.datetime.fromisoformat(current_cluster[0]['timestamp'])
            event_time = datetime.datetime.fromisoformat(event['timestamp'])
            
            if (event_time - cluster_start).total_seconds() <= time_window_minutes * 60:
                current_cluster.append(event)
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [event]
                
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
            
        return clusters
        
    def analyze_attack_sequence(self) -> Dict[str, Any]:
        '''Analyze events for potential attack sequences'''
        analysis = {
            'potential_attack_chains': [],
            'suspicious_patterns': [],
            'recommendations': []
        }
        
        # Look for common attack patterns
        attack_patterns = [
            {
                'name': 'Credential Dumping Attack',
                'sequence': ['file_accessed', 'process_started', 'network_connection'],
                'indicators': ['lsass.exe', 'mimikatz', 'credential']
            },
            {
                'name': 'Lateral Movement',
                'sequence': ['user_login', 'process_started', 'network_connection'],
                'indicators': ['psexec', 'wmic', 'remote']
            }
        ]
        
        for pattern in attack_patterns:
            matches = self._find_pattern_matches(pattern)
            if matches:
                analysis['potential_attack_chains'].extend(matches)
                
        return analysis
        
    def _find_pattern_matches(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        '''Find events matching attack pattern'''
        matches = []
        
        # Simple pattern matching (would be more sophisticated in real implementation)
        for event in self.events:
            event_desc = event.get('description', '').lower()
            if any(indicator.lower() in event_desc for indicator in pattern['indicators']):
                matches.append({
                    'pattern': pattern['name'],
                    'event': event,
                    'confidence': 0.7
                })
                
        return matches

def main():
    '''Main timeline analysis interface'''
    print("[BARS] WatchSleuth Timeline Analysis Tools")
    print()
    
    # Example usage
    print("[TARGET] Available tools:")
    print("   * Timeline Visualization - Create visual timeline charts")
    print("   * Activity Heatmaps - Show activity patterns by time")
    print("   * Event Correlation - Find related events and attack patterns")
    print("   * Attack Sequence Analysis - Identify potential attack chains")
    print()
    print("[PLAN] Usage examples:")
    print("   visualizer = TimelineVisualizer()")
    print("   visualizer.load_timeline_data('timeline.json')")
    print("   visualizer.create_timeline_chart('timeline.png')")
    print()
    print("   correlator = EventCorrelator()")
    print("   correlator.load_events(events)")
    print("   clusters = correlator.find_event_clusters()")

if __name__ == "__main__":
    main()
