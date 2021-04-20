from station_backend.app import app, settings


if __name__ == '__main__':
    app.run(host=settings.host, port=settings.port, threaded=True)
