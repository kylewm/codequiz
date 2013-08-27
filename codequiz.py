import os, string, random, re, datetime
from textwrap import dedent

from flask import Flask, request, session, redirect, render_template, flash,\
  url_for, _app_ctx_stack, abort, Markup

from flaskext.markdown import Markdown
from flask.ext.sqlalchemy import SQLAlchemy

from postmark import PMMail

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['DEBUG'] = os.environ.get('DATABASE_URL')
app.config['USERNAME'] = os.environ.get('USERNAME')
app.config['PASSWORD'] = os.environ.get('PASSWORD')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['POSTMARK_API_KEY'] = os.environ.get('POSTMARK_API_KEY')
app.config['POSTMARK_SENDER'] = os.environ.get('POSTMARK_SENDER')

markdown = Markdown(app)

db = SQLAlchemy(app)



candidate_problems = db.Table('candidate_problems', db.Model.metadata,
                              db.Column('candidate_id', db.Integer, db.ForeignKey('candidates.id')),
                              db.Column('problem_id', db.Integer, db.ForeignKey('problems.id')))
    
class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, db.Sequence('candidate_id_seq'), primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    notify_emails = db.Column(db.String)
    start_time = db.Column(db.DateTime)
    url_hash = db.Column(db.String)
    problems = db.relationship('Problem', secondary=candidate_problems, backref='candidates')


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, db.Sequence('problem_id_seq'), primary_key=True)
    name = db.Column(db.String)
    content = db.Column(db.Text)


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, db.Sequence('submission_id_seq'), primary_key=True)
    time = db.Column(db.DateTime)
    content = db.Column(db.Text)

    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'))
    candidate = db.relationship('Candidate', backref=db.backref('submissions', order_by=id))
    problem_id  = db.Column(db.Integer, db.ForeignKey('problems.id'))
    problem = db.relationship('Problem')


def init_db():
    db.create_all()



@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    problems = Problem.query.order_by(Problem.name)
    candidates = Candidate.query.order_by(Candidate.name)
    return render_template("admin.html", problems=problems, candidates=candidates)


@app.route('/admin/problem/new', defaults={'problem_id': 'new'}, methods=['GET', 'POST'])
@app.route('/admin/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem_view(problem_id):
    action = request.args.get('action', 'view')

    problem = None
    if problem_id == 'new':
        problem = Problem(name='Unnamed', content='')
    else:
        problem = Problem.query.\
            filter(Problem.id == problem_id).\
            one()

    if action == 'view':
        return render_template("problem.html", problem=problem)
    
    elif action == 'edit':
        if request.method == 'POST':
            problem.name = request.form['name']
            problem.content = request.form['content']
            if not problem.id:
                db.session.add(problem)
            db.session.commit()
            return redirect(url_for('problem_view', problem_id=problem.id, action='view'))
        else:
            return render_template('problem_edit.html', problem=problem)
        
    elif action == 'delete':
        if problem.id:
            db.session.delete(problem)
            db.session.commit()
            flash('Deleted problem {}'.format(problem.name))
            return redirect(url_for('admin'))
    
    return abort(404)



@app.route('/admin/candidate/new', defaults={'candidate_id': 'new'}, methods=['GET', 'POST'])
@app.route('/admin/candidate/<int:candidate_id>', methods=['GET', 'POST'])
def candidate_view(candidate_id):
    candidate = None

    action = request.args.get('action', 'view')

    if candidate_id == 'new':
        url_hash = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])
        candidate = Candidate(name='Unnamed', url_hash=url_hash)
    else:
        candidate = Candidate.query.\
            filter(Candidate.id == candidate_id).\
            one()

    if action == 'view':
        return render_template('candidate.html', candidate=candidate)

    elif action == 'edit':
        if request.method == 'POST':
            candidate.name = request.form['name']
            candidate.email = request.form['email']
            candidate.notify_emails = request.form['notify_emails']
            candidate.problems = []
            problem_ids = request.form.getlist('problem')
            for problem_id in problem_ids:
                selected_problem = Problem.query.\
                    filter(Problem.id == problem_id).\
                    one()
                candidate.problems.append(selected_problem)
            if not candidate.id:
                db.session.add(candidate)
            db.session.commit()
            return redirect(url_for('candidate_view', candidate_id=candidate.id, action='view'))

        else:
            all_problems = Problem.query.order_by(Problem.name)
            return render_template('candidate_edit.html', candidate=candidate, all_problems=all_problems)

    elif action == 'delete':
        if candidate.id:
            db.session.delete(candidate)
            db.session.commit()
            flash('Deleted candidate {}'.format(candidate.name))
            return redirect(url_for('admin'))



