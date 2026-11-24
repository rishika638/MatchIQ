import json
import csv
import random
import uuid
import os

ROLES = [
    # Backend & Distributed Systems
    {
        "title": "Senior Distributed Systems Engineer",
        "company": "NexusScale Labs",
        "department": "Infrastructure",
        "work_mode": "remote",
        "location": "San Francisco, CA (Remote)",
        "opportunity_type": "full-time",
        "experience_level": "senior",
        "min_years_experience": 5,
        "max_years_experience": 9,
        "min_salary": 175000,
        "max_salary": 225000,
        "currency": "USD",
        "required_skills": ["Go", "Distributed Systems", "Kubernetes", "gRPC", "Kafka", "PostgreSQL"],
        "nice_to_have_skills": ["Rust", "Raft Consensus", "eBPF", "Prometheus"],
        "description": "NexusScale is building the next-generation multi-region consensus and messaging backbone for high-throughput enterprise systems. You will architect low-latency event fabrics handling 2M+ IOPS across global clusters.",
        "responsibilities": [
            "Architect and maintain fault-tolerant distributed consensus services using Raft and Go.",
            "Optimize network serialization and memory layouts for sub-millisecond p99 latencies.",
            "Design multi-tenant isolation boundaries and load shedding mechanisms."
        ]
    },
    {
        "title": "Backend Engineering Intern - Distributed AI",
        "company": "CognitiveStream",
        "department": "Core AI Platform",
        "work_mode": "hybrid",
        "location": "Seattle, WA",
        "opportunity_type": "internship",
        "experience_level": "entry",
        "min_years_experience": 0,
        "max_years_experience": 1,
        "min_salary": 90000,
        "max_salary": 115000,
        "currency": "USD",
        "required_skills": ["Python", "FastAPI", "Distributed Systems", "SQLAlchemy", "Docker"],
        "nice_to_have_skills": ["Ray", "PyTorch", "Redis", "Kafka"],
        "description": "Join our AI Platform team for an intensive internship building distributed asynchronous worker queues and caching layers for LLM inference pipelines.",
        "responsibilities": [
            "Implement high-throughput batching microservices in Python 3.12 and FastAPI.",
            "Build benchmark harnesses to profile worker queue throughput and Redis cache hit rates.",
            "Collaborate with AI researchers to deploy distributed model inference jobs."
        ]
    },
    {
        "title": "Senior AI Infrastructure Engineer",
        "company": "Synthetix AI",
        "department": "Platform ML",
        "work_mode": "remote",
        "location": "New York, NY (Remote)",
        "opportunity_type": "full-time",
        "experience_level": "senior",
        "min_years_experience": 4,
        "max_years_experience": 8,
        "min_salary": 185000,
        "max_salary": 240000,
        "currency": "USD",
        "required_skills": ["Python", "PyTorch", "Kubernetes", "Vector Databases", "Triton Inference Server", "CUDA"],
        "nice_to_have_skills": ["vLLM", "TensorRT", "Slurm", "LangChain"],
        "description": "Lead the team scaling production inference engines for multi-modal generative models. You will oversee GPU orchestration, model sharding, dynamic batching, and KV-cache offloading.",
        "responsibilities": [
            "Optimize model serving runtimes using Triton, vLLM, and custom CUDA kernels.",
            "Manage large GPU clusters on Kubernetes with custom autoscalers.",
            "Integrate pgvector and Milvus for trillion-vector semantic retrieval."
        ]
    },
    {
        "title": "Machine Learning Engineer - NLP & Search",
        "company": "Vectura Search",
        "department": "Applied Research",
        "work_mode": "remote",
        "location": "Austin, TX (Remote)",
        "opportunity_type": "full-time",
        "experience_level": "mid",
        "min_years_experience": 3,
        "max_years_experience": 6,
        "min_salary": 150000,
        "max_salary": 190000,
        "currency": "USD",
        "required_skills": ["Python", "Sentence Transformers", "pgvector", "Information Retrieval", "Elasticsearch", "PyTorch"],
        "nice_to_have_skills": ["Cross-Encoders", "HuggingFace", "Reranking", "FastAPI"],
        "description": "We are seeking an ML engineer passionate about neural search, dense retrieval, and hybrid re-ranking. You will train custom bi-encoders and cross-encoders to power enterprise knowledge discovery.",
        "responsibilities": [
            "Fine-tune dense bi-encoder models on domain-specific enterprise corpora.",
            "Implement hybrid search pipelines combining BM25 keyword matching with vector cosine distance.",
            "Evaluate retrieval quality using NDCG@10, MRR, and reciprocal rank fusion."
        ]
    },
    {
        "title": "Full Stack Engineer - AI Experiences",
        "company": "HyperLogic Technologies",
        "department": "Product Engineering",
        "work_mode": "hybrid",
        "location": "San Francisco, CA",
        "opportunity_type": "full-time",
        "experience_level": "mid",
        "min_years_experience": 3,
        "max_years_experience": 7,
        "min_salary": 145000,
        "max_salary": 185000,
        "currency": "USD",
        "required_skills": ["TypeScript", "Next.js", "React", "Python", "FastAPI", "Tailwind CSS"],
        "nice_to_have_skills": ["PostgreSQL", "Docker", "LangChain", "WebSockets"],
        "description": "Help design and build interactive, real-time AI copilots. You will bridge elegant React/Next.js interfaces with streaming FastAPI backends, delivering fluid generative UI experiences.",
        "responsibilities": [
            "Build accessible, responsive UI workflows in Next.js App Router and Tailwind CSS.",
            "Develop resilient backend endpoints with FastAPI, WebSockets, and server-sent events.",
            "Collaborate closely with product designers to ship intuitive agentic dashboards."
        ]
    },
    {
        "title": "Senior Cloud SRE & Security Engineer",
        "company": "Aegis Cloud Systems",
        "department": "Security & Operations",
        "work_mode": "remote",
        "location": "Chicago, IL (Remote)",
        "opportunity_type": "full-time",
        "experience_level": "senior",
        "min_years_experience": 5,
        "max_years_experience": 10,
        "min_salary": 170000,
        "max_salary": 215000,
        "currency": "USD",
        "required_skills": ["Terraform", "AWS", "Kubernetes", "Linux", "CI/CD", "Docker", "Python"],
        "nice_to_have_skills": ["Vault", "OpenTelemetry", "Zero Trust", "Golang"],
        "description": "Aegis Cloud operates mission-critical fintech infrastructure. As Senior SRE, you will harden our multi-region AWS and Kubernetes footprints, implement zero-trust telemetry, and manage automated DR drills.",
        "responsibilities": [
            "Maintain infrastructure as code with Terraform and GitOps practices (ArgoCD).",
            "Establish SLOs, automated error-budget alerting, and incident response playbooks.",
            "Conduct penetration testing and enforce IAM least-privilege policies."
        ]
    },
    {
        "title": "Data Platform Engineer - Streaming & Analytics",
        "company": "DataPulse Corp",
        "department": "Data Infrastructure",
        "work_mode": "onsite",
        "location": "Boston, MA",
        "opportunity_type": "full-time",
        "experience_level": "mid",
        "min_years_experience": 3,
        "max_years_experience": 6,
        "min_salary": 140000,
        "max_salary": 180000,
        "currency": "USD",
        "required_skills": ["Python", "Apache Kafka", "Apache Spark", "SQL", "Snowflake", "dbt"],
        "nice_to_have_skills": ["Apache Flink", "Airflow", "Iceberg", "AWS"],
        "description": "Architect real-time event streaming and analytical data marts powering consumer insights. You will craft scalable ETL/ELT pipelines processing billions of events daily.",
        "responsibilities": [
            "Build and monitor streaming data consumers using Apache Kafka and Spark Streaming.",
            "Maintain dimensional schemas and data warehouse transforms in Snowflake and dbt.",
            "Ensure high data freshness, accuracy, and schema evolution compatibility."
        ]
    },
    {
        "title": "Lead Backend Architect - Financial Systems",
        "company": "Finovate Global",
        "department": "Core Banking",
        "work_mode": "hybrid",
        "location": "New York, NY",
        "opportunity_type": "full-time",
        "experience_level": "lead",
        "min_years_experience": 8,
        "max_years_experience": 14,
        "min_salary": 220000,
        "max_salary": 290000,
        "currency": "USD",
        "required_skills": ["Java", "Spring Boot", "Distributed Systems", "PostgreSQL", "Kafka", "Microservices"],
        "nice_to_have_skills": ["Go", "Kubernetes", "Event Sourcing", "CQRS"],
        "description": "Lead the technical strategy and system architecture for our distributed ledger and ledger settlement engines. High concurrency, double-entry consistency, and zero downtime are paramount.",
        "responsibilities": [
            "Design immutable event-sourced ledgers and real-time transaction reconciliation services.",
            "Mentor senior engineers on distributed transaction patterns (Saga, 2PC, Outbox).",
            "Partner with compliance and security leaders on regulatory audit trails."
        ]
    },
    {
        "title": "Frontend Software Engineer - Design Systems",
        "company": "Aura Interactive",
        "department": "Design Engineering",
        "work_mode": "remote",
        "location": "Los Angeles, CA (Remote)",
        "opportunity_type": "full-time",
        "experience_level": "mid",
        "min_years_experience": 2,
        "max_years_experience": 5,
        "min_salary": 130000,
        "max_salary": 165000,
        "currency": "USD",
        "required_skills": ["React", "TypeScript", "Tailwind CSS", "CSS Modules", "Storybook", "Accessibility (a11y)"],
        "nice_to_have_skills": ["Framer Motion", "Next.js", "Figma", "Radix UI"],
        "description": "Create the unified UI kit and component library powering dozens of web and mobile enterprise applications. Focus on micro-interactions, accessibility compliance (WCAG AAA), and developer velocity.",
        "responsibilities": [
            "Develop reusable, token-driven component architectures in TypeScript and React.",
            "Ensure cross-browser pixel precision, keyboard navigation, and screen reader friendliness.",
            "Write comprehensive automated visual regression and component unit tests."
        ]
    },
    {
        "title": "Junior Python Backend Developer",
        "company": "Cortex Logistics",
        "department": "Supply Chain Technology",
        "work_mode": "hybrid",
        "location": "Atlanta, GA",
        "opportunity_type": "full-time",
        "experience_level": "entry",
        "min_years_experience": 1,
        "max_years_experience": 3,
        "min_salary": 85000,
        "max_salary": 110000,
        "currency": "USD",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git", "REST APIs"],
        "nice_to_have_skills": ["Redis", "SQLAlchemy", "Pytest", "AWS"],
        "description": "Join an agile logistics team digitizing fleet dispatch and warehouse operations. Great mentorship environment for early-career developers looking to master modern asynchronous Python.",
        "responsibilities": [
            "Develop and test REST API endpoints for dispatch tracking and load calculations.",
            "Write relational queries and schema migrations in PostgreSQL and Alembic.",
            "Troubleshoot staging environments and assist in production deployments."
        ]
    }
]

