class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html", error=None)

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if self.check_credentials(username, password):
            self.set_secure_cookie("user", username)
            next_url = self.get_argument("next", "/")
            self.redirect(next_url)
        else:
            self.render("login.html", error="Credenziali non valide")