@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)


@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


@app.route('/quiz_submit', methods=['POST'])
def quiz_submit():
    candidate_id = request.form['candidate']
    problem_id = request.form['problem']

    candidate = Candidate.query.\
        filter(Candidate.id == candidate_id).\
        one()

    problem = Problem.query.\
        filter(Problem.id == problem_id).\
        one()
    
    content = request.form['content']
    if content:
        sub = Submission(candidate_id=candidate.id, problem_id=problem_id,
                         content=content, time=datetime.datetime.utcnow())
        db.session.add(sub)
        db.session.commit()

        # notify via email
        text_template = dedent("""Submission from: {}
                               Problem: {}
                               At: {}
                               --------------------------------------------------------------------------------
                               {}""")
        html_template = dedent("""<html>
                               Submission from <b>{}</b><br>
                               Problem: <b>{}</b><br>
                               At: <b>{}</b>
                               <hr>
                               <pre>{}</pre>
                               </html>""") 
        time_str = format_timestamp(sub.time)
        send_email(candidate, "Submission from {}, {}".format(candidate.name, problem.name),
                   text_template.format(candidate.name, problem.name,
                                        time_str, sub.content),
                   html_template.format(candidate.name, problem.name,
                                        time_str, sub.content))

        flash("Submitted solution for {}".format(problem.name))

        return redirect(url_for('quiz_view', url_hash=candidate.url_hash))


@app.route('/quiz/<string:url_hash>', methods=['GET', 'POST'])
def quiz_view(url_hash):
    candidate = db.session.query(Candidate).\
        filter(Candidate.url_hash == url_hash).\
        one()
    
    action = request.args.get('action')
    if not candidate.start_time and action == 'start':
        candidate.start_time = datetime.datetime.utcnow()
        db.session.commit()

        text_template = dedent("""Quiz started: {}
                               At: {}""")

        html_template = dedent("""<html>
                               Quiz started by: <b>{}</b><br>
                               At: <b>{}</b>
                               </html>""")

        time_str = format_timestamp(candidate.start_time)

        send_email(candidate, "Quiz started {} at {}".format(candidate.name, time_str),
                   text_template.format(candidate.name, time_str),
                   html_template.format(candidate.name, time_str))

        return redirect(url_for('quiz_view', url_hash=url_hash))
        

    if candidate.start_time:        
        return render_template('quiz.html', candidate=candidate)
    else:
        return render_template('quiz_intro.html', candidate=candidate)


def format_timestamp(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%S Z")


@app.template_filter('moment')    
def moment_filter(ts):
    if not ts:
        return ""

    #print 'apply moment filter to: {}'.format(ts)
    ts_str = format_timestamp(ts)
    return Markup(dedent(
        '''<script>
            var mo = moment("{}");
            document.write(mo.format("LLL") + ", " + mo.fromNow());
           </script>'''.format(ts_str)))


def send_email(candidate, subject, text_body, html_body):
    if candidate.notify_emails:
        msg = PMMail(api_key = app.config['POSTMARK_API_KEY'],
                     subject = subject,
                     sender = app.config['POSTMARK_SENDER'],
                     to = candidate.notify_emails,
                     text_body = text_body,
                     html_body = html_body)
        msg.send()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=True)
