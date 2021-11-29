
import getpass
import os
import glob
from fabric import task

CLONE_URL = 'git@github.com:MarkVergunst/robot.git'

# dont forget for proxy pass apt-get install apache2 libapache2-mod-proxy-uwsgi
# a2enmod headers deflate expires rewrite proxy proxy_uwsgi ssl
# ssh root@85.214.27.56 -p234

MYSQL_CREATE_SCRIPT = """
CREATE DATABASE %(db_name)s;
CREATE USER '%(db_user)s'@'localhost' IDENTIFIED BY '%(db_pwd)s';
GRANT ALL PRIVILEGES ON %(db_name)s . * TO '%(db_user)s'@'localhost';
FLUSH PRIVILEGES;
"""

'''

fab -H root@butterbot.hqweb.nl prd create-app-user install-native get-latest-sourcecode prepare-postgresql prepare-virtualenv django-preparations process-configfiles prepare-webserverconfig prepare-supervisor-config

one of [dev|tst|acc|prd] MUST be first target called! 

example call:
fab -H root@prd.materialstestingveendam.nl prd create-app-user install-native get-latest-sourcecode prepare-postgresql prepare-virtualenv django-preparations process-configfiles prepare-webserverconfig prepare-supervisor-config
fab -H root@prd.materialstestingveendam.nl prd prepare-supervisor-config
Alleen even django sources releasen naar prd:
fab -H root@prd.materialstestingveendam.nl prd get-latest-sourcecode prepare-supervisor-config

deploy met mogelijk config aanpassingen naar tst:
fab -H root@85.214.27.56 tst get-latest-sourcecode prepare-virtualenv django-preparations process-configfiles prepare-webserverconfig prepare-supervisor-config


database backup maken:
mysqldump -u timmerplanner_prd -ppl4n3rpl4n TIMMERPLANNER_PRD > TIMMERPLANNER_PRD_20190521.sql

'''

def general_config(ctx):

    sudo_pass = getpass.getpass("What's your sudo password on %s? " % ctx.host)
    ctx.update({
        'sudo': {'password': sudo_pass}})
    ctx.update({
        'target_user': "mtveendam_%s" % ctx['target']
    })
    ctx.update({
        'db_name': 'butterpasser_%s' % ctx['target'].upper(),
        'db_pwd': 'Nf10S09uxn',
        'db_user': 'butterpasser_%s' % ctx['target'],
        'target_user_home': "/home/%s" % ctx['target_user'],
        'remote_conf_dir': "/home/%s/_BUTTER_PASSER/project/config" % ctx['target_user'],
        'requirementsfile': '/home/%s/_BUTTER_PASSER/requirements.txt' % ctx['target_user'],
        'settings_init_file': "~%s/mtveendam/mtveendam/settings/__init__.py" % ctx['target_user']
    })
    ctx.update({
        # deze twee zijn lokaal!!!!
        'conf_templates_dir': '%s/project/deployment/templates' % os.path.dirname(__file__),
        'conf_target_dir': '%s/project/config' % os.path.dirname(__file__),

        'mysql_db_create_script': MYSQL_CREATE_SCRIPT % ctx,

        'webserver_file': '%s/%s-ssl-apache.conf' % (ctx['remote_conf_dir'], ctx['target_user']),
        'webserver_conf_dir': '/etc/apache2/sites-enabled/',
        'webserver_reload_cmd': "/etc/init.d/apache2 reload",

        'supervisor_conf_dir': '/etc/supervisor/conf.d/',
        'supervisor_file': '%s/%s-supervisor.conf' % (ctx['remote_conf_dir'], ctx['target_user']),

        'supervisor_reload_cmd': '/etc/init.d/supervisor reload',

        'app_base_dir': '%s/_BUTTER_PASSER' % (ctx['target_user_home']),

        'appserver_ini_file': '%s/%s-uwsgi.ini' % (
            ctx['remote_conf_dir'], ctx['target_user']
        ),

        'create_dirs': [
            'var/log',
            'var/data/media',
            'var/data/uploads',
            'var/data/email-messages',
            'var/run',
        ],
        'native_packages': [
            "build-essential", "python3-dev", "python3-virtualenv",
            "libjpeg8-dev", "zlib1g-dev", "libfreetype6-dev",
            "python-psycopg2",
            # "libwebp-dev", "supervisor", "liblcms2-dev",
            "libffi-dev", "libssl-dev", "libxml2-dev", "libxslt1-dev", "git",
            "supervisor"
        ]
    })

    ctx.update({
        'appserver_supervisor_cmd': '%s/venv/bin/uwsgi --ini %s' % (
            ctx['target_user_home'], ctx['appserver_ini_file']
        ),
    })


