# src/services/github_fetcher.py
"""
GitHub Fetcher — Fetch public repos, download repos for analysis, caching.
"""
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional
from github import BadCredentialsException, Github, RateLimitExceededException
from github.Repository import Repository
from src.config.settings import settings
from src.models.schemas import RepoSummary, RepoTree


class GitHubFetcher:
    def __init__(self, token: str, cache_dir: Path):
        self.token = token.strip() if token else ""
        if self.token and not self.token.lower().endswith("placeholder"):
            self.client = Github(self.token)
        else:
            self.client = Github()
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache subdirectories
        self.repo_cache_dir = cache_dir / "repos"
        self.meta_cache_dir = cache_dir / "meta"
        self.repo_cache_dir.mkdir(exist_ok=True)
        self.meta_cache_dir.mkdir(exist_ok=True)
    
    def get_user_repos(self, username: str, force_refresh: bool = False) -> List[RepoSummary]:
        """Fetch all public repositories for a user."""
        cache_file = self.meta_cache_dir / f"{username}_repos.json"
        
        # Check cache (24h TTL)
        if not force_refresh and cache_file.exists():
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < 86400:  # 24 hours
                import json
                with open(cache_file) as f:
                    cached = json.load(f)
                return [RepoSummary(**r) for r in cached]
        
        try:
            user = self.client.get_user(username)
            repos = []
            
            for repo in user.get_repos():
                if repo.fork or repo.archived:
                    continue  # Skip forks and archived by default
                
                repos.append(RepoSummary(
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description,
                    stars=repo.stargazers_count,
                    language=repo.language,
                    updated_at=repo.updated_at,
                    is_fork=repo.fork,
                    is_archived=repo.archived,
                    html_url=repo.html_url
                ))
            
            # Cache results
            import json
            with open(cache_file, 'w') as f:
                json.dump([r.model_dump() for r in repos], f, default=str)
            
            return repos
            
        except BadCredentialsException:
            if not self.token:
                raise
            # An expired/placeholder token should not prevent public repos
            # from loading; retry through GitHub's unauthenticated API.
            self.client = Github()
            try:
                return self.get_user_repos(username, force_refresh=True)
            except RateLimitExceededException:
                raise
        except RateLimitExceededException:
            # Return stale cache if available
            if cache_file.exists():
                import json
                with open(cache_file) as f:
                    cached = json.load(f)
                return [RepoSummary(**r) for r in cached]
            raise
        except Exception as e:
            raise Exception(f"Failed to fetch repos for {username}: {str(e)}")
    
    def get_repo_tree(self, owner: str, repo_name: str) -> RepoTree:
        """Get file tree of repository without full clone."""
        repo = self.client.get_repo(f"{owner}/{repo_name}")
        
        files = []
        languages = {}
        
        def traverse_contents(contents, path=""):
            for content in contents:
                full_path = f"{path}/{content.name}" if path else content.name
                if content.type == "dir":
                    traverse_contents(repo.get_contents(full_path), full_path)
                else:
                    files.append(full_path)
                    # Track language by extension
                    ext = Path(content.name).suffix.lower()
                    if ext:
                        languages[ext] = languages.get(ext, 0) + content.size or 0
        
        try:
            traverse_contents(repo.get_contents(""))
        except:
            pass  # Handle empty repos or permission issues
        
        total_size = sum(languages.values()) if languages else 0
        
        return RepoTree(
            files=files,
            total_size_bytes=total_size,
            languages=languages
        )
    
    def download_repo(self, owner: str, repo_name: str, force_refresh: bool = False) -> Path:
        """Clone repository for analysis (shallow clone)."""
        repo_dir = self.repo_cache_dir / f"{owner}_{repo_name}"
        
        if not force_refresh and repo_dir.exists():
            # Check if repo is recent (7 days)
            if time.time() - repo_dir.stat().st_mtime < 604800:
                return repo_dir
            else:
                shutil.rmtree(repo_dir)
        
        # Shallow clone with git
        import subprocess
        clone_url = f"https://github.com/{owner}/{repo_name}.git"
        
        try:
            result = subprocess.run([
                "git", "clone", 
                "--depth", "1",
                "--filter=blob:none",
                "--sparse",
                clone_url,
                str(repo_dir)
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                # Fallback: try without sparse
                if repo_dir.exists():
                    shutil.rmtree(repo_dir)
                result = subprocess.run([
                    "git", "clone", 
                    "--depth", "1",
                    clone_url,
                    str(repo_dir)
                ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            # Update timestamp
            repo_dir.touch()
            
            return repo_dir
            
        except subprocess.TimeoutExpired:
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            raise Exception(f"Clone timeout for {owner}/{repo_name}")
        except Exception as e:
            if repo_dir.exists():
                shutil.rmtree(repo_dir)
            raise
    
    def check_rate_limit(self) -> dict:
        """Check current GitHub API rate limit."""
        rate_limit = self.client.get_rate_limit()
        return {
            "limit": rate_limit.core.limit,
            "remaining": rate_limit.core.remaining,
            "reset_at": rate_limit.core.reset.timestamp() if rate_limit.core.reset else None,
            "used": rate_limit.core.used
        }
    
    def wait_for_rate_limit(self):
        """Wait if rate limit is low."""
        limit_info = self.check_rate_limit()
        if limit_info["remaining"] < 100:
            reset_time = limit_info["reset_at"]
            if reset_time:
                wait_time = max(0, reset_time - time.time() + 10)
                if wait_time > 0:
                    print(f"Rate limit low ({limit_info['remaining']} remaining). Waiting {wait_time:.0f}s...")
                    time.sleep(min(wait_time, 300))  # Max 5 min wait