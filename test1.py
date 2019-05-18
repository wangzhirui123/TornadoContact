#encoding:utf-8
from tornado import web
from tornado import ioloop
import MySQLdb
import torndb
import os
'''
tornado 基本基本使用
'''

def get_conn():
    return MySQLdb.connect('localhost','root','','test',charset='utf8')


def get_tconn():
    return torndb.Connection('localhost',database='test',user='root',password='')




class Index(web.RequestHandler):
    '''1、展示首页'''
    def get(self, *args, **kwargs):
        self.set_secure_cookie('uname','zhangsan',expires_days=1)
        data = {
            'name':'zhangsan',
            'age':'20'
        }

        return self.render('index.html',data = data)

class login(web.RequestHandler):
    '''2、登录获取参数'''
    def get(self, *args, **kwargs):
        print self.get_secure_cookie('uname')
        self.render('login.html')

    def post(self, *args, **kwargs):

        uname = self.get_argument('uname')
        pwd = self.get_argument('upwd')

        self.redirect('/login')


class upload(web.RequestHandler):
    '''3、文件上传'''
    def get(self, *args, **kwargs):

        self.render('upload.html')


    def post(self, *args, **kwargs):
        '''上传图片，并将图片展示出来'''
        import os
        file = self.request.files['file'][0]
        with open(os.path.join(os.getcwd(),'files/{}'.format(file.get('filename'))),'wb')as f:
            f.write(file.get('body',''))
        self.set_header('Content-Type',file.get('content_type',''))
        self.write(file.get('body',''))


class judge_accsess(web.RequestHandler):
    '''4、判断是否正常访问+限制访问次数'''
    usa = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36']
    ipcount = {}
    def get(self, *args, **kwargs):
        ua = self.request.headers['User-Agent']
        ip = self.request.remote_ip
        num = self.ipcount.get(ip,0)+1
        self.ipcount[ip] = num
        print num,ip
        print self.request.headers
        if ua in self.usa and num <3:
            self.write('正常访问')
        else:
            self.send_error(403)


class register(web.RequestHandler):
    '''注册功能'''
    #
    def initialize(self,conn):
        self.conn = conn

    def get(self, *args, **kwargs):

        self.render('register.html')


    def post(self, *args, **kwargs):

        uname = self.get_argument('uname')
        pwd = self.get_argument('pwd')
        try:
            cursor = self.conn.cursor()
            cursor.execute('insert into reg (uname,pwd)VALUE ("%s","%s")'%(uname,pwd))
            self.conn.commit()
            self.write('注册成功')
        except:
            self.write('注册失败')


class TorndbHandler(web.RequestHandler):
    '''torndb数据库操作'''

    def initialize(self,tconn):
        self.tconn = tconn

    def get(self, *args, **kwargs):
        con = self.tconn.get('select * from reg')
        print con

        info = self.tconn.query('select * from reg')

        print info

        self.tconn.execute('update reg set pwd = "123123" where uname = "zhangsan"')

settings = {
    'template_path':'templates',
    'xsrf':True,
    'cookie_secret':'!@#',
    'static_path':os.path.join(os.getcwd(),'static')

}

app = web.Application(
    [(r'/',Index),
    (r'/login',login),
    (r'/upload',upload),
    (r'/judge',judge_accsess),
    (r'/register',register),
    (r'/torndb',TorndbHandler,{'tconn':get_tconn()}),
     ],**settings)

app.listen(80)
ioloop.IOLoop.instance().start()




