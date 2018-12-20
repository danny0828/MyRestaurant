"""
 Created by Danny on 2018/11/28
"""
from app.app import app, manager
from flask_script import Server
from app.jobs.launcher import RunJob
__author__ = 'Danny'

# web server
manager.add_command("runserver", Server(host='0.0.0.0', port=app.config['SERVER_PORT'],
                                        use_debugger=True, use_reloader=True))

# job entrance
manager.add_command('runjob', RunJob())


def main():
    # app.run(host='0.0.0.0', debug=True)
    # python manager.py runserver
    # export op_config=local && python manager.py runserver
    manager.run()


if __name__ == '__main__':
    try:
        import sys
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()









