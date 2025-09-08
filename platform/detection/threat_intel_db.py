"""Threat Intelligence Database implementing RAG-based threat knowledge lookup.

This module provides unified access to structured threat intelligence from multiple
frameworks including MITRE ATT&CK, Cyber Kill Chain, and incident response methodologies.
"""

from __future__ import annotations

import os
import re
import time
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from loguru import logger

from detection.knowledge.loader import KnowledgeLoader

if TYPE_CHECKING:
    from app_core.schemas import DetectionAlert

# Cache configuration from environment (default OFF for non-regression)
CACHE_ENABLED = os.getenv("TI_CACHE_ENABLED", "0") == "1"
CACHE_TTL_SECONDS = int(os.getenv("TI_CACHE_TTL", "300"))  # 5 minutes default
CACHE_MAX_SIZE = int(os.getenv("TI_CACHE_MAX", "2048"))    # 2048 entries default

# Type for cache entries: (expires_at: float, payload: Any)
CacheEntry = tuple[float, Any]

# Global cache storage: OrderedDict for LRU behavior
_ti_cache: OrderedDict[tuple[str, str, int], CacheEntry] = OrderedDict()

T = TypeVar('T')


def _normalize_query(query: str) -> str:
    """Normalize query string for consistent cache keys."""
    return query.strip().lower()


def _ti_cache_clear() -> None:
    """Clear the threat intelligence cache (for testing/ops)."""
    global _ti_cache
    _ti_cache.clear()
    logger.debug("Threat intel cache cleared")


def _cache_get_or_set(key: tuple[str, str, int], compute_fn: Callable[[], T]) -> T:
    """Get from cache or compute and cache the result.
    
    Args:
        key: Cache key tuple (method, normalized_query, k)
        compute_fn: Function to compute result on cache miss
        
    Returns:
        Cached or computed result
    """
    if not CACHE_ENABLED:
        return compute_fn()
    
    global _ti_cache
    current_time = time.monotonic()
    
    # Prune expired entries from the front (oldest items)
    while _ti_cache:
        first_key, (expires_at, _) = next(iter(_ti_cache.items()))
        if expires_at <= current_time:
            del _ti_cache[first_key]
        else:
            break
    
    # Check for cache hit
    if key in _ti_cache:
        expires_at, payload = _ti_cache[key]
        if expires_at > current_time:
            # Cache hit - move to end (most recently used)
            del _ti_cache[key]
            _ti_cache[key] = (expires_at, payload)
            return payload
        else:
            # Expired entry - remove it
            del _ti_cache[key]
    
    # Cache miss - compute result
    result = compute_fn()
    
    # Store in cache with TTL
    expires_at = current_time + CACHE_TTL_SECONDS
    _ti_cache[key] = (expires_at, result)
    
    # Enforce max size (LRU eviction)
    while len(_ti_cache) > CACHE_MAX_SIZE:
        # Remove oldest (first) entry
        oldest_key = next(iter(_ti_cache))
        del _ti_cache[oldest_key]
    
    return result