COMPANIES = [
    "NexusScale Labs", "Synthetix AI", "CognitiveStream", "Vectura Search", "HyperLogic Technologies",
    "Aegis Cloud Systems", "DataPulse Corp", "Finovate Global", "Aura Interactive", "Cortex Logistics",
    "Prism Analytics", "Aether Robotics", "CloudMatrix", "NovaByte Systems", "QuantEdge Financial",
    "BioGenix Informatics", "Starlight Media Tech", "Veritas CyberSec", "OmniRoute Networks", "Kinetix Cloud",
    "DeepTensor Inc", "Vertex Scale", "Helix Medical AI", "Beacon Energy Tech", "PulsePoint Health",
    "Zenith Payments", "Apex Microservices", "Strata Data Labs", "VectorShift", "Orbital Telemetry"
]

LOCATIONS = [
    ("San Francisco, CA", "hybrid"),
    ("San Francisco, CA (Remote)", "remote"),
    ("New York, NY", "hybrid"),
    ("New York, NY (Remote)", "remote"),
    ("Seattle, WA", "onsite"),
    ("Austin, TX", "hybrid"),
    ("Austin, TX (Remote)", "remote"),
    ("Chicago, IL", "hybrid"),
    ("Boston, MA", "onsite"),
    ("Denver, CO (Remote)", "remote"),
    ("London, UK", "hybrid"),
    ("London, UK (Remote)", "remote"),
    ("Toronto, Canada", "hybrid"),
    ("Remote, United States", "remote"),
    ("Remote, Global", "remote")
]

