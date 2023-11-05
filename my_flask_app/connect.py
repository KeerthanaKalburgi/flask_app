import pandas as pd
from sqlalchemy import create_engine, text

"""
In this modeule i have loaded all the relavant data required for the application.
hope this works.
in emp_df i have all info regarding employee,
in project_df I have stored all info regrding project
I have combined the skills for both when modifying the request_df table
"""

engine = create_engine(
    "mysql+pymysql://admin:#1234abc@mysite.c2wsj582gqkn.ap-south-1.rds.amazonaws.com:3306/test"
)
conn = engine.connect()
columns = [
    "pwd",
    "pname",
    "pid",
    "pdomain",
    "mnane",
    "mmail",
    "managerid",
    "ename",
    "email",
    "eid",
    "dept",
]
result = conn.execute(text("select * from load_emp"))
dir_list = []
for row in result:
    dir = {
        "pwd": row.pwd,
        "pname": row.pname,
        "pid": row.pid,
        "pdomain": row.pdomain,
        "mname": row.mnane,
        "mmail": row.mmail,
        "managerid": row.managerid,
        "ename": row.ename,
        "email": row.email,
        "eid": row.eid,
        "dept": row.dept,
    }
    dir_list.append(dir)

emp_df = pd.DataFrame(dir_list)
skill_dir = []
for x in emp_df["eid"].unique():
    result = conn.execute(text("SELECT skill FROM emp_skill WHERE eid = :y "), {"y": x})
    skill = []
    for row in result:
        skill.append(row.skill)
    dir = {"eid": x, "skills": skill}
    skill_dir.append(dir)

skill_df = pd.DataFrame(skill_dir)
"""
In this section I have loaded the database and appended the skills to the employee,
along with adding project and manager details(this was done using views in MySql workbench).

"""
emp_df = pd.merge(skill_df, emp_df, on="eid")

result = conn.execute(text("select * from manager_project"))
dir_list = []
for row in result:
    dir = {
        "mid": row.eid,
        "mmail": row.email,
        "mname": row.ename,
        "vacant": row.needed,
        "pdesc": row.pdesc,
        "pdomain": row.pdomain,
        "pid": row.pid,
        "pname": row.pname,
        "present": row.present,
    }
    dir_list.append(dir)

project_df = pd.DataFrame(dir_list)
skill_dir = []
for x in project_df["pid"].unique():
    result = conn.execute(text("SELECT skill FROM emp_skill WHERE eid = :y "), {"y": x})
    skill = []
    for row in result:
        skill.append(row.skill)
    dir = {"pid": x, "skills": skill}
    skill_dir.append(dir)

skill_df = pd.DataFrame(skill_dir)
project_df = pd.merge(skill_df, project_df, on="pid")


result = conn.execute(text("select * from request_tab"))
dir_list = []
for row in result:
    dir = {
        "eid": row.eid,
        "ename": row.ename,
        "pdesc": row.pdesc,
        "pid": row.pid,
        "pname": row.pname,
        "status": row.status,
    }
    dir_list.append(dir)

request_df = pd.DataFrame(dir_list)
request_df = pd.merge(request_df, emp_df[["skills", "eid"]], on="eid")
request_df = request_df.rename(columns={"skills": "emp_skills"})
request_df = pd.merge(request_df, project_df[["skills", "pid"]], on="pid")
request_df = request_df.rename(columns={"skills": "project_skills"})


def req_tranfer(eid, ename, pdesc, pid, pname, request_df, emp_df, project_df):
    conn.execute(
        text("insert into request values(:x,:y,'Pending');"), [{"x": pid, "y": eid}]
    )
    conn.commit()
    dir = {
        "eid": eid,
        "ename": ename,
        "pdesc": pdesc,
        "pid": pid,
        "pname": pname,
        "status": "Pending",
    }
    request_df = request_df._append(dir, ignore_index=True)
    request_df = pd.merge(request_df, emp_df[["skills", "eid"]], on="eid")
    request_df = request_df.rename(columns={"skills": "emp_skills"})
    request_df = pd.merge(request_df, project_df[["skills", "pid"]], on="pid")
    request_df = request_df.rename(columns={"skills": "project_skills"})
