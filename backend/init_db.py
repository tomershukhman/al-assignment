from backend.database import create_db_and_tables
from backend.models import Topic, Problem, Submission  # Import models to register them with metadata

if __name__ == "__main__":
    print("Creating tables...")
    create_db_and_tables()
    print("Tables created.")

    import json
    from pathlib import Path
    from sqlmodel import Session, select
    from backend.database import engine

    seed_file = Path("seed_data.json")
    if seed_file.exists():
        print(f"Found seed data: {seed_file}")
        with open(seed_file, "r") as f:
            data = json.load(f)
            
        with Session(engine) as session:
            for topic_data in data.get("topics", []):
                # Check if topic exists
                existing_topic = session.exec(select(Topic).where(Topic.id == topic_data["id"])).first()
                if not existing_topic:
                    print(f"Adding topic: {topic_data['name']}")
                    topic = Topic(
                        id=topic_data["id"],
                        name=topic_data["name"],
                        description=topic_data["description"],
                        grade_level=topic_data["grade_level"]
                    )
                    session.add(topic)
                else:
                    print(f"Topic already exists: {topic_data['name']}")
                
                # Commit topic to ensure FK constraint satisfied for problems
                session.commit()
                if not existing_topic:
                    session.refresh(topic)

                for problem_data in topic_data.get("problems", []):
                    # Check if problem exists
                    existing_problem = session.exec(select(Problem).where(Problem.id == problem_data["id"])).first()
                    if not existing_problem:
                        print(f"  Adding problem: {problem_data['id']}")
                        problem = Problem(
                            id=problem_data["id"],
                            topic_id=topic_data["id"],
                            question=problem_data["question"],
                            correct_answer=problem_data["correct_answer"]
                        )
                        session.add(problem)
                    else:
                        print(f"  Problem already exists: {problem_data['id']}")
            
            session.commit()
            print("Seeding completed.")
    else:
        print("No seed_data.json found.")
