"""
Simple user name extraction from hostnames
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_user_name(hostname: str) -> Optional[str]:
    """
    Extract user name from hostname using common patterns
    
    Args:
        hostname: Hostname string
        
    Returns:
        Extracted user name or None
    """
    if not hostname:
        return None
    
    try:
        # Common patterns for user identification in hostnames
        patterns = [
            r'user-(\w+)',           # user-john
            r'(\w+)-pc',             # john-pc
            r'(\w+)\.local',          # john.local
            r'(\w+)-laptop',          # john-laptop
            r'(\w+)-desktop',         # john-desktop
            r'(\w+)-workstation',    # john-workstation
            r'(\w+)-mac',            # john-mac
            r'(\w+)-win',            # john-win
            r'(\w+)-ubuntu',          # john-ubuntu
            r'(\w+)-linux',          # john-linux
            r'(\w+)-server',         # john-server
            r'(\w+)-vm',             # john-vm
            r'(\w+)-host',           # john-host
            r'(\w+)-machine',        # john-machine
            r'(\w+)-device',         # john-device
            r'(\w+)-computer',       # john-computer
            r'(\w+)-notebook',       # john-notebook
            r'(\w+)-system',         # john-system
            r'(\w+)-node',           # john-node
            r'(\w+)-client',         # john-client
        ]
        
        for pattern in patterns:
            match = re.search(pattern, hostname.lower())
            if match:
                username = match.group(1)
                # Filter out common non-user words
                if username not in ['admin', 'user', 'pc', 'laptop', 'desktop', 'workstation', 
                                  'mac', 'win', 'ubuntu', 'linux', 'server', 'vm', 'host', 
                                  'machine', 'device', 'computer', 'notebook', 'system', 
                                  'node', 'client', 'test', 'demo', 'temp', 'tmp']:
                    return username.title()
        
        # If hostname looks like a name (starts with capital letter and is short)
        if (hostname[0].isupper() and 
            len(hostname.split('.')) == 1 and 
            len(hostname) <= 20 and
            not any(char.isdigit() for char in hostname)):
            return hostname
        
        # Try to extract from domain names (e.g., john.company.com -> john)
        domain_parts = hostname.split('.')
        if len(domain_parts) >= 2:
            first_part = domain_parts[0]
            if (first_part[0].isupper() and 
                len(first_part) <= 15 and
                not any(char.isdigit() for char in first_part) and
                first_part.lower() not in ['www', 'mail', 'ftp', 'admin', 'test', 'dev']):
                return first_part
        
    except Exception as e:
        logger.debug(f"Error extracting user from hostname {hostname}: {e}")
    
    return None


def get_display_name(hostname: str, ip: str) -> str:
    """
    Get display name for an IP/hostname combination
    
    Args:
        hostname: Hostname string
        ip: IP address string
        
    Returns:
        Display name (user name, hostname, or IP)
    """
    # Try to extract user name first
    user_name = extract_user_name(hostname)
    if user_name:
        return user_name
    
    # Fall back to hostname if available
    if hostname:
        return hostname
    
    # Last resort: use IP
    return ip
