import unittest

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from database import Base
    from models import Course, Institution
except ModuleNotFoundError:  # Lightweight source-test environments omit SQLAlchemy.
    create_engine = None


@unittest.skipIf(create_engine is None, "SQLAlchemy is not installed")
class CourseIdentityScopeTests(unittest.TestCase):
    def test_same_catalog_code_can_exist_at_two_campuses(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
        bmcc = Institution(code="BMCC", name="BMCC")
        brooklyn = Institution(code="BROOKLYN", name="Brooklyn College")
        db.add_all([bmcc, brooklyn])
        db.flush()
        db.add_all([
            Course(institution_id=bmcc.id, code="MATH 301", title="Calculus I", credits=4),
            Course(institution_id=brooklyn.id, code="MATH 301", title="Probability", credits=3),
        ])
        db.commit()
        rows = db.query(Course).filter_by(code="MATH 301").all()
        self.assertEqual(2, len(rows))
        self.assertEqual({bmcc.id, brooklyn.id}, {row.institution_id for row in rows})


if __name__ == "__main__":
    unittest.main()
