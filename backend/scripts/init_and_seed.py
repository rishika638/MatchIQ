import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.entities import User, Organization, OrganizationMember, CandidateProfile, Opportunity
from app.services.ingestion_service import ingestion_service
from app.services.evaluation_service import evaluation_engine


def seed_database(demo=False, run_benchmarks=False):
    print("Creating application tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        org = None
        if demo:
            org = db.query(Organization).filter(Organization.slug == "matchiq-labs").first()
            if not org:
                org = Organization(name="MatchIQ Enterprise Labs", slug="matchiq-labs", plan="enterprise")
                db.add(org)
                db.flush()

            demo_user = db.query(User).filter(User.email == "candidate@matchiq.ai").first()
            if not demo_user:
                demo_user = User(
                    email="candidate@matchiq.ai",
                    hashed_password=hash_password("DemoCandidate123!"),
                    full_name="Alex Mercer",
                    role="candidate",
                    is_active=True
                )
                db.add(demo_user)
                db.flush()
                db.add(OrganizationMember(
                    organization_id=org.id,
                    user_id=demo_user.id,
                    role="member"
                ))
                db.add(CandidateProfile(
                    user_id=demo_user.id,
                    organization_id=org.id,
                    headline="Senior Full Stack & Distributed Systems Engineer",
                    bio="Local demo candidate profile.",
                    experience_years=5.5,
                    skills=["Python", "FastAPI", "Go", "Distributed Systems", "PostgreSQL", "Docker", "Kubernetes", "Next.js", "TypeScript", "Kafka"],
                    preferred_locations=["San Francisco, CA (Remote)", "Remote, United States", "Seattle, WA"],
                    preferred_work_modes=["remote", "hybrid"],
                    preferred_opportunity_types=["full-time"],
                    preferred_min_salary=160000,
                    preferred_currency="USD",
                    preferred_roles=["Senior Backend Engineer", "Distributed Systems Engineer", "Full Stack Engineer"]
                ))
                db.commit()
                print("Created local demo candidate.")

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        opp_count = db.query(Opportunity).filter(Opportunity.status == "active").count()
        if opp_count == 0:
            seed_json_path = os.path.join(project_root, "data", "seed", "opportunities_100.json")
            if os.path.exists(seed_json_path):
                with open(seed_json_path, "r", encoding="utf-8") as seed_file:
                    records = json.load(seed_file)
                job = ingestion_service.ingest_records(
                    db=db,
                    raw_records=records,
                    file_name="opportunities_100.json",
                    file_type="json",
                    organization_id=org.id if org else None
                )
                print(f"Seed ingestion: {job.successful_records} successful, {job.failed_records} failed.")

        benchmark_path = os.path.join(project_root, "data", "evaluation", "evaluation_benchmark.json")
        if os.path.exists(benchmark_path):
            loaded = evaluation_engine.load_benchmark_dataset(db, benchmark_file=benchmark_path)
            print(f"Loaded {loaded} benchmark queries.")

        if run_benchmarks:
            runs = evaluation_engine.run_full_suite(db, organization_id=org.id if org else None)
            print(f"Generated {len(runs)} benchmark evaluation runs.")

        print("MatchIQ database initialization complete.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Create local demo credentials and organization.")
    parser.add_argument("--run-benchmarks", action="store_true", help="Generate evaluation runs.")
    args = parser.parse_args()
    seed_database(demo=args.demo, run_benchmarks=args.run_benchmarks)
