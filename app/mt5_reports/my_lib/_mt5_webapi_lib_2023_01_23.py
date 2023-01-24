from urllib import parse


class MT5Session:
    server = "localhost:443"
    manager = "1000"
    password = "password"
    session = None
    connection = False

    def __init__(self, _server, _manager, _password):
        import requests
        import hashlib
        import secrets
        import urllib3
        urllib3.disable_warnings()

        self.server = _server
        self.manager = _manager
        self.password = _password
        self.session = requests.Session()

        url = 'https://' + self.server + '/api/auth/start?version=3091&agent=WebAPI&login=' + self.manager + \
              '&type=manager'
        try:
            result = self.session.get(url, verify=False)
            srv_rand = bytes.fromhex(result.json().get('srv_rand'))
            password = self.password.encode('utf-16le')
            password = hashlib.md5(password).digest()
            password = hashlib.md5(password + b'WebAPI').digest()
            srv_rand = hashlib.md5(password + srv_rand).hexdigest()
            cli_rand = hashlib.md5(secrets.token_hex(16).encode('utf-16le')).hexdigest()

            url = 'https://' + self.server + '/api/auth/answer?srv_rand_answer=' + srv_rand + '&cli_rand=' + cli_rand
            result = self.session.get(url, verify=False)
            self.connection = (result.status_code == 200)

            url = 'https://' + self.server + '/api/test/access'
            result = self.session.get(url, verify=False)
            self.connection = (result.status_code == 200)

            url = 'https://' + self.server + '/api/common/get'
            result = self.session.get(url, verify=False)
            self.common = result.json().get('answer')

            url = 'https://' + self.server + '/api/time/server'
            result = self.session.get(url, verify=False)
            self.servertime = result.json().get('answer')['time']
        except Exception as ex:
            print(ex)
            self.session = None


class MT5Mysql:
    def __init__(self, _host, _port, _user, _password, _db_name, _sql):
        import pymysql
        self.result = ''
        try:
            self.connection = pymysql.connect(host=_host, port=int(_port), user=_user, password=_password,
                                              database=_db_name, cursorclass=pymysql.cursors.DictCursor)
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(_sql)
                    self.result = cursor.fetchall()
            except Exception as _ex:
                print(f"{_ex}\nSQL syntax error!")
            finally:
                self.connection.close()
        except Exception as _ex:
            print(f"{_ex}\nDB connection error!")