EXPERIENCE_LEVELS = [
    ("entry", 0, 2, 75000, 115000),
    ("mid", 2, 6, 125000, 180000),
    ("senior", 5, 10, 165000, 235000),
    ("lead", 7, 14, 210000, 280000),
    ("staff", 10, 18, 250000, 340000)
]

OPPORTUNITY_TYPES = ["full-time", "full-time", "full-time", "contract", "internship"]

SKILL_SETS = [
    (["Python", "FastAPI", "PostgreSQL", "Docker", "SQLAlchemy"], ["Redis", "Celery", "AWS", "Pytest"]),
    (["Go", "Distributed Systems", "Kubernetes", "gRPC", "Kafka"], ["Prometheus", "Docker", "Raft", "AWS"]),
    (["Python", "PyTorch", "LLMs", "Vector Databases", "LangChain"], ["vLLM", "HuggingFace", "FastAPI", "Docker"]),
    (["TypeScript", "Next.js", "React", "Tailwind CSS", "Node.js"], ["GraphQL", "PostgreSQL", "Docker", "Zustand"]),
    (["Python", "Apache Spark", "Kafka", "SQL", "Snowflake"], ["dbt", "Airflow", "AWS S3", "Databricks"]),
    (["Terraform", "Kubernetes", "AWS", "CI/CD", "Linux"], ["Docker", "Prometheus", "Grafana", "Python"]),
    (["Rust", "Distributed Systems", "Concurrency", "Linux", "Networking"], ["WebAssembly", "C++", "gRPC", "Docker"]),
    (["Java", "Spring Boot", "Microservices", "PostgreSQL", "Kafka"], ["Docker", "Kubernetes", "Redis", "Elasticsearch"]),
    (["Python", "Information Retrieval", "Sentence Transformers", "pgvector"], ["Elasticsearch", "FastAPI", "Cross-Encoders"]),
    (["React Native", "TypeScript", "Mobile Development", "REST APIs"], ["Redux", "iOS", "Android", "GraphQL"])
]

