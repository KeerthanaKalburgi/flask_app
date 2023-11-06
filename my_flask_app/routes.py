from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app
import pandas as pd
from df_db import *

emp_df = get_emp_df()
project_df = get_project_df()
request_df = get_request_df(emp_df, project_df)


@app.route("/", methods=["GET", "POST"])
def index():
    return login()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if email exists in emp_df
        if email in emp_df["email"].values:
            # Check if password matches
            if password == emp_df.loc[emp_df["email"] == email, "pwd"].values[0]:
                # Store email and eid in session variables
                session["email"] = email
                session["eid"] = int(
                    emp_df.loc[emp_df["email"] == email, "eid"].values[0]
                )
                session["ename"] = emp_df.loc[emp_df["email"] == email, "ename"].values[
                    0
                ]

                # Check department and redirect to the appropriate dashboard
                if emp_df.loc[emp_df["email"] == email, "dept"].values[0] == "HR":
                    session["pid"] = None
                    return redirect(url_for("hr_dashboard"))

                else:
                    session["pid"] = int(
                        emp_df.loc[emp_df["email"] == email, "pid"].values[0]
                    )
                    session["skills"] = emp_df.loc[
                        emp_df["email"] == email, "skills"
                    ].values[0]
                    return redirect(url_for("dashboard"))
            else:
                flash("Invalid password")
        else:
            flash("Invalid email")

    return render_template("login.html")


@app.route("/hr_dashboard")
def hr_dashboard():
    user_data = emp_df.loc[emp_df["eid"] == session["eid"]].iloc[0]
    return render_template(
        "HR Dashboard.html",
        user_name=user_data["ename"],
        user_mail=user_data["email"],
        user_dept=user_data["dept"],
    )


@app.route("/dashboard")
def dashboard():
    user_data = emp_df.loc[emp_df["eid"] == session["eid"]].iloc[0]
    # Convert skills list to string
    user_skills = ", ".join(session["skills"])

    return render_template(
        "dashboard.htm",
        user_name=user_data["ename"],
        user_project=user_data["pname"],
        user_skills=user_skills,
        user_dept=user_data["dept"],
    )


@app.route("/add_new_employee", methods=["GET", "POST"])
def add_new_employee():
    courses_df = get_courses()
    emp_df = get_emp_df()
    project_df = get_project_df()
    emp_dept_values = emp_df["dept"].unique()
    skills = courses_df["skill"]
    projects = project_df.loc[project_df["present"] < project_df["needed"], "pname"]
    if request.method == "POST":
        emp_df = get_emp_df()
        project_df = get_project_df()
        courses_df = get_courses()
        eid = emp_df["eid"].max() + 1
        ename = request.form.get("ename")
        email = request.form.get("email")
        dept = request.form.get("dept")
        skills = request.form.getlist("skills[]")
        project = request.form.getlist("project")
        skill_ids = courses_df.loc[courses_df["skill"].isin(skills), "cid"]
        pid = project_df.loc[project_df["pname"].isin(project), "pid"].values[0]
        managerid = project_df.loc[project_df["pname"].isin(project), "eid"].values[0]
        pwd = "password" + str(len(emp_df.index))
        add_employe(pwd, pid, managerid, ename, email, eid, dept, skill_ids)
        flash("Onboarded succesfully")
        return redirect("/add_new_employee")
    return render_template(
        "add new employee.html",
        emp_dept_values=emp_dept_values,
        skills=skills,
        projects=projects,
    )


@app.route("/add_new_project", methods=["GET", "POST"])
def add_new_project():
    emp_df = get_emp_df()
    project_df = get_project_df()
    non_man = non_man = emp_df.loc[emp_df["managerid"].notnull(), ["eid", "ename"]]
    employees = non_man.to_dict("records")
    domains = list(project_df["pdomain"].dropna().unique())
    courses_df = get_courses()
    courses = courses_df[["cid", "skill"]].to_dict("records")

    if request.method == "POST":
        project_df = get_project_df()
        pid = project_df["pid"].max() + 1
        pname = request.form.get("pname")
        pdesc = request.form.get("pdesc")
        pdomain = request.form.get("pdomain")
        needed = int(request.form.get("needed"))
        manager = request.form.get("manager")
        present = int(request.form.get("present"))
        manager_id = emp_df.loc[emp_df["ename"] == manager, "eid"].values[0]
        skills = request.form.getlist("skills[]")
        skill_ids = courses_df.loc[courses_df["skill"].isin(skills), "cid"]
        add_project(pid, pdomain, pdesc, pname, needed, present, skill_ids, manager_id)
        flash(f" Accepted succesfully")
        return redirect("/add_new_project")

    return render_template(
        "add new projects.html", employees=employees, domains=domains, courses=courses
    )


