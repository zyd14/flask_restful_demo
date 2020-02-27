from argparse import ArgumentParser

if __name__ == '__main__':
    from src.setupapp import api
    api.app.run(host='0.0.0.0', debug=True)
