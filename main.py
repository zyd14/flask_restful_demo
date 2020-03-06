from argparse import ArgumentParser

if __name__ == '__main__':
    from src.app import api
    api.app.run(host='127.0.0.1')