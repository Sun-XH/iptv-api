#!/usr/bin/env python3
"""
Script to filter and save IPv6 channels from the results
"""

import os
import re
from collections import defaultdict

def read_result_file(file_path):
    """Read the result file and parse channels"""
    channels = defaultdict(list)
    current_category = ""
    
    if not os.path.exists(file_path):
        print(f"Result file not found: {file_path}")
        return channels
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(',#genre#'):
                current_category = line.replace(',#genre#', '')
                continue
            
            if ',' in line:
                parts = line.split(',', 1)
                if len(parts) == 2:
                    name, url = parts[0], parts[1]
                    channels[current_category].append({
                        'name': name,
                        'url': url
                    })
    
    return channels

def is_ipv6_url(url):
    """Check if URL contains IPv6 address"""
    # IPv6 patterns
    ipv6_patterns = [
        r'\[([0-9a-fA-F:]+)\]',  # [IPv6] format
        r'2409:8087:',           # Common IPv6 prefix in the logs
        r'2001:',                # Another common IPv6 prefix
        r'::1',                  # localhost IPv6
        r'fe80:',                # link-local IPv6
    ]
    
    for pattern in ipv6_patterns:
        if re.search(pattern, url):
            return True
    return False

def filter_ipv6_channels(channels):
    """Filter only IPv6 channels"""
    ipv6_channels = defaultdict(list)
    
    for category, channel_list in channels.items():
        for channel in channel_list:
            if is_ipv6_url(channel['url']):
                ipv6_channels[category].append(channel)
    
    return ipv6_channels

def save_channels_to_file(channels, file_path):
    """Save channels to file in the same format"""
    with open(file_path, 'w', encoding='utf-8') as f:
        first_category = True
        
        for category, channel_list in channels.items():
            if not channel_list:
                continue
                
            if not first_category:
                f.write('\n')
            first_category = False
            
            f.write(f'{category},#genre#\n')
            
            for channel in channel_list:
                f.write(f"{channel['name']},{channel['url']}\n")

def remove_duplicates_keep_best(channels):
    """Remove duplicate channels, keeping the best one for each channel name"""
    deduplicated = defaultdict(list)
    
    for category, channel_list in channels.items():
        seen_names = {}
        
        for channel in channel_list:
            name = channel['name']
            url = channel['url']
            
            if name not in seen_names:
                seen_names[name] = channel
            else:
                # Keep the shorter URL (usually better)
                existing_url = seen_names[name]['url']
                if len(url) < len(existing_url):
                    seen_names[name] = channel
        
        deduplicated[category] = list(seen_names.values())
    
    return deduplicated

def main():
    # File paths
    result_file = 'output/result.txt'
    ipv6_file = 'output/ipv6_channels.txt'
    
    print("Reading result file...")
    channels = read_result_file(result_file)
    
    if not channels:
        print("No channels found in result file")
        return
    
    print(f"Found {sum(len(ch) for ch in channels.values())} total channels across {len(channels)} categories")
    
    print("Filtering IPv6 channels...")
    ipv6_channels = filter_ipv6_channels(channels)
    
    if not ipv6_channels:
        print("No IPv6 channels found")
        return
    
    print(f"Found {sum(len(ch) for ch in ipv6_channels.values())} IPv6 channels")
    
    print("Removing duplicates...")
    final_channels = remove_duplicates_keep_best(ipv6_channels)
    
    print(f"After deduplication: {sum(len(ch) for ch in final_channels.values())} unique IPv6 channels")
    
    print(f"Saving IPv6 channels to {ipv6_file}...")
    save_channels_to_file(final_channels, ipv6_file)
    
    # Print summary
    print("\nSummary of IPv6 channels by category:")
    for category, channel_list in final_channels.items():
        if channel_list:
            print(f"  {category}: {len(channel_list)} channels")
    
    print(f"\nIPv6 channels saved to: {ipv6_file}")

if __name__ == "__main__":
    main() 