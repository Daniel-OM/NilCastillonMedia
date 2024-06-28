
from .app import application
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = DispatcherMiddleware(app=None, mounts={
    '/': application,
})

if __name__ == "__main__":
    app.run(port=5000)
