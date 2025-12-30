"""
XES (eXtensible Event Stream) Parser for Process Mining
Lightweight parser that converts XES event logs to pandas DataFrames

Supports:
- Standard XES format from BPI Challenge datasets
- Trace/Event extraction
- Attribute parsing (concept:name, time:timestamp, lifecycle:transition, etc.)
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import os
import gzip
import logging

logger = logging.getLogger(__name__)

# XES namespace
XES_NS = {
    'xes': 'http://www.xes-standard.org/'
}


def parse_xes_file(filepath: str, max_traces: Optional[int] = None) -> pd.DataFrame:
    """
    Parse a XES file and return a pandas DataFrame.
    
    Args:
        filepath: Path to .xes or .xes.gz file
        max_traces: Maximum number of traces to parse (for sampling large files)
    
    Returns:
        DataFrame with columns: case_id, activity, timestamp, resource, lifecycle, 
        plus any additional attributes found
    """
    logger.info(f"Parsing XES file: {filepath}")
    
    # Handle gzipped files
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            tree = ET.parse(f)
    else:
        tree = ET.parse(filepath)
    
    root = tree.getroot()
    
    # Handle namespace
    ns = {}
    if root.tag.startswith('{'):
        ns_end = root.tag.find('}')
        ns['xes'] = root.tag[1:ns_end]
    
    events = []
    trace_count = 0
    
    # Find all traces
    for trace in root.iter('trace'):
        if max_traces and trace_count >= max_traces:
            break
        
        trace_count += 1
        
        # Extract trace-level attributes (case attributes)
        case_attrs = _parse_attributes(trace)
        case_id = case_attrs.get('concept:name', f'Case_{trace_count}')
        
        # Extract events in this trace
        for event in trace.iter('event'):
            event_attrs = _parse_attributes(event)
            
            # Merge case and event attributes
            event_record = {
                'case_id': case_id,
                'activity': event_attrs.get('concept:name', 'Unknown'),
                'timestamp': event_attrs.get('time:timestamp'),
                'resource': event_attrs.get('org:resource', event_attrs.get('org:group', '')),
                'lifecycle': event_attrs.get('lifecycle:transition', 'complete'),
            }
            
            # Add any additional attributes
            for key, value in event_attrs.items():
                if key not in ['concept:name', 'time:timestamp', 'org:resource', 'org:group', 'lifecycle:transition']:
                    event_record[key] = value
            
            # Add case-level attributes
            for key, value in case_attrs.items():
                if key not in ['concept:name'] and key not in event_record:
                    event_record[f'case_{key}'] = value
            
            events.append(event_record)
    
    df = pd.DataFrame(events)
    
    # Convert timestamp to datetime
    if 'timestamp' in df.columns and len(df) > 0:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Sort by case and timestamp
    if len(df) > 0:
        df = df.sort_values(['case_id', 'timestamp']).reset_index(drop=True)
    
    logger.info(f"Parsed {len(df)} events from {trace_count} traces")
    return df


def _parse_attributes(element: ET.Element) -> Dict:
    """Parse XES attributes from an element."""
    attrs = {}
    
    for child in element:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        key = child.get('key', '')
        value = child.get('value', '')
        
        if tag == 'string':
            attrs[key] = value
        elif tag == 'date':
            attrs[key] = value
        elif tag == 'int':
            attrs[key] = int(value) if value else 0
        elif tag == 'float':
            attrs[key] = float(value) if value else 0.0
        elif tag == 'boolean':
            attrs[key] = value.lower() == 'true'
    
    return attrs


def get_xes_summary(filepath: str) -> Dict:
    """
    Get summary statistics about a XES file without fully loading it.
    
    Returns:
        Dict with trace_count, event_count, activity_count, date_range
    """
    if filepath.endswith('.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
            tree = ET.parse(f)
    else:
        tree = ET.parse(filepath)
    
    root = tree.getroot()
    
    trace_count = 0
    event_count = 0
    activities = set()
    min_time = None
    max_time = None
    
    for trace in root.iter('trace'):
        trace_count += 1
        for event in trace.iter('event'):
            event_count += 1
            attrs = _parse_attributes(event)
            
            if 'concept:name' in attrs:
                activities.add(attrs['concept:name'])
            
            if 'time:timestamp' in attrs:
                try:
                    ts = pd.to_datetime(attrs['time:timestamp'])
                    if min_time is None or ts < min_time:
                        min_time = ts
                    if max_time is None or ts > max_time:
                        max_time = ts
                except:
                    pass
    
    return {
        'trace_count': trace_count,
        'event_count': event_count,
        'activity_count': len(activities),
        'activities': list(activities)[:20],  # First 20 activities
        'date_range': {
            'start': min_time.isoformat() if min_time else None,
            'end': max_time.isoformat() if max_time else None
        }
    }


def standardize_xes_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize a XES-parsed DataFrame to match the expected format.
    
    Ensures columns: case_id, activity, timestamp, resource, value, priority, region
    """
    # Rename common XES column names to standard names
    column_mapping = {
        'concept:name': 'activity',
        'time:timestamp': 'timestamp',
        'org:resource': 'resource',
        'lifecycle:transition': 'lifecycle'
    }
    
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Ensure required columns exist
    if 'resource' not in df.columns:
        df['resource'] = 'Unknown'
    if 'value' not in df.columns:
        df['value'] = 0
    if 'priority' not in df.columns:
        df['priority'] = 'Medium'
    if 'region' not in df.columns:
        df['region'] = 'Unknown'
    if 'customer' not in df.columns:
        df['customer'] = df['case_id'].apply(lambda x: f"Customer_{hash(x) % 100}")
    
    return df
