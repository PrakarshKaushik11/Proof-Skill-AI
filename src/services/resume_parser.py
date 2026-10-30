# src/services/resume_parser.py
"""
Resume Parser — PDF/DOCX parsing, skill/project/GitHub extraction, normalization.
"""
import re
import json
from pathlib import Path
from typing import List, Optional
import pdfplumber
from docx import Document
import spacy
from src.models.schemas import *
from src.config.settings import settings


class ResumeParser:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load skill taxonomy
        self.skill_taxonomy = self._load_skill_taxonomy()
        
        # Common skill keywords for fallback extraction
        self.skill_keywords = self._build_skill_keywords()
    
    def _load_skill_taxonomy(self) -> dict:
        """Load canonical skill taxonomy."""
        taxonomy_path = Path("data/skill_taxonomy.json")
        if taxonomy_path.exists():
            with open(taxonomy_path) as f:
                return json.load(f)
        # Default fallback taxonomy
        return {
            "languages": ["Python", "Java", "JavaScript", "TypeScript", "HTML5", "CSS3", "C++", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin"],
            "frameworks": ["Django", "Flask", "FastAPI", "Spring Boot", "React", "Vue", "Angular", "Next.js", "Express", "Node.js"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "Elasticsearch", "Cassandra"],
            "tools": ["Git", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD", "Jenkins", "GitHub Actions"],
            "concepts": ["REST API", "GraphQL", "Microservices", "OOP", "Design Patterns", "Testing", "Agile", "HTML5 Canvas API", "Game Loop Design", "Browser Game Mechanics", "Cybersecurity"]
        }
    
    def _build_skill_keywords(self) -> dict:
        """Build flat keyword -> canonical skill mapping."""
        mapping = {}
        for category, skills in self.skill_taxonomy.items():
            for skill in skills:
                mapping[skill.lower()] = skill
                # Add common variations
                mapping[skill.lower().replace(" ", "")] = skill
                mapping[skill.lower().replace(".", "")] = skill
                mapping[skill.lower().replace("-", "")] = skill
                if skill.lower() == "react":
                    mapping["react.js"] = skill
        return mapping

    @staticmethod
    def _skill_key(name: str) -> str:
        """Normalize punctuation and whitespace for taxonomy lookup."""
        return re.sub(r"[^a-z0-9]", "", name.lower())
    
    def parse(self, file_path: Path) -> ParsedResume:
        """Parse resume file (PDF or DOCX) into structured data."""
        if file_path.suffix.lower() == ".pdf":
            raw_text = self._extract_pdf(file_path)
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            raw_text = self._extract_docx(file_path)
        elif file_path.suffix.lower() in [".txt", ".md"]:
            raw_text = file_path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Extract structured information
        skills = self.extract_skills(raw_text)
        projects = self.extract_projects(raw_text)
        github_urls = self.extract_github_urls(raw_text)
        education = self.extract_education(raw_text)
        experience = self.extract_experience(raw_text)
        
        return ParsedResume(
            raw_text=raw_text,
            skills=skills,
            projects=projects,
            github_urls=github_urls,
            education=education,
            experience=experience
        )
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using pdfplumber."""
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX."""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def extract_skills(self, text: str) -> List[SkillClaim]:
        """Extract skills from resume text."""
        skills = []
        text_lower = text.lower()
        
        # Keyword-based extraction
        found_skills = set()
        for keyword, canonical in self.skill_keywords.items():
            if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text_lower):
                found_skills.add(canonical)
        
        # spaCy NER for additional entities (ORG, PRODUCT might catch tech names)
        doc = self.nlp(text[:10000])  # Limit for performance
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
                ent_lower = ent.text.lower()
                if ent_lower in self.skill_keywords:
                    found_skills.add(self.skill_keywords[ent_lower])
        
        # Convert to SkillClaim objects
        for skill in sorted(found_skills):
            # Infer level from context
            level = self._infer_skill_level(text, skill)
            skills.append(SkillClaim(
                name=skill,
                level=level,
                source=EvidenceSource.RESUME,
                confidence=0.0  # Will be computed later
            ))
        
        return skills
    
    def _infer_skill_level(self, text: str, skill: str) -> SkillLevel:
        """Infer skill level from resume context."""
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Look for level indicators near skill mentions
        patterns = {
            SkillLevel.ADVANCED: [
                rf"expert.*{skill_lower}", rf"{skill_lower}.*expert",
                rf"advanced.*{skill_lower}", rf"{skill_lower}.*advanced",
                rf"proficient.*{skill_lower}", rf"{skill_lower}.*proficient",
                rf"deep.*{skill_lower}", rf"{skill_lower}.*deep"
            ],
            SkillLevel.INTERMEDIATE: [
                rf"experience.*{skill_lower}", rf"{skill_lower}.*experience",
                rf"working.*{skill_lower}", rf"{skill_lower}.*working",
                rf"familiar.*{skill_lower}", rf"{skill_lower}.*familiar",
                rf"knowledge.*{skill_lower}", rf"{skill_lower}.*knowledge"
            ],
            SkillLevel.BEGINNER: [
                rf"learning.*{skill_lower}", rf"{skill_lower}.*learning",
                rf"beginner.*{skill_lower}", rf"{skill_lower}.*beginner",
                rf"basic.*{skill_lower}", rf"{skill_lower}.*basic"
            ]
        }
        
        for level, level_patterns in patterns.items():
            for pattern in level_patterns:
                if re.search(pattern, text_lower):
                    return level
        
        return SkillLevel.BEGINNER  # Default
    
    def extract_projects(self, text: str) -> List[ProjectClaim]:
        """Extract project information from resume."""
        project_text = self._extract_section(
            text,
            r"(?:projects?|featured\s+github\s+projects?|personal\s+projects?|"
            r"academic\s+projects?|key\s+projects?)",
        )
        if not project_text:
            return []

        description_starts = (
            "built ", "implemented ", "engineered ", "contributed ", "managed ",
            "maintained ", "developed ", "created ", "designed ", "worked ",
        )
        blocks = []
        current = []
        for line in (line.strip() for line in project_text.splitlines()):
            if not line:
                continue
            is_bullet = bool(re.match(r"^[•\-*]\s*", line))
            line = re.sub(r"^[•\-*]\s*", "", line)
            starts_new_heading = is_bullet or (
                not line.lower().startswith(description_starts)
                and not line.endswith((".", "!", "?", ",", ";", ":"))
            )
            if current and starts_new_heading:
                blocks.append(current)
                current = []
            current.append(line)
        if current:
            blocks.append(current)

        projects = []
        for block in blocks[:10]:
            if not block:
                continue
            combined = " ".join(block)
            if len(block) == 1 and ":" in block[0]:
                name, description = block[0].split(":", 1)
            else:
                name, description = block[0], " ".join(block[1:])
            projects.append(ProjectClaim(
                name=name.strip()[:100],
                description=description.strip()[:500] or name.strip(),
                tech_stack=self._extract_tech_from_text(combined),
                github_url=self._extract_project_github_url(combined),
            ))
        return projects

    @staticmethod
    def _extract_section(text: str, heading_pattern: str) -> str:
        """Return text between a section heading and the next uppercase heading."""
        match = re.search(
            rf"^\s*(?i:{heading_pattern})\s*:?\s*$([\s\S]*?)"
            r"(?=^\s*[A-Z][A-Z &/]+(?:\n|$)|\Z)",
            text, flags=re.MULTILINE,
        )
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_project_github_url(text: str) -> Optional[HttpUrl]:
        match = re.search(r"(?:https?://)?github\.com/[\w.-]+/[\w.-]+", text, re.IGNORECASE)
        if not match:
            match = re.search(r"(?<!\w)([\w.-]+/[\w.-]+)(?!\w)", text)
        if not match:
            return None
        try:
            value = match.group(0)
            if not value.startswith("http"):
                value = "https://github.com/" + value
            return HttpUrl(value)
        except ValueError:
            return None
    
    def _extract_tech_from_text(self, text: str) -> List[str]:
        """Extract technology mentions from text."""
        tech = []
        text_lower = text.lower()
        for keyword, canonical in self.skill_keywords.items():
            if re.search(rf"(?<!\w){re.escape(keyword)}(?!\w)", text_lower) and canonical not in tech:
                tech.append(canonical)
        return tech[:10]  # Limit
    
    def extract_github_urls(self, text: str) -> List[HttpUrl]:
        """Extract GitHub URLs from resume text."""
        # Pattern for GitHub profile and repo URLs
        patterns = [
            r'https?://github\.com/[\w\-\.]+(?:/[\w\-\.]+)?',
            r'(?<![\w@])github\.com/[\w\-\.]+(?:/[\w\-\.]+)?',
            r'(?<![\w])@[\w\-]+',
        ]

        urls = []
        labeled_username = re.search(
            r'\bgithub\s*:\s*@?([A-Za-z0-9][A-Za-z0-9-]{0,38})\b',
            text,
            re.IGNORECASE,
        )
        if labeled_username:
            patterns.append(
                rf'(?<![\w-]){re.escape(labeled_username.group(1))}(?![\w-])'
            )

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.startswith("@"):
                    match = "https://github.com/" + match[1:]
                elif not match.lower().startswith(("http://", "https://", "github.com/")):
                    match = "https://github.com/" + match
                if not match.startswith('http'):
                    match = 'https://' + match
                try:
                    urls.append(HttpUrl(match))
                except:
                    pass
        
        # Deduplicate
        unique_urls = []
        seen = set()
        for url in urls:
            if str(url) not in seen:
                seen.add(str(url))
                unique_urls.append(url)
        
        return unique_urls
    
    def extract_education(self, text: str) -> List[Education]:
        """Extract education information."""
        education = []
        edu_text = self._extract_section(
            text, r"education(?:\s*&\s*community)?|academic|qualification"
        )
        direct_match = re.search(
            r"(?P<degree>.+?)\s+(?P<year>20\d{2})\s*[–-]\s*(?:present|20\d{2})\s*\n"
            r"(?P<college>[^\n]+)",
            edu_text,
            flags=re.IGNORECASE,
        )
        if direct_match:
            return [Education(
                degree=direct_match.group("degree").strip(),
                college=direct_match.group("college").strip(),
                year=int(direct_match.group("year")),
            )]
        
        # Common degree patterns
        degree_patterns = [
            r'(B\.?Tech|B\.?E|Bachelor of (?:Technology|Engineering|Science))\s+(?:in\s+)?([^\n,]+)',
            r'(M\.?Tech|M\.?E|Master of (?:Technology|Engineering|Science))\s+(?:in\s+)?([^\n,]+)',
            r'(B\.?Sc|Bachelor of Science)\s+(?:in\s+)?([^\n,]+)',
            r'(M\.?Sc|Master of Science)\s+(?:in\s+)?([^\n,]+)',
            r'(Ph\.?D|Doctor of Philosophy)\s+(?:in\s+)?([^\n,]+)',
        ]
        
        # College patterns
        college_patterns = [
            r'(?:from|at|,)\s+([A-Z][a-zA-Z\s&]+(?:University|Institute|College|IIT|NIT|IIIT))',
        ]
        
        # Year patterns
        year_pattern = r'(20\d{2})'
        
        # Simple extraction - look for education section
        edu_section = re.split(
            r'\n\s*(?:education|academic|qualification)(?:\s*&\s*community)?\s*\n',
            text, flags=re.IGNORECASE
        )
        
        if len(edu_section) > 1:
            edu_text = edu_section[1][:2000]
            
            # Find degrees
            for pattern in degree_patterns:
                matches = re.findall(pattern, edu_text, re.IGNORECASE)
                for match in matches:
                    degree = match[0] if isinstance(match, tuple) else match
                    field = match[1] if isinstance(match, tuple) and len(match) > 1 else ""
                    
                    # Find nearby college
                    college = "Unknown"
                    for cp in college_patterns:
                        c_match = re.search(cp, edu_text, re.IGNORECASE)
                        if c_match:
                            college = c_match.group(1).strip()
                            break
                    
                    # Find year
                    year_match = re.search(year_pattern, edu_text)
                    year = int(year_match.group(1)) if year_match else 2024
                    
                    education.append(Education(
                        degree=degree.strip(),
                        college=college,
                        year=year
                    ))
        
        return education[:5]  # Limit
    
    def extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience."""
        experience = []
        
        # Look for experience section
        exp_section = re.split(
            r'\n\s*(?:experience|work|employment|internship)\s*\n',
            text, flags=re.IGNORECASE
        )
        
        if len(exp_section) > 1:
            exp_text = exp_section[1][:3000]
            
            # Split by potential job entries
            # This is heuristic - real implementation would be more sophisticated
            entries = re.split(r'\n\s*\n', exp_text)
            
            for entry in entries[:5]:
                entry = entry.strip()
                if len(entry) < 50:
                    continue
                
                lines = entry.split('\n')
                role = lines[0] if lines else "Unknown Role"
                
                # Try to extract company
                company = "Unknown"
                for line in lines[1:3]:
                    if any(kw in line.lower() for kw in ['at', '@', '|', '-']):
                        parts = re.split(r'\s+(?:at|@|\|)\s+', line)
                        if len(parts) > 1:
                            company = parts[1].split(',')[0].split('-')[0].strip()
                            break
                
                # Extract skills from entry
                skills = self._extract_tech_from_text(entry)
                
                experience.append(Experience(
                    role=role[:100],
                    company=company,
                    duration_months=6,  # Default
                    description=entry[:500],
                    skills=skills
                ))
        
        return experience
    
    def normalize_skills(self, skills: List[SkillClaim]) -> List[NormalizedSkill]:
        """Normalize skill names to canonical taxonomy."""
        normalized = []
        seen = set()
        
        for skill in skills:
            canonical = self.skill_keywords.get(
                skill.name.lower(),
                self.skill_keywords.get(self._skill_key(skill.name), skill.name),
            )
            if canonical not in seen:
                seen.add(canonical)
                # Determine category
                category = "other"
                for cat, skills_list in self.skill_taxonomy.items():
                    if canonical in skills_list:
                        category = cat
                        break
                
                normalized.append(NormalizedSkill(
                    canonical_name=canonical,
                    original_names=[skill.name],
                    category=category
                ))
        
        return normalized