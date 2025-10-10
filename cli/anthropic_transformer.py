#!/usr/bin/env python3

def transform_anthropic_to_gateway(anthropic_response, base_port=8100):
    """Transform Anthropic ServerResponse to Gateway Registry Config format."""
    
    server = anthropic_response.get("server", anthropic_response)
    name = server["name"]
    
    # Generate tags from name parts + anthropic-registry
    name_parts = name.replace("/", "-").split("-")
    tags = name_parts + ["anthropic-registry"]
    
    # Handle packages (can be array or object)
    packages = server.get("packages", {})
    is_python = False
    npm_pkg = None
    
    if isinstance(packages, dict):
        npm_pkg = packages.get("npm")
        is_python = "pypi" in packages or "python" in packages
    elif isinstance(packages, list):
        is_python = any(pkg.get("registryType") == "pypi" for pkg in packages)
        npm_pkg = next((pkg["identifier"] for pkg in packages 
                       if pkg.get("registryType") == "npm"), None)
    
    # Generate safe path
    safe_path = name.replace("/", "-")
    
    return {
        "server_name": name,
        "description": server.get("description", "MCP server imported from Anthropic Registry"),
        "path": f"/{safe_path}",
        "proxy_pass_url": f"http://localhost:{base_port}/",
        "auth_provider": "keycloak",
        "auth_type": "oauth", 
        "supported_transports": ["stdio"],
        "tags": tags,
        "headers": [],
        "num_tools": 0,
        "num_stars": 0,
        "is_python": is_python,
        "license": "MIT",
        "repository_url": server.get("repository", {}).get("url", ""),
        "website_url": server.get("websiteUrl", ""),
        "package_npm": npm_pkg,
        "tool_list": []
    }

if __name__ == "__main__":
    import json
    import sys
    
    # Example usage
    example_input = {
        "name": "brave-search",
        "description": "MCP server for Brave Search API", 
        "version": "0.1.0",
        "repository": {
            "type": "github",
            "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
        },
        "websiteUrl": "https://brave.com/search/api/",
        "packages": {
            "npm": "@modelcontextprotocol/server-brave-search"
        }
    }
    
    # Transform and output
    result = transform_anthropic_to_gateway(example_input)
    print(json.dumps(result, indent=2))
