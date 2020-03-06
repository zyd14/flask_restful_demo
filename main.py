import os

if __name__ == '__main__':
    from src.app import api
    if os.getenv('DOCKER_EXE'):
        api.app.run(host='0.0.0.0')
    else:
        api.app.run(host='127.0.0.1')
