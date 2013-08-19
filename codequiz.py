import os, string, random, re, datetime, textwrap

from flask import Flask, request, session, redirect, render_template, flash,\
  url_for, _app_ctx_stack, abort, Markup
from flaskext.markdown import Markdown

from collections import namedtuple

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey,\
  DateTime, Sequence

app = Flask(__name__)
app.config.from_pyfile('codequiz.cfg')
Markdown(app)

Base = declarative_base()

candidate_problems = Table('candidate_problems', Base.metadata,
                           Column('candidate_id', Integer, ForeignKey('candidates.id')),
                           Column('problem_id', Integer, ForeignKey('problems.id')))

    
class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, Sequence('candidate_id_seq'), primary_key=True)
    name = Column(String)
    email = Column(String)
    start_time = Column(DateTime)
    url_hash = Column(String)
    problems = relationship('Problem', secondary=candidate_problems, backref='candidates')


class Problem(Base):
    __tablename__ = 'problems'

    id = Column(Integer, Sequence('problem_id_seq'), primary_key=True)
    name = Column(String)
    content = Column(Text)


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, Sequence('submission_id_seq'), primary_key=True)
    time = Column(DateTime)
    content = Column(Text)

    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    candidate = relationship('Candidate', backref=backref('submissions', order_by=id))
    problem_id  = Column(Integer, ForeignKey('problems.id'))
    problem = relationship('Problem')



db_url = os.environ["DATABASE_URL"]
db_engine = create_engine(db_url, echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=db_engine))

def init_db():
    Base.metadata.create_all(db_engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    problems = db_session.query(Problem).order_by(Problem.name)
    candidates = db_session.query(Candidate).order_by(Candidate.name)
    return render_template("admin.html", problems=problems, candidates=candidates)


@app.route('/admin/problem/new', defaults={'problem_id': 'new'}, methods=['GET', 'POST'])
@app.route('/admin/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem_view(problem_id):
    action = request.args.get('action', 'view')

    problem = None
    if problem_id == 'new':
        problem = Problem(name='Unnamed', content='')
    else:
        problem = db_session.query(Problem).\
            filter(Problem.id == problem_id).\
            one()

    if action == 'view':
        return render_template("problem.html", problem=problem)
    
    elif action == 'edit':
        if request.method == 'POST':
            problem.name = request.form['name']
            problem.content = request.form['content']
            if not problem.id:
                db_session.add(problem)
            db_session.commit()
            return redirect(url_for('problem_view', problem_id=problem.id, action='view'))
        else:
            return render_template('problem_edit.html', problem=problem)
        
    elif action == 'delete':
        if problem.id:
            db_session.delete(problem)
            db_session.commit()
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
        candidate = db_session.query(Candidate).\
            filter(Candidate.id == candidate_id).\
            one()

    if action == 'view':
        return render_template('candidate.html', candidate=candidate)

    elif action == 'edit':
        if request.method == 'POST':
            candidate.name = request.form['name']
            candidate.email = request.form['email']
            candidate.problems = []
            problem_ids = request.form.getlist('problem')
            for problem_id in problem_ids:
                selected_problem = db_session.query(Problem).\
                    filter(Problem.id == problem_id).\
                    one()
                candidate.problems.append(selected_problem)
            if not candidate.id:
                db_session.add(candidate)
            db_session.commit()
            return redirect(url_for('candidate_view', candidate_id=candidate.id, action='view'))

        else:
            all_problems = db_session.query(Problem).order_by(Problem.name)
            return render_template('candidate_edit.html', candidate=candidate, all_problems=all_problems)

    elif action == 'delete':
        if candidate.id:
            db_session.delete(candidate)
            db_session.commit()
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

    candidate = db_session.query(Candidate).\
        filter(Candidate.id == candidate_id).\
        one()
    
    content = request.form['content']
    if content:
        sub = Submission(candidate_id=candidate.id, problem_id=problem_id,
                         content=content, time=datetime.datetime.utcnow())
        db_session.add(sub)
        db_session.commit()
        return redirect(url_for('quiz_view', url_hash=candidate.url_hash))


@app.route('/quiz/<string:url_hash>', methods=['GET', 'POST'])
def quiz_view(url_hash):
    candidate = db_session.query(Candidate).\
        filter(Candidate.url_hash == url_hash).\
        one()
    
    action = request.args.get('action')
    if not candidate.start_time and action == 'start':
        candidate.start_time = datetime.datetime.utcnow()
        db_session.commit()
        return redirect(url_for('quiz_view', url_hash=url_hash))
        

    if candidate.start_time:        
        return render_template('quiz.html', candidate=candidate)
    else:
        return render_template('quiz_intro.html', candidate=candidate)

@app.template_filter('moment')    
def moment_filter(ts):
    print 'apply moment filter to: {}'.format(ts)
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S Z")
    return Markup(textwrap.dedent(
            '''<script>
                 var mo = moment("{}");
                 document.write(mo.format("LLL") + ", " + mo.fromNow());
               </script>'''.format(ts_str)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=True)