@task
def process_configfiles(ctx):
    ''' 8. make gunicorn, nginx and supervisor files and push to server'''

    from string import Template

    for conffile in glob.glob('%s/*.tmpl' % ctx['conf_templates_dir']):

        # print(conffile)
        # template file lezen
        src = Template(open(conffile, 'r').read())
        # door de template-renderer halen met de context van hierboven
        rendered = src.substitute(ctx)
        # print(rendered)
        # alleen tmpl-filenaam, pad eraf gesloopt, bijv. gunicorn.ini.py.tmpl
        src_filename = conffile.split('/')[-1]

        # nieuw naam met .tmpl eraf, bijv: photobooth_prd-gunicorn.ini.py
        tgt_filename = '%s-%s' % (ctx['target_user'],
                                  src_filename.replace('.tmpl', ''))
        tgt_filepath = '%s/%s' % (ctx['conf_target_dir'], tgt_filename)
        print(tgt_filepath)
        with open(tgt_filepath, 'w') as tgtfile:
            tgtfile.write(rendered)

        ctx.put(tgt_filepath, "/tmp/%s" % tgt_filename)
        ctx.sudo("cp /tmp/%s %s" % (tgt_filename, ctx['remote_conf_dir']))
        ctx.sudo("chown %(target_user)s.%(target_user)s %(remote_conf_dir)s/%(tgt_filename)s" % {
            'target_user': ctx['target_user'],
            'remote_conf_dir': ctx['remote_conf_dir'],
            'tgt_filename': tgt_filename
        })
        ctx.sudo("rm /tmp/%s" % tgt_filename)



@task
def acc(ctx):
    ''' 1. Sets the deployment target to "acc"'''
    ctx.update({'target': 'acc'})
    ctx.update({'db_pwd': 'Nf10S0&9uxn$'})
    general_config(ctx)

@task
def dev(ctx):
    ''' 1. Sets the deployment target to "dev"'''
    ctx.update({'target': 'dev'})
    general_config(ctx)

@task
def tst(ctx):
    ''' 1. Sets the deployment target to "tst"'''
    ctx.update({'target': 'tst'})
    ctx.update({'db_pwd': 'Nf10S0&9uxn$'})
    general_config(ctx)

@task
def prd(ctx):
    ''' 1. Sets the deployment target to "prd"'''
    ctx.update({'target': 'prd'})
    ctx.update({'db_pwd': 'Nf10S09uxn'})
    general_config(ctx)

# user aanmaken
@task
def create_app_user(ctx):
    ''' 2. Checks if unix-user that will run the app exists (created if not)'''

    result = ctx.run("getent passwd %s | cut -d: -f6" % ctx['target_user'])

    if not result or not result.stdout:
        print("User '%s' does not exist. Creating it." % ctx['target_user'])
        ctx.sudo("useradd -s /bin/bash -m -U %s" % ctx['target_user'])
        ctx.sudo("-i mkdir .ssh",
                 user=ctx['target_user'], hide=True)
        #
        #
        #  TODO TODO TODO
        #
        #
        # ctx.sudo("-i echo '%s' > .ssh/id_rsa" % GITGUEST_PRIVATE_KEY,
        #          user=ctx['target_user'], hide=False)
        ctx.sudo("-i chmod -R go-rwx .ssh",
                 user=ctx['target_user'], hide=True)


# install_native
@task
def install_native(ctx, *args, **kwargs):
    ''' 3. installs required native packages with apt-get'''
    ctx.sudo('apt-get -y install %s' % " ".join(
        ctx['native_packages']
    ))
    print("install_native done")


@task
def prepare_virtualenv(ctx):
    ''' 6. creates or update the virtualenv '''
    print("checking or creating virtualenv")
    venv_full_path = '%s/venv' % ctx['target_user_home']

    if ctx.sudo('-i test -d %s' % venv_full_path, warn=True,
                user=ctx['target_user']).failed:
        print("venv not found. Creating virtualenv")
        result = ctx.sudo("-i virtualenv -p python3 %s" % venv_full_path,
                          user=ctx['target_user'])
        print("creating virtualenv done: %s" % result.stdout)

    # --no-cache-dir voorkomt probleem met cache-dir in home van verkeerde user
    result = ctx.sudo(
        "-i bash -c \"source ./venv/bin/activate; %(venvdir)s/bin/pip "
        "--no-cache-dir install -r %(requirementsfile)s\"" % {
            'venvdir': venv_full_path,
            'requirementsfile': ctx['requirementsfile']
        },
        user=ctx['target_user']
    )
    print("Virtualenv updated: %s" % result.stdout)


# mysql configureren
@task
def prepare_mysql(ctx):
    ''' 5. install mysql dependencies and makes DB user + schema'''
    # VOOR MYSQL
    print("Installing or updating apt-packages for mysql")
    ctx.sudo("apt-get -y install mysql-client libmysqlclient-dev")

    mysql_root_pass = getpass.getpass(
        "What's the MYSQL root password on %s? " % ctx.host)

    check_mysql_cmd = "echo \"select 1 from db where Db='%s'\"| mysql -uroot -p%s mysql" % \
    (ctx['db_name'], mysql_root_pass)
    result = ctx.sudo(
        check_mysql_cmd,
        user=ctx['target_user'],
        warn=True,
    )
    print(result)
    if result.stdout == '':
        # make the database and user
        create_database_cmd = "echo \"%s\" | mysql -uroot -p%s mysql" % (
            ctx['mysql_db_create_script'], mysql_root_pass)
        result = ctx.sudo(
            create_database_cmd,
            user=ctx['target_user'],
            warn=True,
        )
        print("mysql_db_create_script: %s" % result.stdout)
    else:
        print("database %s already exists." % ctx['db_name'])

    print("mysql + schema install done")