TITLES_POOL = [
    "Backend Software Engineer", "Senior Backend Engineer", "Distributed Systems Architect",
    "Staff AI Systems Engineer", "Machine Learning Platform Engineer", "NLP Research Engineer",
    "Full Stack Software Engineer", "Senior Frontend Engineer", "Cloud Infrastructure SRE",
    "DevOps & Platform Engineer", "Data Infrastructure Engineer", "Real-Time Streaming Engineer",
    "Security Software Engineer", "Applied AI Research Scientist", "Search & Retrieval Engineer",
    "Backend Systems Engineer (Go/Rust)", "AI Solutions Architect", "Autonomous Agent Engineer",
    "Database Internals Engineer", "Core Platform Software Engineer"
]

def generate_opportunities(count=100):
    opportunities = []
    
    # 1. First add the 10 carefully crafted initial roles
    for i, role in enumerate(ROLES):
        opp_id = f"opp-seed-{i+1:03d}"
        opp = {
            "id": opp_id,
            "title": role["title"],
            "company": role["company"],
            "department": role["department"],
            "work_mode": role["work_mode"],
            "location": role["location"],
            "opportunity_type": role["opportunity_type"],
            "experience_level": role["experience_level"],
            "min_years_experience": role["min_years_experience"],
            "max_years_experience": role["max_years_experience"],
            "min_salary": role["min_salary"],
            "max_salary": role["max_salary"],
            "currency": role["currency"],
            "description": role["description"],
            "responsibilities": role["responsibilities"],
            "required_skills": role["required_skills"],
            "nice_to_have_skills": role["nice_to_have_skills"],
            "benefits": [
                "Comprehensive medical, dental, and vision insurance",
                "401(k) matching up to 5%",
                "Generous equity package with early-exercise options",
                "$2,500 annual personal learning and conference budget",
                "Home office setup stipend ($1,500)"
            ],
            "is_synthetic": True,
            "source": "synthetic_seed_v1",
            "application_url": f"https://careers.example.com/{opp_id}",
            "contact_email": f"talent@{role['company'].lower().replace(' ', '')}.com"
        }
        opportunities.append(opp)
        
    # 2. Generate the remaining to reach exactly count (e.g. 100)
    random.seed(42) # Reproducible seed
    departments = ["Core Engineering", "Platform Infrastructure", "Applied AI", "Data Products", "Developer Tools", "Product Growth", "Security & SRE"]
    
    for i in range(len(ROLES), count):
        opp_id = f"opp-seed-{i+1:03d}"
        title = random.choice(TITLES_POOL)
        company = random.choice(COMPANIES)
        department = random.choice(departments)
        loc, mode = random.choice(LOCATIONS)
        exp_lvl, min_yr, max_yr, min_sal, max_sal = random.choice(EXPERIENCE_LEVELS)
        opp_type = random.choice(OPPORTUNITY_TYPES)
        if opp_type == "internship":
            exp_lvl = "entry"
            min_yr = 0
            max_yr = 1
            min_sal = 80000
            max_sal = 110000
            if "Intern" not in title:
                title = f"{title} Intern"
        elif exp_lvl in ["lead", "staff"] and not any(k in title for k in ["Lead", "Staff", "Architect"]):
            title = f"{exp_lvl.capitalize()} {title}"
        elif exp_lvl == "senior" and "Senior" not in title and "Lead" not in title and "Staff" not in title:
            title = f"Senior {title}"
            
        req_skills, nice_skills = random.choice(SKILL_SETS)
        
        desc = (
            f"{company} is looking for a talented {title} to join our {department} group in {loc}. "
            f"In this role, you will collaborate with cross-functional product, platform, and AI engineering teams "
            f"to architect resilient services, optimize data pipelines, and ship production features serving hundreds of thousands of users. "
            f"Key focus areas include robust test-driven software design, distributed data consistency, and high-performance computation."
        )
        
        resps = [
            f"Design and maintain scalable microservices using {req_skills[0]} and {req_skills[1]}.",
            f"Optimize database queries, indices, and schema layouts in {req_skills[2]} for low latency.",
            f"Partner with team leads to participate in architectural reviews, automated testing, and CI/CD releases.",
            f"Drive system reliability, observability, and metrics using modern telemetry frameworks."
        ]
        
        opp = {
            "id": opp_id,
            "title": title,
            "company": company,
            "department": department,
            "work_mode": mode,
            "location": loc,
            "opportunity_type": opp_type,
            "experience_level": exp_lvl,
            "min_years_experience": min_yr,
            "max_years_experience": max_yr,
            "min_salary": min_sal + random.randint(-5, 10) * 1000,
            "max_salary": max_sal + random.randint(0, 20) * 1000,
            "currency": "USD",
            "description": desc,
            "responsibilities": resps,
            "required_skills": req_skills,
            "nice_to_have_skills": nice_skills,
            "benefits": [
                "Comprehensive medical, dental, and vision insurance",
                "401(k) retirement plan with match",
                "Flexible paid time off (PTO)",
                "Annual hardware & learning budget"
            ],
            "is_synthetic": True,
            "source": "synthetic_seed_v1",
            "application_url": f"https://careers.example.com/{opp_id}",
            "contact_email": f"talent@{company.lower().replace(' ', '')}.com"
        }
        opportunities.append(opp)
        
    return opportunities

