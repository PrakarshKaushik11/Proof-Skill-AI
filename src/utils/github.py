# src/utils/github.py
"""
GitHub Utilities — Helper functions for GitHub API interactions.
"""
import re
from typing import List, Optional, Dict
from urllib.parse import urlparse
from src.config.settings import settings


def parse_github_url(url: str) -> Optional[Dict[str, str]]:
    """Parse GitHub URL to extract owner, repo, and type."""
    # Patterns for different GitHub URL formats
    patterns = [
        # Profile: github.com/username
        (r'github\.com/([\w\-]+)/?$', 'profile'),
        # Repo: github.com/owner/repo
        (r'github\.com/([\w\-]+)/([\w\-\.]+)/?$', 'repo'),
        # Repo with .git
        (r'github\.com/([\w\-]+)/([\w\-\.]+)\.git$', 'repo'),
        # With protocol
        (r'https?://github\.com/([\w\-]+)/?$', 'profile'),
        (r'https?://github\.com/([\w\-]+)/([\w\-\.]+)/?$', 'repo'),
    ]
    
    for pattern, url_type in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            groups = match.groups()
            if url_type == 'profile':
                return {"type": "profile", "owner": groups[0], "repo": None}
            else:
                return {"type": "repo", "owner": groups[0], "repo": groups[1]}
    
    return None


def extract_github_urls(text: str) -> List[str]:
    """Extract all GitHub URLs from text."""
    # Comprehensive pattern for GitHub URLs
    pattern = r'https?://github\.com/[\w\-\./]+'
    urls = re.findall(pattern, text, re.IGNORECASE)
    
    # Also catch bare github.com/... patterns
    bare_pattern = r'github\.com/[\w\-\./]+'
    bare_urls = re.findall(bare_pattern, text, re.IGNORECASE)
    
    # Combine and normalize
    all_urls = urls + [f"https://{u}" for u in bare_urls]
    
    # Deduplicate
    seen = set()
    unique = []
    for url in all_urls:
        normalized = url.rstrip('/').rstrip('.git')
        if normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    
    return unique


def get_repo_language_stats(languages: Dict[str, int]) -> Dict[str, float]:
    """Convert language byte counts to percentages."""
    total = sum(languages.values())
    if total == 0:
        return {}
    return {lang: (bytes / total) * 100 for lang, bytes in languages.items()}


def is_likely_fork(repo_name: str, owner: str, candidate_username: str) -> bool:
    """Heuristic to check if repo is likely a fork of candidate's own work."""
    return owner.lower() != candidate_username.lower()


def estimate_repo_complexity(file_count: int, total_lines: int, languages: Dict) -> str:
    """Estimate repository complexity."""
    score = 0
    
    # File count factor
    if file_count > 50:
        score += 3
    elif file_count > 20:
        score += 2
    elif file_count > 5:
        score += 1
    
    # Lines of code factor
    if total_lines > 10000:
        score += 3
    elif total_lines > 3000:
        score += 2
    elif total_lines > 500:
        score += 1
    
    # Language diversity
    if len(languages) > 5:
        score += 2
    elif len(languages) > 2:
        score += 1
    
    if score >= 7:
        return "high"
    elif score >= 4:
        return "medium"
    return "low"


def get_default_branch(repo) -> str:
    """Get default branch name (main/master)."""
    try:
        return repo.default_branch
    except:
        return "main"


def format_repo_url(owner: str, repo: str) -> str:
    """Format repository URL."""
    return f"https://github.com/{owner}/{repo}"


def format_profile_url(username: str) -> str:
    """Format profile URL."""
    return f"https://github.com/{username}"


def sanitize_repo_name(name: str) -> str:
    """Sanitize repository name for filesystem."""
    return re.sub(r'[^\w\-_.]', '_', name)


def get_file_extension_category(filename: str) -> str:
    """Categorize file by extension."""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    categories = {
        'source': ['py', 'js', 'ts', 'jsx', 'tsx', 'java', 'kt', 'go', 'rs', 'cpp', 'cc', 'cxx', 'c', 'h', 'hpp', 'cs', 'rb', 'php', 'swift', 'dart', 'scala', 'clj', 'hs', 'ml', 'fs'],
        'config': ['json', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'conf', 'config', 'env', 'properties'],
        'docs': ['md', 'rst', 'txt', 'adoc', 'tex'],
        'test': ['test.py', 'spec.js', 'spec.ts', '_test.py', 'test_.py', 'spec.py'],
        'build': ['gradle', 'maven', 'pom.xml', 'build.gradle', 'package.json', 'requirements.txt', 'setup.py', 'cargo.toml', 'go.mod'],
        'docker': ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
        'ci': ['yml', 'yaml']  # In .github/workflows, .gitlab-ci, etc.
    }
    
    for cat, exts in categories.items():
        if ext in exts or any(filename.endswith(e) for e in exts):
            return cat
    
    return 'other'


def is_config_file(filename: str) -> bool:
    """Check if file is a configuration file."""
    config_patterns = [
        'package.json', 'requirements.txt', 'setup.py', 'pyproject.toml',
        'pom.xml', 'build.gradle', 'Cargo.toml', 'go.mod',
        'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        '.github/workflows/', '.gitlab-ci.yml', '.circleci/config.yml',
        'tsconfig.json', 'webpack.config.js', 'vite.config.js',
        'jest.config.js', 'pytest.ini', 'tox.ini', 'mypy.ini',
        '.eslintrc', '.prettierrc', '.editorconfig'
    ]
    
    filename_lower = filename.lower()
    return any(pattern in filename_lower for pattern in config_patterns)


def is_test_file(filename: str) -> bool:
    """Check if file is a test file."""
    test_patterns = [
        'test_', '_test.', '.test.', '.spec.', '__test__',
        '/test/', '/tests/', '/__tests__/', '/spec/'
    ]
    
    filename_lower = filename.lower()
    return any(pattern in filename_lower for pattern in test_patterns)


def is_generated_file(filename: str) -> bool:
    """Check if file is likely generated/auto-generated."""
    generated_patterns = [
        'generated', 'auto-generated', 'codegen', '.pb.go', '.pb.py',
        '.g.dart', '.generated.', 'migrations/', 'dist/', 'build/',
        'node_modules/', '__pycache__/', '.venv/', 'venv/', 'target/',
        'vendor/', '.min.js', '.min.css', 'bundle.', 'compiled.'
    ]
    
    filename_lower = filename.lower()
    return any(pattern in filename_lower for pattern in generated_patterns)