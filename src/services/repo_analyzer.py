# src/services/repo_analyzer.py
"""
Repository Analyzer — 5 parallel analyzers for deep code analysis.
"""
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Optional
from src.models.schemas import *
from src.config.settings import settings


class RepoAnalyzer:
    def __init__(self):
        self.tutorial_fingerprints = self._load_tutorial_fingerprints()
    
    def _load_tutorial_fingerprints(self) -> dict:
        """Load known tutorial/template fingerprints."""
        return {
            "create-react-app": {
                "required_files": ["public/index.html", "src/App.js", "src/index.js", "package.json"],
                "package_patterns": ["react-scripts", "testing-library/react", "web-vitals"],
                "structure_hash": "cra_structure",
                "description": "Create React App boilerplate"
            },
            "nextjs-starter": {
                "required_files": ["pages/index.js", "package.json", "next.config.js"],
                "package_patterns": ["next", "next-auth"],
                "structure_hash": "nextjs_structure",
                "description": "Next.js starter template"
            },
            "django-tutorial": {
                "required_files": ["manage.py", "settings.py", "urls.py", "wsgi.py"],
                "package_patterns": ["django", "djangorestframework"],
                "structure_hash": "django_structure",
                "description": "Django project template"
            },
            "spring-boot-initializr": {
                "required_files": ["pom.xml", "src/main/java", "src/main/resources/application.properties"],
                "package_patterns": ["spring-boot-starter", "spring-boot-maven-plugin"],
                "structure_hash": "springboot_structure",
                "description": "Spring Boot Initializr template"
            },
            "express-generator": {
                "required_files": ["app.js", "bin/www", "package.json", "routes/index.js"],
                "package_patterns": ["express", "express-generator"],
                "structure_hash": "express_structure",
                "description": "Express.js generator template"
            },
            "vite-react": {
                "required_files": ["index.html", "src/main.jsx", "package.json", "vite.config.js"],
                "package_patterns": ["vite", "@vitejs/plugin-react"],
                "structure_hash": "vite_react_structure",
                "description": "Vite + React template"
            },
            "flutter-counter": {
                "required_files": ["pubspec.yaml", "lib/main.dart"],
                "package_patterns": ["flutter"],
                "structure_hash": "flutter_counter",
                "description": "Flutter default counter app"
            }
        }
    
    def analyze(self, repo_path: Path) -> RepoAnalysis:
        """Run all analyzers in parallel."""
        start_time = time.time()
        
        repo_id = f"{repo_path.parent.name}_{repo_path.name}"
        repo_name = repo_path.name
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                'authorship': executor.submit(self._analyze_authorship, repo_path),
                'evolution': executor.submit(self._analyze_evolution, repo_path),
                'tutorial_clone': executor.submit(self._detect_tutorial_clone, repo_path),
                'quality': executor.submit(self._assess_code_quality, repo_path),
                'skills': executor.submit(self._map_skills, repo_path),
            }
            
            results = {}
            for name, future in futures.items():
                try:
                    results[name] = future.result(timeout=60)
                except Exception as e:
                    print(f"Analyzer {name} failed: {e}")
                    results[name] = self._get_default_signal(name)
        
        analysis_duration = int((time.time() - start_time) * 1000)
        
        return RepoAnalysis(
            repo_id=repo_id,
            name=repo_name,
            owner=repo_path.parent.name,
            authorship=results['authorship'],
            evolution=results['evolution'],
            tutorial_clone=results['tutorial_clone'],
            quality=results['quality'],
            skill_evidence=results['skills'],
            analysis_duration_ms=analysis_duration
        )
    
    def _get_default_signal(self, name: str):
        """Return default signal for failed analyzer."""
        defaults = {
            'authorship': AuthorshipSignal(score=0.0, total_commits=0, candidate_commits=0, primary_author=False,
                                          commit_frequency_per_week=0.0, time_span_days=0, email_mapping={}),
            'evolution': EvolutionSignal(score=0.0, loc_growth_trend="unknown", complexity_trend="unknown",
                                       feature_commits=0, bugfix_commits=0, refactor_commits=0,
                                       first_commit_date=None, last_commit_date=None),
            'tutorial_clone': TutorialCloneSignal(score=0.0, is_clone=False, confidence=0.0),
            'quality': QualitySignal(score=0.0, has_tests=False, test_coverage_estimate=0.0, has_docs=False,
                                   doc_coverage=0.0, lint_score=0.0, type_hint_coverage=0.0, cyclomatic_complexity_avg=0.0),
            'skills': []
        }
        return defaults.get(name, [])
    
    # ============================================================
    # 1. AUTHORSHIP ANALYSIS
    # ============================================================
    def _analyze_authorship(self, repo_path: Path) -> AuthorshipSignal:
        """Analyze git commit history for authorship signals."""
        try:
            # Get commit log with author emails
            result = subprocess.run([
                "git", "-C", str(repo_path), "log",
                "--format=%ae|%an|%ad|%s",
                "--date=short",
                "--all"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return self._get_default_signal('authorship')
            
            lines = result.stdout.strip().split('\n')
            if not lines or not lines[0]:
                return self._get_default_signal('authorship')
            
            # Parse commits
            commits = []
            emails = set()
            for line in lines:
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    email, name, date, message = parts
                    commits.append({
                        'email': email.strip(),
                        'name': name.strip(),
                        'date': date.strip(),
                        'message': message.strip()
                    })
                    emails.add(email.strip())
            
            if not commits:
                return self._get_default_signal('authorship')
            
            total_commits = len(commits)
            
            # Find most frequent author (assume candidate)
            from collections import Counter
            email_counts = Counter(c['email'] for c in commits)
            primary_email, primary_count = email_counts.most_common(1)[0]
            
            # Check if candidate is primary author (>50% commits)
            primary_author = primary_count / total_commits > 0.5
            
            # Commit frequency
            dates = [c['date'] for c in commits if c['date']]
            if dates:
                from datetime import datetime
                date_objs = [datetime.strptime(d, '%Y-%m-%d') for d in dates]
                time_span = (max(date_objs) - min(date_objs)).days
                commit_frequency = (total_commits / max(time_span / 7, 1)) if time_span > 0 else total_commits
            else:
                time_span = 0
                commit_frequency = 0
            
            # Authorship score: primary author weight + commit count factor
            authorship_score = 0.0
            if primary_author:
                authorship_score += 0.6
            authorship_score += min(primary_count / 50, 0.4)  # Up to 0.4 for commit volume
            
            return AuthorshipSignal(
                score=min(authorship_score, 1.0),
                total_commits=total_commits,
                candidate_commits=primary_count,
                primary_author=primary_author,
                commit_frequency_per_week=commit_frequency,
                time_span_days=time_span,
                email_mapping={primary_email: "candidate"}
            )
            
        except Exception as e:
            print(f"Authorship analysis error: {e}")
            return self._get_default_signal('authorship')
    
    # ============================================================
    # 2. EVOLUTION ANALYSIS
    # ============================================================
    def _analyze_evolution(self, repo_path: Path) -> EvolutionSignal:
        """Analyze code evolution over time."""
        try:
            # Get numstat for LOC changes over time
            result = subprocess.run([
                "git", "-C", str(repo_path), "log",
                "--numstat",
                "--format=%H|%ad",
                "--date=short",
                "--all"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return self._get_default_signal('evolution')
            
            # Parse commits with stats
            commits = []
            current_hash = None
            current_date = None
            
            for line in result.stdout.strip().split('\n'):
                if '|' in line and not line.startswith(' '):
                    current_hash, current_date = line.split('|', 1)
                elif line.strip() and current_hash:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        try:
                            added = int(parts[0]) if parts[0] != '-' else 0
                            deleted = int(parts[1]) if parts[1] != '-' else 0
                            filepath = parts[2]
                            commits.append({
                                'hash': current_hash,
                                'date': current_date,
                                'added': added,
                                'deleted': deleted,
                                'file': filepath,
                                'net': added - deleted
                            })
                        except ValueError:
                            pass
            
            if not commits:
                return self._get_default_signal('evolution')
            
            # Analyze trends
            from datetime import datetime
            dates = [datetime.strptime(c['date'], '%Y-%m-%d') for c in commits if c['date']]
            
            total_added = sum(c['added'] for c in commits)
            total_deleted = sum(c['deleted'] for c in commits)
            net_loc = total_added - total_deleted
            
            # Simple trend detection
            if net_loc > total_added * 0.1:
                loc_trend = "increasing"
            elif net_loc < -total_added * 0.1:
                loc_trend = "decreasing"
            else:
                loc_trend = "stable"
            
            # Categorize commits by message
            feature_keywords = ['add', 'implement', 'create', 'new', 'feature']
            bugfix_keywords = ['fix', 'bug', 'patch', 'resolve', 'issue']
            refactor_keywords = ['refactor', 'clean', 'reorganize', 'restructure', 'improve']
            
            feature_commits = 0
            bugfix_commits = 0
            refactor_commits = 0
            
            for c in commits:
                msg = c.get('file', '').lower()  # Using file as proxy - in real app, get commit message
                if any(kw in msg for kw in feature_keywords):
                    feature_commits += 1
                elif any(kw in msg for kw in bugfix_keywords):
                    bugfix_commits += 1
                elif any(kw in msg for kw in refactor_keywords):
                    refactor_commits += 1
            
            # Evolution score based on sustained development
            time_span = (max(dates) - min(dates)).days if dates else 0
            evolution_score = 0.0
            if time_span > 30:
                evolution_score += 0.4
            if time_span > 90:
                evolution_score += 0.3
            if total_added > 1000:
                evolution_score += 0.3
            
            return EvolutionSignal(
                score=min(evolution_score, 1.0),
                loc_growth_trend=loc_trend,
                complexity_trend="increasing",  # Would need radon over time
                feature_commits=feature_commits,
                bugfix_commits=bugfix_commits,
                refactor_commits=refactor_commits,
                first_commit_date=min(dates) if dates else None,
                last_commit_date=max(dates) if dates else None
            )
            
        except Exception as e:
            print(f"Evolution analysis error: {e}")
            return self._get_default_signal('evolution')
    
    # ============================================================
    # 3. TUTORIAL CLONE DETECTION (CRITICAL)
    # ============================================================
    def _detect_tutorial_clone(self, repo_path: Path) -> TutorialCloneSignal:
        """Detect if repository is a tutorial clone."""
        try:
            matched_patterns = []
            max_confidence = 0.0
            detected_type = None
            
            # Check each fingerprint
            for template_name, fingerprint in self.tutorial_fingerprints.items():
                confidence = self._check_fingerprint(repo_path, fingerprint)
                if confidence > 0.3:
                    matched_patterns.append(f"{template_name} ({confidence:.0%})")
                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_type = template_name
            
            # Additional heuristics
            structure_score = self._check_structure_similarity(repo_path)
            commit_score = self._check_commit_pattern(repo_path)
            
            # Combined score
            combined_score = max(max_confidence, structure_score, commit_score)
            
            is_clone = combined_score >= settings.TUTORIAL_CLONE_THRESHOLD
            
            return TutorialCloneSignal(
                score=combined_score,
                is_clone=is_clone,
                clone_type=detected_type if is_clone else None,
                confidence=max_confidence if is_clone else 0.0,
                matched_patterns=matched_patterns,
                structure_similarity=structure_score,
                commit_pattern_suspicious=commit_score > 0.7
            )
            
        except Exception as e:
            print(f"Tutorial clone detection error: {e}")
            return self._get_default_signal('tutorial_clone')
    
    def _check_fingerprint(self, repo_path: Path, fingerprint: dict) -> float:
        """Check if repo matches a specific template fingerprint."""
        score = 0.0
        checks = 0
        
        # Check required files
        for req_file in fingerprint.get("required_files", []):
            checks += 1
            if (repo_path / req_file).exists():
                score += 1
        
        # Check package.json / requirements.txt patterns
        package_files = ["package.json", "requirements.txt", "pom.xml", "build.gradle", "pubspec.yaml"]
        for pkg_file in package_files:
            pkg_path = repo_path / pkg_file
            if pkg_path.exists():
                checks += 1
                content = pkg_path.read_text(errors='ignore')
                for pattern in fingerprint.get("package_patterns", []):
                    if pattern in content:
                        score += 1
                        break
        
        return score / max(checks, 1)
    
    def _check_structure_similarity(self, repo_path: Path) -> float:
        """Check directory structure similarity to common templates."""
        # Get top-level structure
        dirs = [d.name for d in repo_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        files = [f.name for f in repo_path.iterdir() if f.is_file()]
        
        # Common template structures
        template_structures = {
            "react": {"src", "public", "package.json"},
            "django": {"manage.py", "requirements.txt"},
            "spring": {"src", "pom.xml"},
            "node": {"package.json", "index.js"},
        }
        
        max_similarity = 0.0
        for template, expected in template_structures.items():
            found = sum(1 for e in expected if e in dirs or e in files)
            similarity = found / len(expected)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _check_commit_pattern(self, repo_path: Path) -> float:
        """Check if commit pattern suggests tutorial (single initial commit + few)."""
        try:
            result = subprocess.run([
                "git", "-C", str(repo_path), "log", "--oneline", "--all"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return 0.0
            
            commits = result.stdout.strip().split('\n')
            commit_count = len([c for c in commits if c.strip()])
            
            # Suspicious: very few commits, or first commit is "Initial commit" with many files
            if commit_count <= 3:
                return 0.8
            elif commit_count <= 5:
                return 0.5
            
            # Check first commit message
            if commits:
                first_commit = commits[-1].lower()
                if 'initial commit' in first_commit or 'first commit' in first_commit:
                    return 0.4
            
            return 0.0
            
        except Exception:
            return 0.0
    
    # ============================================================
    # 4. CODE QUALITY ASSESSMENT
    # ============================================================
    def _assess_code_quality(self, repo_path: Path) -> QualitySignal:
        """Assess code quality metrics."""
        try:
            has_tests = False
            has_docs = False
            test_files = 0
            total_files = 0
            
            # Find test files
            test_patterns = ['test_', '_test.py', '.test.', '.spec.', 'test/', 'tests/', '__tests__/']
            for pattern in test_patterns:
                if list(repo_path.rglob(pattern)):
                    has_tests = True
                    break
            
            # Find docs
            doc_patterns = ['README', 'readme', 'docs/', 'doc/', '*.md', '*.rst']
            for pattern in doc_patterns:
                if list(repo_path.rglob(pattern)):
                    has_docs = True
                    break
            
            # Count source files
            source_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.cs', '.go', '.rs', '.rb', '.php'}
            source_files = [f for f in repo_path.rglob('*') if f.suffix in source_extensions]
            total_files = len(source_files)
            
            # Run radon for cyclomatic complexity (Python only)
            complexity_avg = 0.0
            py_files = [f for f in source_files if f.suffix == '.py']
            if py_files:
                try:
                    result = subprocess.run([
                        "radon", "cc", str(repo_path), "-a", "-j"
                    ], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        import json
                        data = json.loads(result.stdout)
                        complexities = []
                        for file_data in data.values():
                            for item in file_data:
                                if isinstance(item, dict) and 'complexity' in item:
                                    complexities.append(item['complexity'])
                        if complexities:
                            complexity_avg = sum(complexities) / len(complexities)
                except:
                    pass
            
            # Estimate test coverage (heuristic)
            test_coverage = 0.0
            if has_tests:
                test_files = len(list(repo_path.rglob('test_*.py'))) + len(list(repo_path.rglob('*_test.py')))
                if total_files > 0:
                    test_coverage = min(test_files / max(total_files * 0.5, 1), 1.0)
            
            # Doc coverage (presence of docstrings in Python)
            doc_coverage = 0.0
            if py_files:
                try:
                    result = subprocess.run([
                        "radon", "raw", str(repo_path), "-j"
                    ], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        total_items = 0
                        documented = 0
                        for file_data in data.values():
                            for item in file_data:
                                if isinstance(item, dict):
                                    total_items += 1
                                    if item.get('docstring', False):
                                        documented += 1
                        if total_items > 0:
                            doc_coverage = documented / total_items
                except:
                    pass
            
            # Lint score (placeholder - would run ruff/eslint)
            lint_score = 0.7  # Default assumption
            
            # Type hint coverage (Python)
            type_hint_coverage = 0.0
            if py_files:
                try:
                    result = subprocess.run([
                        "python", "-m", "mypy", "--strict", "--namespace-packages", str(repo_path)
                    ], capture_output=True, text=True, timeout=60)
                    # Heuristic: no errors = good coverage
                    if result.returncode == 0:
                        type_hint_coverage = 0.8
                    else:
                        type_hint_coverage = 0.4
                except:
                    type_hint_coverage = 0.3
            
            # Overall quality score
            quality_score = 0.0
            if has_tests: quality_score += 0.3
            if has_docs: quality_score += 0.2
            if test_coverage > 0.5: quality_score += 0.2
            if doc_coverage > 0.5: quality_score += 0.1
            if complexity_avg < 10: quality_score += 0.1
            if lint_score > 0.7: quality_score += 0.1
            
            return QualitySignal(
                score=min(quality_score, 1.0),
                has_tests=has_tests,
                test_coverage_estimate=test_coverage,
                has_docs=has_docs,
                doc_coverage=doc_coverage,
                lint_score=lint_score,
                type_hint_coverage=type_hint_coverage,
                cyclomatic_complexity_avg=complexity_avg
            )
            
        except Exception as e:
            print(f"Quality assessment error: {e}")
            return self._get_default_signal('quality')
    
    # ============================================================
    # 5. SKILL MAPPING
    # ============================================================
    def _map_skills(self, repo_path: Path) -> List[SkillEvidence]:
        """Map repository code to skills with evidence."""
        skills = []
        
        # Language detection
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.jsx': 'React', '.tsx': 'React', '.vue': 'Vue',
            '.java': 'Java', '.kt': 'Kotlin', '.go': 'Go',
            '.rs': 'Rust', '.cpp': 'C++', '.cs': 'C#',
            '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift',
            '.dart': 'Dart'
        }
        
        # Framework/library detection patterns
        framework_patterns = {
            'FastAPI': ['fastapi', 'FastAPI'],
            'Django': ['django', 'Django'],
            'Flask': ['flask', 'Flask'],
            'React': ['react', 'useState', 'useEffect', 'jsx'],
            'Vue': ['vue', 'Vue', 'createApp'],
            'Express': ['express', 'Express'],
            'Spring Boot': ['spring-boot', 'SpringBoot', '@SpringBootApplication'],
            'PostgreSQL': ['postgresql', 'psycopg2', 'pg_'],
            'MongoDB': ['mongodb', 'pymongo', 'mongoose'],
            'Redis': ['redis', 'Redis'],
            'Docker': ['Dockerfile', 'docker-compose', 'FROM '],
            'Kubernetes': ['kubernetes', 'k8s', 'Deployment', 'Service'],
            'AWS': ['boto3', 'aws-sdk', 'AWS'],
            'Testing': ['pytest', 'jest', 'testing-library', 'unittest'],
            'CI/CD': ['github/workflows', '.gitlab-ci', 'Jenkinsfile', '.circleci'],
        }
        
        # Scan files for patterns
        skill_evidence = {}
        
        # First pass: detect languages
        for ext, lang in language_map.items():
            files = list(repo_path.rglob(f'*{ext}'))
            if files:
                if lang not in skill_evidence:
                    skill_evidence[lang] = {'files': [], 'type': 'language', 'details': []}
                skill_evidence[lang]['files'].extend([str(f.relative_to(repo_path)) for f in files[:5]])
        
        # Second pass: scan content for frameworks
        source_files = []
        for ext in language_map.keys():
            source_files.extend(repo_path.rglob(f'*{ext}'))
        
        # Also check config files
        config_files = list(repo_path.rglob('package.json')) + list(repo_path.rglob('requirements.txt')) + \
                       list(repo_path.rglob('pom.xml')) + list(repo_path.rglob('build.gradle')) + \
                       list(repo_path.rglob('Dockerfile')) + list(repo_path.rglob('docker-compose*')) + \
                       list(repo_path.rglob('*.yml')) + list(repo_path.rglob('*.yaml'))
        
        all_files = source_files + config_files
        
        for file_path in all_files[:50]:  # Limit files scanned
            try:
                content = file_path.read_text(errors='ignore').lower()
                rel_path = str(file_path.relative_to(repo_path))
                
                for skill, patterns in framework_patterns.items():
                    for pattern in patterns:
                        if pattern.lower() in content:
                            if skill not in skill_evidence:
                                skill_evidence[skill] = {'files': [], 'type': 'framework_usage', 'details': []}
                            if rel_path not in skill_evidence[skill]['files']:
                                skill_evidence[skill]['files'].append(rel_path)
                            skill_evidence[skill]['details'].append(f"Found '{pattern}' in {rel_path}")
                            break
            except:
                continue
        
        # Convert to SkillEvidence objects
        for skill, evidence in skill_evidence.items():
            files = evidence['files'][:10]
            confidence = min(0.5 + len(files) * 0.1, 0.95)
            
            skills.append(SkillEvidence(
                skill=skill,
                evidence_type=evidence['type'],
                confidence=confidence,
                files=files,
                details="; ".join(evidence['details'][:3])
            ))
        
        return skills