class ThreatIntelDB:
    """Threat Intelligence Database with structured framework knowledge."""

    def __init__(self, knowledge_loader: KnowledgeLoader | None = None) -> None:
        """Initialize Threat Intelligence Database.

        Args:
            knowledge_loader: Optional KnowledgeLoader instance. If None, creates default.
        """
        self.loader = knowledge_loader or KnowledgeLoader()
        self._framework_cache: dict[str, dict[str, Any]] = {}
        self._tactics_cache: dict[str, list[str]] = {}
        self._techniques_cache: dict[str, list[str]] = {}
        
        logger.info("ThreatIntelDB initialized")

    def search(self, query: str, k: int = 10) -> list[dict[str, Any]]:
        """Search threat intelligence knowledge base.

        Args:
            query: Search query string
            k: Maximum number of results to return

        Returns:
            List of search results with metadata and provenance
        """
        # Create cache key with normalized query
        cache_key = ("search", _normalize_query(query), k)
        
        def _compute_search_results() -> list[dict[str, Any]]:
            """Compute search results (the original search logic)."""
            try:
                # Use the knowledge loader's search capability
                hits = self.loader.query_knowledge(query, limit=k)
                
                results = []
                for hit in hits:
                    result = {
                        "content": hit.content,
                        "source": hit.filename,
                        "section": hit.section,
                        "lines": hit.lines,
                        "confidence": hit.confidence,
                        "framework": self._identify_framework(hit.filename),
                    }
                    
                    # Add structured metadata if available
                    metadata = self._extract_metadata(hit.content, hit.filename)
                    if metadata:
                        result.update(metadata)
                        
                    results.append(result)
                    
                logger.debug(f"ThreatIntelDB search '{query}' returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"ThreatIntelDB search failed: {e}")
                return []
        
        # Use cache-aware lookup
        return _cache_get_or_set(cache_key, _compute_search_results)

    def tactics_for(self, tag: str) -> list[str]:
        """Get tactics associated with a tag or framework.

        Args:
            tag: Framework tag, technique ID, or search term

        Returns:
            List of relevant tactics
        """
        try:
            # Check cache first
            if tag in self._tactics_cache:
                return self._tactics_cache[tag]

            tactics = []
            
            # Search for tactics in different frameworks
            if tag.lower() in ["mitre", "attack", "mitre_attack"]:
                tactics = self._get_mitre_tactics()
            elif tag.lower() in ["kill_chain", "killchain", "lockheed"]:
                tactics = self._get_kill_chain_phases()
            elif tag.lower() in ["nist", "sans", "incident_response"]:
                tactics = self._get_incident_response_phases()
            else:
                # Search for the tag in content and extract relevant tactics
                search_results = self.search(f"tactics {tag}", k=5)
                tactics = self._extract_tactics_from_results(search_results)
            
            # Cache the results
            self._tactics_cache[tag] = tactics
            
            logger.debug(f"Found {len(tactics)} tactics for tag '{tag}'")
            return tactics
            
        except Exception as e:
            logger.error(f"Failed to get tactics for '{tag}': {e}")
            return []

    def techniques_for(self, tag: str) -> list[str]:
        """Get techniques associated with a tag or framework.

        Args:
            tag: Framework tag, tactic name, or search term

        Returns:
            List of relevant techniques
        """
        try:
            # Check cache first
            if tag in self._techniques_cache:
                return self._techniques_cache[tag]

            techniques = []
            
            # Search for techniques based on tag
            if tag.upper().startswith("T") and tag[1:].replace(".", "").isdigit():
                # This looks like a MITRE technique ID
                techniques = [tag.upper()]
            elif tag.lower() in ["mitre", "attack", "mitre_attack"]:
                techniques = self._get_mitre_techniques()
            else:
                # Search for the tag in content and extract relevant techniques
                search_results = self.search(f"techniques {tag}", k=10)
                techniques = self._extract_techniques_from_results(search_results)
            
            # Cache the results
            self._techniques_cache[tag] = techniques
            
            logger.debug(f"Found {len(techniques)} techniques for tag '{tag}'")
            return techniques
            
        except Exception as e:
            logger.error(f"Failed to get techniques for '{tag}': {e}")
            return []

    def enrich_alert(self, alert: DetectionAlert) -> DetectionAlert:
        """Enrich detection alert with threat intelligence context.

        Args:
            alert: Detection alert to enrich

        Returns:
            Enriched alert with additional threat intelligence metadata
        """
        try:
            # Create a copy of the alert to avoid modifying the original
            enriched_alert = alert.model_copy()
            
            # Search for relevant threat intelligence based on alert content
            search_queries = self._build_search_queries(alert)
            
            threat_intel = []
            for query in search_queries:
                results = self.search(query, k=3)
                threat_intel.extend(results)
            
            # Remove duplicates and limit results
            seen_sources = set()
            unique_intel = []
            for intel in threat_intel:
                source_key = f"{intel['source']}#{intel['section']}"
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    unique_intel.append(intel)
                if len(unique_intel) >= 5:  # Limit to top 5 results
                    break
            
            # Extract MITRE ATT&CK technique mappings
            techniques = self._extract_techniques_from_intel(unique_intel)
            
            # Add enrichment data to alert metadata
            if not hasattr(enriched_alert, 'metadata') or enriched_alert.metadata is None:
                enriched_alert.metadata = {}
                
            enriched_alert.metadata.update({
                "threat_intelligence": {
                    "frameworks_matched": list({intel["framework"] for intel in unique_intel}),
                    "techniques_mapped": techniques,
                    "sources_consulted": [
                        {
                            "source": intel["source"],
                            "section": intel["section"], 
                            "confidence": intel["confidence"]
                        }
                        for intel in unique_intel
                    ],
                    "enrichment_timestamp": "2025-09-02T00:36:00Z"
                }
            })
            
            logger.debug(f"Alert enriched with {len(unique_intel)} threat intel sources, {len(techniques)} techniques")
            return enriched_alert
            
        except Exception as e:
            logger.error(f"Failed to enrich alert: {e}")
            return alert

    def _identify_framework(self, filename: str) -> str:
        """Identify framework from filename."""
        filename_lower = filename.lower()
        
        if "mitre" in filename_lower or "attack" in filename_lower:
            return "MITRE_ATT&CK"
        elif "kill_chain" in filename_lower or "lockheed" in filename_lower:
            return "Cyber_Kill_Chain"  
        elif "crowdstrike" in filename_lower or "hunting" in filename_lower:
            return "Threat_Hunting"
        elif "nist" in filename_lower or "sans" in filename_lower:
            return "Incident_Response"
        else:
            return "Unknown"

    def _extract_metadata(self, content: str, filename: str) -> dict[str, Any]:
        """Extract structured metadata from content."""
        metadata = {}
        
        # Look for MITRE technique IDs
        technique_pattern = r'\bT\d{4}(?:\.\d{3})?\b'
        techniques = re.findall(technique_pattern, content)
        if techniques:
            metadata["mitre_techniques"] = list(set(techniques))
        
        # Look for tactic mentions
        tactic_keywords = [
            "reconnaissance", "initial access", "execution", "persistence", 
            "privilege escalation", "defense evasion", "credential access",
            "discovery", "collection", "command and control", "exfiltration", "impact"
        ]
        found_tactics = []
        content_lower = content.lower()
        for tactic in tactic_keywords:
            if tactic in content_lower:
                found_tactics.append(tactic.replace(" ", "_"))
        
        if found_tactics:
            metadata["tactics"] = found_tactics
            
        return metadata

    def _build_search_queries(self, alert: DetectionAlert) -> list[str]:
        """Build search queries based on alert properties."""
        queries = []
        
        # Base query on alert content
        if hasattr(alert, 'description') and alert.description:
            queries.append(alert.description[:100])  # Truncate long descriptions
            
        # Add queries based on alert type/severity
        if hasattr(alert, 'alert_type') and alert.alert_type:
            queries.append(f"{alert.alert_type} detection")
            
        # Add queries based on source information
        if hasattr(alert, 'source') and alert.source:
            queries.append(f"{alert.source} threat")
            
        # Default query if no specific content found
        if not queries:
            queries.append("threat detection incident response")
            
        return queries[:3]  # Limit to 3 queries to avoid overwhelming the search

    def _extract_techniques_from_intel(self, intel_results: list[dict[str, Any]]) -> list[str]:
        """Extract MITRE ATT&CK techniques from intelligence results."""
        techniques = []
        
        for intel in intel_results:
            # Check if techniques are already in metadata
            if "mitre_techniques" in intel:
                techniques.extend(intel["mitre_techniques"])
            else:
                # Extract from content
                technique_pattern = r'\bT\d{4}(?:\.\d{3})?\b'
                found_techniques = re.findall(technique_pattern, intel.get("content", ""))
                techniques.extend(found_techniques)
        
        return list(set(techniques))  # Remove duplicates

    def _get_mitre_tactics(self) -> list[str]:
        """Get MITRE ATT&CK tactics."""
        return [
            "reconnaissance", "resource_development", "initial_access", "execution",
            "persistence", "privilege_escalation", "defense_evasion", "credential_access",
            "discovery", "lateral_movement", "collection", "command_and_control",
            "exfiltration", "impact"
        ]

    def _get_kill_chain_phases(self) -> list[str]:
        """Get Cyber Kill Chain phases."""
        return [
            "reconnaissance", "weaponization", "delivery", "exploitation",
            "installation", "command_and_control", "actions_on_objectives"
        ]

    def _get_incident_response_phases(self) -> list[str]:
        """Get incident response phases."""
        return [
            "preparation", "identification", "containment", "eradication",
            "recovery", "lessons_learned"
        ]

    def _get_mitre_techniques(self) -> list[str]:
        """Get sample MITRE ATT&CK techniques."""
        return [
            "T1566", "T1078", "T1059", "T1106", "T1053", "T1547",
            "T1134", "T1068", "T1055", "T1027", "T1003", "T1110",
            "T1083", "T1057", "T1005", "T1113", "T1071", "T1573",
            "T1041", "T1048", "T1486", "T1490"
        ]

    def _extract_tactics_from_results(self, results: list[dict[str, Any]]) -> list[str]:
        """Extract tactics from search results."""
        tactics = []
        tactic_keywords = self._get_mitre_tactics()
        
        for result in results:
            content_lower = result.get("content", "").lower()
            for tactic in tactic_keywords:
                if tactic.replace("_", " ") in content_lower:
                    tactics.append(tactic)
                    
        return list(set(tactics))

    def _extract_techniques_from_results(self, results: list[dict[str, Any]]) -> list[str]:
        """Extract techniques from search results."""
        techniques = []
        
        for result in results:
            content = result.get("content", "")
            technique_pattern = r'\bT\d{4}(?:\.\d{3})?\b'
            found_techniques = re.findall(technique_pattern, content)
            techniques.extend(found_techniques)
            
        return list(set(techniques))


# Global instance (lazy initialization)
_threat_intel_db: ThreatIntelDB | None = None


def get_threat_intel_db() -> ThreatIntelDB:
    """Get global threat intelligence database instance.

    Returns:
        Global ThreatIntelDB instance.
    """
    global _threat_intel_db
    if _threat_intel_db is None:
        _threat_intel_db = ThreatIntelDB()
    return _threat_intel_db
