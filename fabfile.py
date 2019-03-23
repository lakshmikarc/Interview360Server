from fabric.api import local, cd, run, sudo, env, put, prefix
from fabric.contrib.files import exists

env.use_ssh_config = True
env.user = 'ec2-user'
env.hosts = ['ec2-user@18.218.218.124']
env.home_dir = '/home/ec2-user'

PROJECT_NAME = 'interview360'
PG_HBA_PATH = '/var/lib/pgsql/data/'
SELINUX_PATH = '/etc/sysconfig'
GUNICORN_SERVICE_PATH = '/etc/systemd/system/'
NGINX_CONFIG_PATH = '/etc/nginx/'
PROJECT_PATH = "{}/{}".format(env.home_dir, PROJECT_NAME)
GITHUB_PROJECT = 'https://github.com/vforvad/InterviewManager.git'
PROJECT_NGINX_CONF_NAME = 'interview_360.conf'


def set_up():
    """Set up all dependencies."""

    with cd(env.home_dir):
        put('setup.sh', '{}'.format(env.home_dir))
        run('bash setup.sh')


def replace_hba_conf():
    """Replace ph_hba.conf file on server with the current one."""

    with cd(PG_HBA_PATH):
        put('./deploy/pg_hba.conf', PG_HBA_PATH)
        sudo('systemctl restart postgresql')
        sudo('systemctl enable postgresql')


def set_virtualenvwrapper():
    """Set up virtual env wrapper."""

    with cd(env.home_dir):
        run('pyenv virtualenvwrapper')
        with prefix('source $(pyenv which virtualenvwrapper.sh)'):
            run('mkvirtualenv {}'.format(PROJECT_NAME))


def disable_selinux():
    """Disable selinux and firewalld."""

    with cd(env.home_dir):
        sudo('setenforce 0')
        sudo('firewall-cmd --zone=public --add-port=80/tcp --permanent')
        sudo('systemctl restart firewalld')


def clone_project():
    """Clone project from the GitHub."""

    with cd(env.home_dir):
        run("git clone {} {}".format(GITHUB_PROJECT, PROJECT_NAME))


def set_up_project_dependencies():
    """Set up all project dependencies."""

    run('pyenv virtualenvwrapper')
    with prefix('source $(pyenv which virtualenvwrapper.sh)'):
        with prefix('workon {}'.format(PROJECT_NAME)):
            with cd(PROJECT_PATH):
                run('pip install -r requirements/production.txt')

                with cd(PROJECT_PATH + '/app'):
                    run('./manage.py migrate')
                    run('./manage.py collectstatic')


def set_secrets_file():
    """Put file with secrets to app folder."""

    with cd(PROJECT_PATH + '/app/app'):
        put('./deploy/secrets.yaml', PROJECT_PATH + '/app/app')


def configure_gunicorn_service():
    """Configure gunicorn service."""

    with cd(GUNICORN_SERVICE_PATH):
        put('./deploy/gunicorn.service', GUNICORN_SERVICE_PATH)
        sudo('systemctl start gunicorn')
        sudo('systemctl enable gunicorn')


def configure_nginx_service():
    """Configure the nginx service."""

    with cd(NGINX_CONFIG_PATH):
        command = """
        ln -nfs {}/deploy/{} /etc/nginx/sites-enabled/interview_360.conf
        """.format(PROJECT_PATH, PROJECT_NGINX_CONF_NAME)
        put('./deploy/nginx.conf', NGINX_CONFIG_PATH)
        sudo('usermod -a -G {} nginx'.format(env.user))
        sudo('chmod 710 {}'.format(env.home_dir))
        sudo(command)
        sudo('systemctl start nginx')
        sudo('systemctl enable nginx')


def provision():
    """Implement provisioning of the new server."""

    set_up()
    replace_hba_conf()
    set_virtualenvwrapper()
    disable_selinux()
    clone_project()
    set_up_project_dependencies()
    configure_gunicorn_service()
    configure_nginx_service()


def docker_install():
    """Install docker."""

    run('wget -qO- https://get.docker.com/ | sh')
    sudo('usermod -aG docker $(whoami)')
    sudo('systemctl enable docker.service')
    sudo('systemctl start docker.service')


def docker_redhat_install():
    """Install docker for the RedHat 7."""

    sudo('yum update -y')
    sudo('yum install -y docker')
    sudo('usermod -aG docker $(whoami)')
    sudo('service docker start')


def docker_compose_install():
    """Install docker-compose."""

    sudo('yum install epel-release')
    sudo('yum install -y python-pip')
    sudo('pip install docker-compose')


def docker_files_copy():
    """Copy necessary files on remote server."""

    file_path = '{}/docker-compose.yml'.format(env.home_dir)
    put('docker-compose.prod.yml', file_path)
    run('mkdir -p {}/deploy/nginx'.format(env.home_dir))
    put('./deploy/nginx/dev.conf',
        '{}/deploy/nginx/developmet.conf'.format(env.home_dir))
    put('.env.prod', '{}/.env'.format(env.home_dir))


def docker_provision():
    """Run provision on remote server for docker."""

    with cd(env.home_dir):
        docker_install()
        docker_compose_install()
        docker_files_copy()


def docker_provision_aws():
    """Run provision on remote AWS server for the docker."""

    with cd(env.home_dir):
        docker_redhat_install()
        docker_compose_install()
        docker_files_copy()


def docker_deploy(version='latest', container='app'):
    """Deploy docker application."""

    compose_command = (
        "docker-compose build --force-rm --no-cache --build-arg "
        "DEFAULT_REQUIREMENTS=production.txt app"
    )

    local(compose_command)
    local('docker-compose push app')

    with cd(env.home_dir):
        run('docker-compose pull')
        run('docker-compose stop')
        run('docker-compose up -d')


def deploy(branch='master'):
    """Deploy project."""

    with cd(PROJECT_PATH):
        run('git checkout {} && git pull origin {}'.format(branch, branch))

        with prefix('source $(pyenv which virtualenvwrapper.sh)'):
            with prefix('workon {}'.format(PROJECT_NAME)):
                run('pip install -r requirements/production.txt')

                with cd(PROJECT_PATH + '/app'):
                    run('./manage.py migrate')
        sudo('systemctl restart gunicorn')