def generate_evaluation_benchmark(opportunities):
    """
    Generate labelled benchmark dataset with realistic user queries,
    candidate profile contexts, and ground-truth relevance judgements (0: not relevant, 1: marginally relevant, 2: relevant, 3: highly relevant).
    """
    benchmarks = [
        {
            "query_id": "eval-q01",
            "query": "I want a backend engineering internship involving Python, distributed systems and AI.",
            "candidate_profile": {
                "title": "Computer Science Student / Software Engineering Intern",
                "years_experience": 1,
                "skills": ["Python", "FastAPI", "Distributed Systems", "Docker", "PyTorch"],
                "preferred_opportunity_types": ["internship"],
                "preferred_locations": ["Seattle, WA", "Remote, United States"]
            },
            "intent": "Junior candidate looking for entry-level / internship role combining Python backend with distributed AI workloads.",
            "judgments": [
                {"opportunity_id": "opp-seed-002", "grade": 3, "rationale": "Perfect match: Backend Engineering Intern - Distributed AI using Python, FastAPI, Docker."},
                {"opp_search_skill": "Python, Distributed Systems", "min_grade": 2}
            ]
        },
        {
            "query_id": "eval-q02",
            "query": "Senior Distributed Systems engineer experienced with Go, Kubernetes and Kafka for high-throughput messaging.",
            "candidate_profile": {
                "title": "Senior Backend Systems Engineer",
                "years_experience": 7,
                "skills": ["Go", "Distributed Systems", "Kubernetes", "Kafka", "gRPC", "PostgreSQL"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["San Francisco, CA (Remote)", "Remote, United States"]
            },
            "intent": "Senior Go engineer seeking high throughput distributed infrastructure positions.",
            "judgments": [
                {"opportunity_id": "opp-seed-001", "grade": 3, "rationale": "Direct title, tech stack (Go, K8s, Kafka, gRPC), and senior experience match."}
            ]
        },
        {
            "query_id": "eval-q03",
            "query": "Machine learning and NLP search role utilizing Sentence Transformers, vector databases, and neural reranking.",
            "candidate_profile": {
                "title": "Machine Learning Engineer",
                "years_experience": 4,
                "skills": ["Python", "Sentence Transformers", "pgvector", "Information Retrieval", "Elasticsearch"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["Austin, TX (Remote)", "Remote, United States"]
            },
            "intent": "Information retrieval and NLP specialist looking for semantic search and reranking roles.",
            "judgments": [
                {"opportunity_id": "opp-seed-004", "grade": 3, "rationale": "Exact match for ML Engineer - NLP & Search with Sentence Transformers, pgvector, and reranking."}
            ]
        },
        {
            "query_id": "eval-q04",
            "query": "Full stack engineer proficient in Next.js, React, TypeScript and FastAPI building interactive AI web applications.",
            "candidate_profile": {
                "title": "Full Stack Engineer",
                "years_experience": 4,
                "skills": ["TypeScript", "Next.js", "React", "Python", "FastAPI", "Tailwind CSS"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["San Francisco, CA", "Remote, United States"]
            },
            "intent": "Modern web full-stack engineer targeting AI-driven user experience positions.",
            "judgments": [
                {"opportunity_id": "opp-seed-005", "grade": 3, "rationale": "Direct match for Full Stack Engineer - AI Experiences using Next.js, React, TypeScript, FastAPI."}
            ]
        },
        {
            "query_id": "eval-q05",
            "query": "Cloud infrastructure SRE and security engineer with Terraform, AWS, and Kubernetes automation experience.",
            "candidate_profile": {
                "title": "Senior DevOps / SRE",
                "years_experience": 6,
                "skills": ["Terraform", "AWS", "Kubernetes", "Linux", "CI/CD", "Docker", "Python"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["Chicago, IL (Remote)", "Remote, United States"]
            },
            "intent": "Senior SRE seeking cloud infrastructure, Terraform, and zero-trust security positions.",
            "judgments": [
                {"opportunity_id": "opp-seed-006", "grade": 3, "rationale": "Exact alignment with Senior Cloud SRE & Security Engineer requirements and tech stack."}
            ]
        },
        {
            "query_id": "eval-q06",
            "query": "Data engineering streaming role working with Apache Kafka, Spark, and Snowflake data warehouses.",
            "candidate_profile": {
                "title": "Data Engineer",
                "years_experience": 4,
                "skills": ["Python", "Apache Kafka", "Apache Spark", "SQL", "Snowflake", "dbt"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["Boston, MA", "Remote, United States"]
            },
            "intent": "Data platform engineer focused on real-time streaming pipelines and modern data warehouse analytics.",
            "judgments": [
                {"opportunity_id": "opp-seed-007", "grade": 3, "rationale": "Direct match with Data Platform Engineer - Streaming & Analytics."}
            ]
        },
        {
            "query_id": "eval-q07",
            "query": "Senior GPU and Triton inference engineer optimizing LLMs and large scale model serving.",
            "candidate_profile": {
                "title": "Senior AI Infrastructure Engineer",
                "years_experience": 6,
                "skills": ["Python", "PyTorch", "Kubernetes", "CUDA", "Triton Inference Server", "vLLM"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["New York, NY (Remote)", "Remote, United States"]
            },
            "intent": "GPU infrastructure specialist looking for high performance inference serving.",
            "judgments": [
                {"opportunity_id": "opp-seed-003", "grade": 3, "rationale": "Direct match with Senior AI Infrastructure Engineer role at Synthetix AI."}
            ]
        },
        {
            "query_id": "eval-q08",
            "query": "Lead architect for distributed financial transaction systems with Java, Spring Boot and event sourcing.",
            "candidate_profile": {
                "title": "Principal Architect",
                "years_experience": 10,
                "skills": ["Java", "Spring Boot", "Distributed Systems", "PostgreSQL", "Kafka", "CQRS"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["New York, NY", "Remote, United States"]
            },
            "intent": "Fintech architect targeting core banking and immutable transaction ledger systems.",
            "judgments": [
                {"opportunity_id": "opp-seed-008", "grade": 3, "rationale": "Exact match with Lead Backend Architect - Financial Systems."}
            ]
        },
        {
            "query_id": "eval-q09",
            "query": "Frontend engineer specialized in accessible UI component design systems and Storybook.",
            "candidate_profile": {
                "title": "Frontend Engineer",
                "years_experience": 3,
                "skills": ["React", "TypeScript", "Tailwind CSS", "Storybook", "Accessibility (a11y)"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["Los Angeles, CA (Remote)", "Remote, United States"]
            },
            "intent": "Frontend developer focusing on UI libraries, design tokens, and accessibility.",
            "judgments": [
                {"opportunity_id": "opp-seed-009", "grade": 3, "rationale": "Matches Frontend Software Engineer - Design Systems perfectly."}
            ]
        },
        {
            "query_id": "eval-q10",
            "query": "Entry-level junior Python backend developer building REST APIs with FastAPI and PostgreSQL.",
            "candidate_profile": {
                "title": "Junior Python Developer",
                "years_experience": 1,
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs"],
                "preferred_opportunity_types": ["full-time"],
                "preferred_locations": ["Atlanta, GA", "Remote, United States"]
            },
            "intent": "Junior developer looking for mentored Python FastAPI backend roles.",
            "judgments": [
                {"opportunity_id": "opp-seed-010", "grade": 3, "rationale": "Direct match with Junior Python Backend Developer at Cortex Logistics."}
            ]
        }
    ]

    # Dynamically assign grades for other opportunities in the pool based on title and skill overlap
    for b in benchmarks:
        explicit_matched_ids = {j["opportunity_id"] for j in b["judgments"] if "opportunity_id" in j}
        q_text = (b["query"] + " " + " ".join(b["candidate_profile"]["skills"])).lower()
        
        for opp in opportunities:
            if opp["id"] in explicit_matched_ids:
                continue
            
            # Compute heuristic relevance score for evaluation benchmark grading (0, 1, 2, 3)
            overlap_skills = sum(1 for s in opp["required_skills"] if s.lower() in q_text)
            title_overlap = sum(1 for word in opp["title"].lower().split() if word in q_text and len(word) > 3)
            
            grade = 0
            if overlap_skills >= 3 and title_overlap >= 1:
                grade = 2
            elif overlap_skills >= 2 or title_overlap >= 2:
                grade = 1
            elif overlap_skills >= 1:
                grade = 1
                
            if opp["opportunity_type"] != b["candidate_profile"]["preferred_opportunity_types"][0] and b["candidate_profile"]["preferred_opportunity_types"][0] == "internship":
                # Strict penalty if user specifically asks for internship
                grade = max(0, grade - 1)
                
            if grade > 0:
                b["judgments"].append({
                    "opportunity_id": opp["id"],
                    "grade": grade,
                    "rationale": f"Partial match based on {overlap_skills} matching skills and title overlap."
                })
                
    return benchmarks

def main():
    os.makedirs("data/seed", exist_ok=True)
    os.makedirs("data/evaluation", exist_ok=True)
    
    opportunities = generate_opportunities(100)
    
    # Save JSON seed
    json_path = "data/seed/opportunities_100.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(opportunities)} opportunities in {json_path}")
    
    # Save CSV seed
    csv_path = "data/seed/opportunities_100.csv"
    fieldnames = [
        "id", "title", "company", "department", "work_mode", "location",
        "opportunity_type", "experience_level", "min_years_experience",
        "max_years_experience", "min_salary", "max_salary", "currency",
        "description", "responsibilities", "required_skills", "nice_to_have_skills",
        "benefits", "is_synthetic", "source", "application_url", "contact_email"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for opp in opportunities:
            row = opp.copy()
            row["responsibilities"] = "; ".join(row["responsibilities"])
            row["required_skills"] = "; ".join(row["required_skills"])
            row["nice_to_have_skills"] = "; ".join(row["nice_to_have_skills"])
            row["benefits"] = "; ".join(row["benefits"])
            writer.writerow(row)
    print(f"Generated CSV export in {csv_path}")
    
    # Generate Evaluation Benchmark
    benchmarks = generate_evaluation_benchmark(opportunities)
    eval_path = "data/evaluation/evaluation_benchmark.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(benchmarks, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(benchmarks)} benchmark queries in {eval_path}")

if __name__ == "__main__":
    main()
