"""HATEOAS Hypermedia Utilities.

This module provides utilities for adding hypermedia links to API responses,
enabling self-describing APIs.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Link(BaseModel):
    """Hypermedia link following HAL-like structure."""
    
    href: str = Field(description="The URL of the linked resource")
    method: str = Field(default="GET", description="HTTP method for the link")
    title: Optional[str] = Field(default=None, description="Human-readable title")
    type: Optional[str] = Field(default=None, description="Media type of the resource")
    templated: bool = Field(default=False, description="Whether the href is a URI template")


class HypermediaLinks:
    """Builder for hypermedia links."""
    
    def __init__(self, base_url: str = "/api/v1"):
        self.base_url = base_url
        self._links: Dict[str, Link] = {}
    
    def add(
        self,
        rel: str,
        href: str,
        method: str = "GET",
        title: Optional[str] = None,
        templated: bool = False,
    ) -> "HypermediaLinks":
        """Add a link."""
        self._links[rel] = Link(
            href=f"{self.base_url}{href}" if not href.startswith("http") else href,
            method=method,
            title=title,
            templated=templated,
        )
        return self
    
    def self_link(self, href: str) -> "HypermediaLinks":
        """Add self link."""
        return self.add("self", href)
    
    def collection(self, href: str) -> "HypermediaLinks":
        """Add collection link."""
        return self.add("collection", href)
    
    def build(self) -> Dict[str, Dict[str, Any]]:
        """Build links dictionary."""
        return {
            rel: link.model_dump(exclude_none=True)
            for rel, link in self._links.items()
        }


def add_log_links(log_id: str) -> Dict[str, Dict[str, Any]]:
    """Generate hypermedia links for an event log."""
    return (
        HypermediaLinks()
        .self_link(f"/logs/{log_id}")
        .add("variants", f"/logs/{log_id}/variants", title="View Variants")
        .add("statistics", f"/logs/{log_id}/statistics", title="View Statistics")
        .add("quality", f"/logs/{log_id}/quality", title="Quality Report")
        .add("discover", "/discovery/discover", method="POST", title="Discover Process Model")
        .add("update", f"/logs/{log_id}", method="PATCH", title="Update Log")
        .add("delete", f"/logs/{log_id}", method="DELETE", title="Delete Log")
        .collection("/logs")
        .build()
    )


def add_model_links(model_id: str, log_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Generate hypermedia links for a process model."""
    links = (
        HypermediaLinks()
        .self_link(f"/models/{model_id}")
        .add("visualize", f"/models/{model_id}/visualize", title="Visualize Model", type="image/svg+xml")
        .add("petri-net", f"/discovery/petri-net/{model_id}", title="Petri Net Structure")
        .add("process-tree", f"/discovery/process-tree/{model_id}", title="Process Tree")
        .add("update", f"/models/{model_id}", method="PATCH", title="Update Model")
        .add("delete", f"/models/{model_id}", method="DELETE", title="Delete Model")
        .collection("/models")
    )
    
    if log_id:
        links.add("conformance", "/conformance/check", method="POST", title="Check Conformance")
        links.add("quality", f"/discovery/model/{model_id}/quality?log_id={log_id}", title="Quality Metrics")
    
    return links.build()


def add_pagination_links(
    base_path: str,
    page: int,
    page_size: int,
    total_pages: int,
) -> Dict[str, Dict[str, Any]]:
    """Generate pagination links."""
    links = HypermediaLinks()
    
    links.self_link(f"{base_path}?page={page}&page_size={page_size}")
    links.add("first", f"{base_path}?page=1&page_size={page_size}")
    links.add("last", f"{base_path}?page={total_pages}&page_size={page_size}")
    
    if page > 1:
        links.add("prev", f"{base_path}?page={page - 1}&page_size={page_size}")
    if page < total_pages:
        links.add("next", f"{base_path}?page={page + 1}&page_size={page_size}")
    
    return links.build()
