import pandas as pd
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://admin:#1234abc@mysite.c2wsj582gqkn.ap-south-1.rds.amazonaws.com:3306/test"
)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def load_data(query, columns):
    with session_scope() as session:
        result = session.execute(text(query))
        dir_list = []
        for row in result:
            dir = {col: getattr(row, col) for col in columns}
            dir_list.append(dir)
        return pd.DataFrame(dir_list)


def get_skills(id, id_field, table):
    with session_scope() as session:
        query = f"SELECT skill FROM {table} WHERE {id_field} = :y"
        result = session.execute(text(query), {"y": id})
        skills = [row.skill for row in result]
        return skills


def get_emp_df():
    with session_scope() as session:
        emp_columns = [
            "pwd",
            "pname",
            "pid",
            "pdomain",
            "mname",
            "mmail",
            "managerid",
            "ename",
            "email",
            "eid",
            "dept",
        ]
        emp_stmt = "select * from load_emp"
        emp_df = load_data(emp_stmt, emp_columns)
        emp_skill_dir = [
            {"eid": eid, "skills": get_skills(eid, "eid", "emp_skill")}
            for eid in emp_df["eid"].unique()
        ]
        skill_df = pd.DataFrame(emp_skill_dir)
        emp_df = pd.merge(skill_df, emp_df, on="eid")
        return emp_df


def get_project_df():
    with session_scope() as session:
        project_columns = [
            "eid",
            "email",
            "ename",
            "needed",
            "pdesc",
            "pdomain",
            "pid",
            "pname",
            "present",
        ]
        proj_stmt = "select * from manager_project"
        project_df = load_data(proj_stmt, project_columns)
        project_skill_dir = [
            {"pid": pid, "skills": get_skills(pid, "pid", "project_skill")}
            for pid in project_df["pid"].unique()
        ]
        skill_df = pd.DataFrame(project_skill_dir)
        project_df = pd.merge(skill_df, project_df, on="pid")
        project_df.rename(columns={"eid": "mid", "email": "mmail", "ename": "mname"})
        return project_df


def get_request_df(emp_df, project_df):
    with session_scope() as session:
        request_columns = ["eid", "ename", "pdesc", "pid", "pname", "status"]
        request_stmt = "select * from request_tab"
        request_df = load_data(request_stmt, request_columns)

        emp_skill_df = emp_df[["skills", "eid"]].rename(
            columns={"skills": "emp_skills"}
        )
        request_df = pd.merge(request_df, emp_skill_df, on="eid")

        project_skill_df = project_df[["skills", "pid"]].rename(
            columns={"skills": "project_skills"}
        )
        request_df = pd.merge(request_df, project_skill_df, on="pid")

        return request_df


def req_transfer(pid, eid):
    with session_scope() as session:
        session.execute(
            text('insert into request values (:x, :y, "Pending");'),
            {"x": pid, "y": eid},
        )
    return get_request_df(get_emp_df(), get_project_df())


def get_courses():
    with session_scope() as session:
        course_columns = ["cid", "skill", "duration", "cname", "clink"]
        stmt = "select * from courses"
        courses_df = load_data(stmt, course_columns)
        return courses_df


def add_skill_emp(eid, cid):
    with session_scope() as session:
        session.execute(
            text("insert into skill_emp values (:x, :y);"), {"x": eid, "y": cid}
        )


def add_project(pid, pdomain, pdesc, pname, needed, present, skill_ids, managerid):
    with session_scope() as session:
        params_project = {
            "x": pid,
            "y": pdomain,
            "z": pdesc,
            "a": pname,
            "b": needed,
            "c": present,
        }
        params_manager = {"x": pid, "y": managerid}
        params_employee = {"x": managerid, "y": pid}

        session.execute(
            text("INSERT INTO project VALUES (:x, :y, :z, :a, :b, :c);"), params_project
        )
        session.execute(text("INSERT INTO manager values (:x, :y);"), params_manager)
        session.execute(
            text("UPDATE employee SET pid = :y, managerid = NULL WHERE eid = :x;"),
            params_employee,
        )

        for id in skill_ids:
            params_skill_project = {"x": pid, "y": id}
            session.execute(
                text("INSERT INTO skill_project VALUES(:x, :y);"), params_skill_project
            )


def add_employee(pwd, pid, managerid, ename, email, eid, dept, skills_id):
    with session_scope() as session:
        session.execute(
            text(
                "insert into employee(pwd, pid , managerid, ename ,email ,eid ,dept) values(:x,:y,:z,:a,:b,:c,:d);"
            ),
            {
                "x": pwd,
                "y": pid,
                "z": managerid,
                "a": ename,
                "b": email,
                "c": eid,
                "d": dept,
            },
        )
        for id in skills_id:
            session.execute(
                text("INSERT INTO skill_emp VALUES(:x, :y);"), {"x": eid, "y": id}
            )


def add_course(cid, skill, duration, cname, clink):
    with session_scope() as session:
        session.execute(
            text("insert into courses values (:x,:y,:z,:a,:b);"),
            {"x": cid, "y": skill, "z": duration, "a": cname, "b": clink},
        )


def accept_emp(pid, eid):
    with session_scope() as session:
        session.execute(
            text("UPDATE request SET status = 'Accepted' WHERE pid = :x AND eid = :y;"),
            {"x": pid, "y": eid},
        )


def reject_emp(pid, eid):
    with session_scope() as session:
        session.execute(
            text("delete from request where pid = :x and eid = :y;"),
            {"x": pid, "y": eid},
        )
