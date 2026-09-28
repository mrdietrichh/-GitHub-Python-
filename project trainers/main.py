from database import init_db
from app import App


def main():
    init_db()
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