# postgresql configureren
@task
def prepare_postgresql(ctx):
    ''' 5. install postgresql dependencies and makes DB user + schema '''
    # VOOR POSTGRESQL:
    print("Installing or updating apt-packages for postgresql")
    ctx.sudo(
        "apt-get -y install postgresql libpq-dev postgresql-client "
        "postgresql-client-common"
    )
    # test of database schema en user er zijn, anders maken
    try:
        result = ctx.sudo(
            "-u postgres createuser %(db_user)s" % ctx,
            warn=False
        )
        print('psql create user: %s' % result.stdout)
    except Exception as exc:
        print("database-user %s already exists" % ctx['db_user'])

    try:
        result = ctx.sudo(
            "-u postgres createdb \"%(db_name)s\"" % ctx,
            warn=False
        )
        print('psql create db: %s' % result.stdout)
    except Exception as exc:
        print("database %s already exists" % ctx['db_name'])

    result = ctx.sudo(
        "-u postgres psql -c \" alter user %(db_user)s with "
        "encrypted password '%(db_pwd)s'\"" % ctx,
        warn=False
    )
    print('psql create password: %s' % result.stdout)
    result = ctx.sudo(
        "-u postgres psql -c 'grant all privileges on "
        "database \"%(db_name)s\" to %(db_user)s'" % ctx,
        warn=False
    )
    print('psql grant privileges: %s' % result.stdout)
    print("postgresql done")


# broncode clonen
@task
def get_latest_sourcecode(ctx, *args, **kwargs):
    ''' 4. fetch application sourcecode from git'''
    print("Making dirs in %s's homedir" % ctx['target_user'])
    ctx.sudo(
        "-i mkdir -p %s" % " ".join(ctx['create_dirs']),
        user=ctx['target_user']
    )
    print("Making dirs done")

    print("get_sourcecode:")
    echo_line = 'echo "from .%s import *" > %s' % (ctx['target'], ctx['settings_init_file'])
    ctx.sudo(
        "-i bash -c '%s'" % echo_line,
        user=ctx['target_user'],
        hide=False)

    if ctx.sudo('-i test -d %s' % ctx['app_base_dir'], warn=True, user=ctx['target_user']).failed:
        # git clone
        ctx.sudo(
            '-i git clone %(clone_url)s' % {
                'base_dir': ctx['app_base_dir'], 'clone_url': CLONE_URL
            },
            user=ctx['target_user'], hide=False
        )
    else:
        print("%s already exists" % ctx['app_base_dir'])
        # git pull
        ctx.sudo(
            '-i bash -c "cd %s ; git pull"' % ctx['app_base_dir'],
            user=ctx['target_user'], hide=False
        )


@task
def django_preparations(ctx):
    ''' 7. Runs django migrate and django collectstatic --noin'''

    result = ctx.sudo(
        "-i bash -c \"cd %s ; source ../venv/bin/activate ; ./manage.py migrate\" " % ctx['app_base_dir'],
        user=ctx['target_user']
    )
    print("django migrate: %s" % result.stdout)
    result = ctx.sudo(
        "-i bash -c \"cd %s ; source ../venv/bin/activate ; ./manage.py collectstatic --noin\" " % ctx['app_base_dir'],
        user=ctx['target_user']
    )
    print("django collectstatic: %s" % result.stdout)


@task
def prepare_webserverconfig(ctx):
    ''' 9. enable webserver config for this app and (re)start webserver'''
    print("linking webserver config")

    # connect config files
    ctx.sudo(
        "ln -sf %(webserver_file)s %(webserver_conf_dir)s" % ctx
    )

    ctx.sudo(
        ctx['webserver_reload_cmd']
    )

    print("webserver config updated and reloaded")


@task
def prepare_supervisor_config(ctx, *args, **kwargs):
    ''' 10. enable supervisor config for this app and reload supervisor'''
    print("linking supervisor config")

    # connect config files
    ctx.sudo(
        "ln -sf %(supervisor_file)s %(supervisor_conf_dir)s" % ctx
    )

    ctx.sudo(
        ctx['supervisor_reload_cmd']
    )

    print("supervisor config updated and reloaded")


@task
def test_fab(ctx, *args, **kwargs):
    ''' ZZZ. testjes om toegang naar server via fabric te testen '''

    ctx.sudo('-i whoami', user=ctx['target_user'], hide=False)
    # print("get_sourcecode.whoami: %s" % result)

    ctx.sudo('-i pwd', user=ctx['target_user'], hide=False)
    # print(result)