from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as up
import github3 as gh
import os
import os.path

# HTTPRequestHandler class
class S(BaseHTTPRequestHandler):
    FORM_LOAD_ERROR = 'Sorry, but theserver can\'t load UI form.'
 
    def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        # Write content as utf-8 data
        try:
            content = open('user_credentials_form.html', 'r').read()
            self.wfile.write(bytes(content, 'utf8'))
        except:
            self.wfile.write(bytes(self.FORM_LOAD_ERROR, 'utf8'))
        return

    def do_POST(self):
        # Get user credentials from submitted form
        if self.headers['content-type'] == 'application/x-www-form-urlencoded':
            creds = up.parse_qs(self.rfile.read(int(self.headers['content-length'])).decode('utf-8'))

        # Convert values from lists to strings by getting first parsed element
        creds = { k: v[0] for k, v in creds.items() }

        # GitHub functionality
        try:
            gh_entity = gh.login(username=creds['username'], password=creds['password'])

            # Check for repository existance
            repos = gh_entity.repositories()
            r_exists = False
            for r in repos:
                if r.name == creds['appname']:
                    r_exists = True
                    break

            # Create repository and upload files into it
            if not r_exists:
                repo = gh_entity.create_repository(creds['appname'])
                if repo:
                    [repo.create_file(f, 'replica', bytes(open(f, 'r').read(), 'utf8')) for f in os.listdir() if os.path.isfile(f)]
                    msg = ('Repository has been created and files have been uploaded into it.', 'success')
                else:
                    msg = ('Can\'t create repository in your account.', 'danger')
            else:
                msg = ('You already have repository with such application name. Please change the name.', 'warning')

        # add github login exception, file open exception, github file creation exception
        except gh.exceptions.AuthenticationFailed:
            msg = ('Can\'t sign in into GitHub with provided credentials.', 'danger')
        except:
            msg = ('Sorry, but something unexpected happened.', 'danger')

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        # Write content as utf-8 data
        try:
            content = open('report_page.html', 'r').read()
            content = content.replace('{{ msg_type }}', msg[1]).replace('{{ msg }}', msg[0])
            self.wfile.write(bytes(content, 'utf8'))
        except:
            self.wfile.write(bytes(self.FORM_LOAD_ERROR, 'utf8'))
        return
 
def run(port=8080):
  print('Starting server...')
 
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('', port)
  httpd = HTTPServer(server_address, S)
  print('Running server...')
  httpd.serve_forever()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()