@app.route("/new_course", methods=["GET", "POST"])
def new_course():
    flash("")
    if request.method == "POST":
        courses_df = get_courses()
        cid = courses_df["cid"].max() + 1
        skill = request.form.get("skill")
        duration = int(request.form.get("duration"))
        cname = request.form.get("cname")
        clink = request.form.get("clink")
        add_course(cid, skill, duration, cname, clink)
        flash("Course added sucessfully")
        return redirect("/new_course")
    return render_template("add new couses.html")


@app.route("/request_page", methods=["GET", "POST"])
def request_page():
    flash("")
    request_df = get_request_df(get_emp_df(), get_project_df())
    requests = request_df.loc[
        request_df["status"] == "Pending",
        ["pname", "ename", "project_skills", "emp_skills"],
    ].to_dict("records")
    projects = list(request_df.loc[
        request_df["status"] == "Pending",
        "pname"].unique())
    return render_template("request.html", requests=requests,projects = projects)


@app.route("/emp_accept", methods=["GET", "POST"])
def emp_accept():
    if request.method == "POST":
        request_df = get_request_df(get_emp_df(), get_project_df())

        ename = request.form.get("ename")
        pname = request.form.get("pname")

        pid = request_df.loc[(request_df["pname"] == pname), "pid"].values[0]
        eid = request_df.loc[(request_df["ename"] == ename), "eid"].values[0]
        accept_emp(pid, eid)
        flash("Accepted for interview")
        return redirect("/request_page")


@app.route("/emp_reject", methods=["GET", "POST"])
def emp_reject():
    if request.method == "POST":
        request_df = get_request_df(get_emp_df(), get_project_df())
        ename = request.form.get("ename")
        pname = request.form.get("pname")
        pid = request_df.loc[(request_df["pname"] == pname), "pid"].values[0]
        eid = request_df.loc[(request_df["ename"] == ename), "eid"].values[0]
        accept_emp(pid, eid)
        flash("Rejected for interview")
        return redirect("/request_page")


@app.route("/ongoing_projects")
def ongoing_projects():
    project_df = get_project_df()
    projects = project_df.to_dict("records")
    domains = project_df["pdomain"].unique().tolist()
    return render_template("ongoing projects.html", projects=projects, domains=domains)


@app.route("/available_projects", methods=["GET", "POST"])
def available_projects():
    project_df = get_project_df()
    projects = project_df.loc[
        (project_df["present"] < project_df["needed"])
        & (project_df["pid"] != session["pid"])
    ].to_dict("records")
    domains = project_df["pdomain"].unique().tolist()
    skills = project_df["skills"].explode().unique().tolist()
    if request.method == "POST":
        request_df = get_request_df(emp_df, project_df)
        project_id = request.form.get("project_id")
        eid = session["eid"]
        pid = int(project_id)
        counter = (
            request_df.loc[
                (request_df["eid"] == eid) & (request_df["pid"] == pid)
            ].shape[0]
            != 0
        )
        if counter:
            flash("You have already applied")
        else:
            request_df = req_transfer(pid, eid)
            flash("Applied Successfully!!")
    return render_template(
        "available projects.html", projects=projects, domains=domains, skills=skills
    )


@app.route("/courses")
def courses():
    courses_df = get_courses()
    user_data = emp_df.loc[emp_df["eid"] == session["eid"]].iloc[0]
    # Convert skills list to string
    user_skills = ", ".join(session["skills"])
    # pass courses for displaying
    courses = courses_df.loc[~courses_df["skill"].isin(session["skills"])].to_dict(
        "records"
    )

    return render_template(
        "courses.html",
        user_name=user_data["ename"],
        user_project=user_data["pname"],
        skills=courses_df.loc[~courses_df["skill"].isin(session["skills"])]["skill"],
        user_skills=user_skills,
        user_dept=user_data["dept"],
        courses=courses,
    )


@app.route("/add_skill", methods=["GET", "POST"])
def add_skill():
    if request.method == "POST":
        courses_df = get_courses()
        course_id = int(request.form.get("cid"))
        eid = session["eid"]
        add_skill_emp(eid, course_id)
        skill = request.form.get("skill")
        session["skills"].append(skill)
        flash(f"Congratulations, {skill} added!")
    return redirect("/courses")
